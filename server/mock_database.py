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
        if "FROM orders" in query and "COUNT(*)" not in query and "AVG" not in query:
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