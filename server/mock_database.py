"""Mock database for testing without Lakebase connection."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class MockLakebaseConnection:
    """Mock Lakebase connection for testing."""
    
    def __init__(self):
        """Initialize mock data."""
        # Need to generate inventory first to calculate KPIs properly
        self.inventory = self._generate_mock_inventory()
        self.orders = self._generate_mock_orders()
    
    def _generate_mock_orders(self) -> List[Dict[str, Any]]:
        """Generate mock orders data."""
        orders = []
        products = ["Premium Coffee Beans", "Organic Green Tea", "Sparkling Water", "Energy Drink", "Fresh Orange Juice"]
        stores = ["STORE-001", "STORE-002", "STORE-003", "STORE-004", "STORE-005"]
        statuses = ["pending", "approved", "shipped", "delivered"]
        managers = ["john.manager", "jane.manager", "bob.manager", "alice.manager"]
        
        for i in range(20):
            order_date = datetime.now() - timedelta(days=random.randint(0, 30))
            orders.append({
                "order_id": i + 1,
                "order_number": f"ORD-2024-{1000 + i}",
                "product": random.choice(products),
                "quantity": random.randint(5, 50),
                "store": random.choice(stores),
                "requested_by": random.choice(managers),
                "order_date": order_date.isoformat(),
                "status": random.choice(statuses)
            })
        
        return orders
    
    def _generate_mock_inventory(self) -> List[Dict[str, Any]]:
        """Generate mock inventory forecast data."""
        inventory = []
        products = [
            ("COF-001", "Premium Coffee Beans"),
            ("TEA-001", "Organic Green Tea"),
            ("WAT-001", "Sparkling Water"),
            ("ENG-001", "Energy Drink"),
            ("JUI-001", "Fresh Orange Juice"),
            ("SOD-001", "Cola Soda"),
            ("MIL-001", "Almond Milk"),
            ("CHO-001", "Hot Chocolate Mix"),
        ]
        
        for sku, name in products:
            current_stock = random.randint(0, 200)
            forecast = random.randint(50, 150)
            
            if current_stock == 0:
                status = "out_of_stock"
                action = "Urgent Reorder"
            elif current_stock < 20:
                status = "reorder_needed"
                action = "Reorder Now"
            elif current_stock < 50:
                status = "low_stock"
                action = "Monitor"
            else:
                status = "in_stock"
                action = "No Action"
            
            inventory.append({
                "item_id": sku,
                "item_name": name,
                "stock": current_stock,
                "forecast_30_days": forecast,
                "status": status,
                "action": action
            })
        
        return inventory
    
    def execute_query(self, query: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Mock execute query."""
        # Log the query for debugging
        print(f"Mock DB Query: {query}")
        
        # Parse the query to determine what to return
        if "WHERE o.order_id = %s" in query and params:
            # Query for specific order by ID
            order_id = params[0] if isinstance(params, (list, tuple)) else params
            for order in self.orders:
                if order["order_id"] == order_id:
                    return [order]
            return []
        elif "FROM orders" in query and "COUNT(*)" not in query and "AVG" not in query:
            return self.orders
        elif "inventory_forecast" in query.lower() or "forecast" in query.lower():
            return self.inventory
        elif "COUNT(*)" in query and "orders" in query.lower():
            # Return order KPI counts
            pending = len([o for o in self.orders if o["status"] == "pending"])
            approved = len([o for o in self.orders if o["status"] == "approved"])
            shipped = len([o for o in self.orders if o["status"] == "shipped"])
            return [{
                "total_orders": len(self.orders),
                "pending_orders": pending,
                "approved_orders": approved,
                "shipped_orders": shipped
            }]
        elif "AVG(o.quantity * p.price)" in query:
            # Return average order value
            return [{
                "avg_order_value": 125.50
            }]
        elif "SUM(CASE WHEN status" in query and "inventory_forecast" in query:
            # Return stock KPI based on actual inventory data
            low_stock = len([i for i in self.inventory if i["status"] == "low_stock"])
            out_of_stock = len([i for i in self.inventory if i["status"] == "out_of_stock"])
            reorder_needed = len([i for i in self.inventory if i["status"] == "reorder_needed"])
            return [{
                "low_stock_items": low_stock,
                "out_of_stock_items": out_of_stock,
                "reorder_needed_items": reorder_needed,
                "total_alerts": low_stock + out_of_stock + reorder_needed
            }]
        else:
            return []
    
    def execute_update(self, query: str, params: Optional[Any] = None) -> int:
        """Mock execute update."""
        return 1
    
    def execute_order_transaction(self, action: str, order_data: dict):
        """Execute order transaction with inventory updates (mock)."""
        import logging
        logger = logging.getLogger(__name__)
        
        if action == "create":
            return self._create_order_with_inventory_mock(order_data)
        elif action == "cancel":
            return self._cancel_order_with_inventory_mock(order_data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _create_order_with_inventory_mock(self, order_data):
        """Create order and update inventory (mock implementation)."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Generate new order ID
        new_order_id = len(self.orders) + 1
        
        # Find product name (mock product mapping)
        product_names = {
            1: "Wireless Bluetooth Headphones",
            2: "USB-C Charging Cable", 
            3: "Smartphone Case"
        }
        product_name = product_names.get(order_data["product_id"], f"Product {order_data['product_id']}")
        
        # Create new order
        new_order = {
            "order_id": new_order_id,
            "order_number": order_data["order_number"],
            "product": product_name,
            "quantity": order_data["quantity"],
            "store": order_data["store_id"],
            "requested_by": order_data["requested_by"],
            "order_date": datetime.now().isoformat(),
            "status": order_data["status"],
            "product_name": product_name,
            "customer_name": "Mock Customer",  # Mock customer name
            # Add missing fields for Order model validation
            "product_id": order_data["product_id"],
            "customer_id": order_data["customer_id"],
            "store_id": order_data["store_id"],
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to orders list
        self.orders.append(new_order)
        
        # Mock inventory update - find and update inventory item
        for item in self.inventory:
            if (item["item_id"] == f"PROD-{order_data['product_id']:03d}" and
                item.get("store_id", order_data["store_id"]) == order_data["store_id"]):
                
                old_stock = item["stock"]
                item["stock"] = max(0, old_stock - order_data["quantity"])
                
                # Update status based on new stock level
                if item["stock"] == 0:
                    item["status"] = "out_of_stock"
                    item["action"] = "Urgent Reorder"
                elif item["stock"] < 10:
                    item["status"] = "low_stock"
                    item["action"] = "Reorder Now"
                
                logger.info(f"Mock inventory updated: {item['item_name']} stock {old_stock} → {item['stock']}")
                break
        
        logger.info(f"Mock order created: {order_data['order_number']}")
        return [new_order]
    
    def _cancel_order_with_inventory_mock(self, order_data):
        """Cancel order and rollback inventory (mock implementation)."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Find and update the order
        for order in self.orders:
            if order["order_id"] == order_data["order_id"]:
                old_status = order["status"]
                order["status"] = "cancelled"
                
                # Mock inventory rollback - add quantity back
                for item in self.inventory:
                    # Simple matching - in real app this would be more sophisticated
                    if order["product"].lower() in item["item_name"].lower():
                        old_stock = item["stock"]
                        item["stock"] += order["quantity"]
                        
                        # Update status based on new stock level
                        if item["stock"] > 50:
                            item["status"] = "in_stock"
                            item["action"] = "Monitor"
                        elif item["stock"] > 10:
                            item["status"] = "low_stock"
                            item["action"] = "Monitor"
                        
                        logger.info(f"Mock inventory rolled back: {item['item_name']} stock {old_stock} → {item['stock']}")
                        break
                
                logger.info(f"Mock order cancelled: {order_data['order_number']} ({old_status} → cancelled)")
                return True
        
        return False
    
    def create_schema_if_not_exists(self):
        """Mock create schema."""
        pass
    
    def create_tables(self):
        """Mock create tables."""
        pass
    
    def seed_sample_data(self):
        """Mock seed data."""
        pass


# Use mock database for development
db = MockLakebaseConnection()