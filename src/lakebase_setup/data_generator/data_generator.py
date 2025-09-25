#!/usr/bin/env python3
"""
Historical Transaction Data Generator for E-Bike Inventory Management

This script generates realistic inventory transaction data for the last 3 years
based on the VulcanTech e-bike manufacturing business model. The data includes:

- Seasonal patterns (spring/summer peak, winter low)
- Product category variations (motors, batteries, frames, etc.)
- Warehouse-specific patterns (Lyon, Hamburg, Milan)
- Realistic business scenarios (rush orders, supply delays, quality issues)
- Growth trends over time
- Holiday and weekend effects

The generated data is suitable for training ML models to predict future inventory levels.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Tuple
import json
import os
import uuid

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class TransactionGenerator:
    """Generates realistic inventory transaction data for e-bike manufacturing."""
    
    def __init__(self):
        """Initialize the transaction generator with business parameters."""
        
        # Date range: Now (today) going back 3 years
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=3*365)
        
        # Initialize products and warehouses data
        self.products_data = self.generate_products_data()
        self.warehouses_data = self.generate_warehouses_data()
        
        # Business parameters
        self.warehouses = {
            1: {"name": "Lyon Main Warehouse", "location": "Lyon, France", "capacity": "high"},
            2: {"name": "Hamburg Distribution Center", "location": "Hamburg, Germany", "capacity": "medium"},
            3: {"name": "Milan Assembly Hub", "location": "Milan, Italy", "capacity": "low"}
        }
        
        # Build product categories after products are generated
        self.build_product_categories()
        
        # Initialize inventory tracking
        self.inventory_levels = self.initialize_inventory_levels()
        
        # Track reorder history to prevent duplicate reorders
        self.reorder_history = {}  # {(product_id, warehouse_id): last_reorder_date}
        self.reorder_cooldown_days = 7  # Minimum days between reorders for same product-warehouse
        
        # Track historical inventory levels for output
        self.inventory_history = []  # List of inventory snapshots over time
        
        # Transaction types and their characteristics
        self.transaction_types = {
            "inbound": {
                "frequency": 0.20,  # Further reduced to 20% for lean operations
                "quantity_range": (5, 80),  # Smaller quantities for lean inventory
                "status_options": ["delivered", "shipped", "processing", "confirmed", "pending"],
                "status_weights": [0.70, 0.15, 0.10, 0.03, 0.02],
                "note_templates": [
                    "Monthly {category} shipment",
                    "Regular {category} delivery",
                    "URGENT: {category} expedite",
                    "emergency: {category} shortage",
                    "rush: {category} air freight",
                    "{category} stock replenishment",
                    "Quarterly {category} order",
                    "Bulk {category} purchase"
                ]
            },
            "sale": {
                "frequency": 0.75,  # Increased to 75% for higher turnover
                "quantity_range": (1, 18),  # Increased consumption for lean operations
                "status_options": ["delivered", "processing", "confirmed", "pending"],
                "status_weights": [0.85, 0.10, 0.03, 0.02],
                "note_templates": [
                    "Production Line A - Morning shift",
                    "Production Line A - URGENT: {category} shortage",
                    "{category} consumption - delay in supply",
                    "Hamburg production",
                    "Production - rush order",
                    "{category} consumption",
                    "Milan cargo production - delayed start",
                    "Production - URGENT shortage",
                    "Monday production - Normal",
                    "Battery consumption",
                    "Frame usage",
                    "Wheelset usage",
                    "Thursday production - Normal",
                    "Friday production increase",
                    "Milan Saturday production",
                    "Hamburg Sunday",
                    "Sunday production - Normal",
                    "Battery Sunday usage",
                    "Monday morning production",
                    "Battery usage current",
                    "Frame consumption today"
                ]
            },
            "adjustment": {
                "frequency": 0.05,  # 5% of transactions (unchanged)
                "quantity_range": (-10, 10),
                "status_options": ["delivered", "confirmed"],
                "status_weights": [0.95, 0.05],
                "note_templates": [
                    "Damaged {category} components",
                    "Inventory count correction",
                    "Quality inspection failure",
                    "Found additional stock",
                    "Returned defective items",
                    "Cycle count adjustment",
                    "Physical inventory variance",
                    "Damaged in transit"
                ]
            }
        }
        
        # Seasonal patterns (monthly multipliers)
        self.seasonal_patterns = {
            1: 0.6,   # January - Low (winter)
            2: 0.7,   # February - Low
            3: 0.9,   # March - Rising (spring prep)
            4: 1.2,   # April - High (spring)
            5: 1.4,   # May - Peak (spring/summer)
            6: 1.5,   # June - Peak (summer)
            7: 1.3,   # July - High (summer)
            8: 1.1,   # August - Medium (summer end)
            9: 1.0,   # September - Normal (fall)
            10: 0.8,  # October - Declining (fall)
            11: 0.6,  # November - Low (winter prep)
            12: 0.5   # December - Low (winter/holidays)
        }
        
        # Growth trend (yearly multipliers)
        self.growth_trends = {
            2022: 0.7,  # Startup year
            2023: 0.9,  # Growth year
            2024: 1.0,  # Current year (baseline)
            2025: 1.1,   # Future year (baseline)
        }
        
        # Day of week patterns
        self.dow_patterns = {
            0: 0.3,  # Monday - Low (weekend effect)
            1: 0.8,  # Tuesday - Medium
            2: 1.0,  # Wednesday - High
            3: 1.0,  # Thursday - High
            4: 1.2,  # Friday - Peak (end of week)
            5: 0.4,  # Saturday - Low
            6: 0.2   # Sunday - Very low
        }
    
    def get_seasonal_multiplier(self, date: datetime) -> float:
        """Calculate seasonal multiplier for a given date."""
        return self.seasonal_patterns[date.month]
    
    def get_growth_multiplier(self, date: datetime) -> float:
        """Calculate growth trend multiplier for a given date."""
        return self.growth_trends[date.year]
    
    def get_dow_multiplier(self, date: datetime) -> float:
        """Calculate day-of-week multiplier for a given date."""
        return self.dow_patterns[date.weekday()]
    
    def generate_products_data(self) -> List[Dict]:
        """Generate products data matching the DDL schema."""
        products = [
            # Motors & Drive Systems
            {"name": "E-Motor 250W Mid-Drive", "description": "Bosch Performance Line CX motor for mountain e-bikes", "sku": "MTR-250-MD-01", "price": 450.00, "unit": "piece", "category": "Motors", "reorder_level": 15},
            {"name": "E-Motor 500W Hub", "description": "Rear hub motor for city e-bikes, 500W continuous power", "sku": "MTR-500-HB-01", "price": 380.00, "unit": "piece", "category": "Motors", "reorder_level": 20},
            {"name": "E-Motor 750W Performance", "description": "High-performance mid-drive motor for cargo bikes", "sku": "MTR-750-PF-01", "price": 680.00, "unit": "piece", "category": "Motors", "reorder_level": 10},
            {"name": "Motor Controller Unit", "description": "Smart controller with regenerative braking support", "sku": "CTR-MCU-01", "price": 125.00, "unit": "piece", "category": "Motors", "reorder_level": 25},
            
            # Batteries
            {"name": "Battery 48V 14Ah", "description": "Lithium-ion battery pack, 672Wh capacity", "sku": "BAT-48-14-01", "price": 420.00, "unit": "piece", "category": "Batteries", "reorder_level": 30},
            {"name": "Battery 36V 10Ah", "description": "Compact battery for city bikes, 360Wh", "sku": "BAT-36-10-01", "price": 280.00, "unit": "piece", "category": "Batteries", "reorder_level": 40},
            {"name": "Battery 52V 20Ah", "description": "Extended range battery, 1040Wh for cargo bikes", "sku": "BAT-52-20-01", "price": 650.00, "unit": "piece", "category": "Batteries", "reorder_level": 15},
            {"name": "Battery Management System", "description": "BMS for battery protection and monitoring", "sku": "BAT-BMS-01", "price": 45.00, "unit": "piece", "category": "Batteries", "reorder_level": 50},
            {"name": "Battery Charger 4A", "description": "Fast charger compatible with all battery models", "sku": "BAT-CHG-4A", "price": 85.00, "unit": "piece", "category": "Batteries", "reorder_level": 35},
            
            # Frames
            {"name": "Carbon Frame MTB", "description": "Full suspension carbon frame for mountain e-bikes", "sku": "FRM-CBN-MTB-01", "price": 1200.00, "unit": "piece", "category": "Frames", "reorder_level": 8},
            {"name": "Aluminum Frame City", "description": "Step-through aluminum frame for urban bikes", "sku": "FRM-ALU-CTY-01", "price": 380.00, "unit": "piece", "category": "Frames", "reorder_level": 20},
            {"name": "Aluminum Frame Cargo", "description": "Reinforced frame for cargo e-bikes", "sku": "FRM-ALU-CRG-01", "price": 520.00, "unit": "piece", "category": "Frames", "reorder_level": 12},
            {"name": "Steel Frame Classic", "description": "Classic steel frame for vintage-style e-bikes", "sku": "FRM-STL-CLS-01", "price": 320.00, "unit": "piece", "category": "Frames", "reorder_level": 15},
            
            # Wheels & Tires
            {"name": "Wheel Set 29\" MTB", "description": "Tubeless-ready wheelset for mountain bikes", "sku": "WHL-29-MTB-01", "price": 320.00, "unit": "set", "category": "Wheels", "reorder_level": 25},
            {"name": "Wheel Set 28\" City", "description": "City bike wheels with puncture protection", "sku": "WHL-28-CTY-01", "price": 180.00, "unit": "set", "category": "Wheels", "reorder_level": 35},
            {"name": "Wheel Set 20\" Cargo", "description": "Heavy-duty wheels for cargo bikes", "sku": "WHL-20-CRG-01", "price": 240.00, "unit": "set", "category": "Wheels", "reorder_level": 20},
            {"name": "Tire 29x2.4 MTB", "description": "All-terrain tire for mountain bikes", "sku": "TIR-29-24-MTB", "price": 55.00, "unit": "piece", "category": "Wheels", "reorder_level": 60},
            {"name": "Tire 28x1.75 City", "description": "City tire with reflective sidewalls", "sku": "TIR-28-175-CTY", "price": 32.00, "unit": "piece", "category": "Wheels", "reorder_level": 80},
            
            # Brakes
            {"name": "Hydraulic Disc Brake Set", "description": "Shimano 4-piston hydraulic disc brakes", "sku": "BRK-HYD-4P-01", "price": 220.00, "unit": "set", "category": "Brakes", "reorder_level": 30},
            {"name": "Mechanical Disc Brake Set", "description": "Cable-actuated disc brakes for city bikes", "sku": "BRK-MEC-DS-01", "price": 85.00, "unit": "set", "category": "Brakes", "reorder_level": 40},
            {"name": "Brake Rotor 180mm", "description": "Stainless steel brake rotor", "sku": "BRK-RTR-180", "price": 28.00, "unit": "piece", "category": "Brakes", "reorder_level": 100},
            {"name": "Brake Pads Set", "description": "High-performance brake pads", "sku": "BRK-PAD-HP-01", "price": 18.00, "unit": "set", "category": "Brakes", "reorder_level": 120},
            
            # Display & Controls
            {"name": "LCD Display 3.5\"", "description": "Color LCD display with GPS and connectivity", "sku": "DSP-LCD-35-01", "price": 145.00, "unit": "piece", "category": "Electronics", "reorder_level": 35},
            {"name": "LED Display Basic", "description": "Basic LED display showing speed and battery", "sku": "DSP-LED-BS-01", "price": 45.00, "unit": "piece", "category": "Electronics", "reorder_level": 50},
            {"name": "Thumb Throttle", "description": "Variable speed thumb throttle", "sku": "CTL-THR-TB-01", "price": 22.00, "unit": "piece", "category": "Electronics", "reorder_level": 60},
            {"name": "Pedal Assist Sensor", "description": "Cadence sensor for pedal assist", "sku": "CTL-PAS-01", "price": 35.00, "unit": "piece", "category": "Electronics", "reorder_level": 70},
            {"name": "Torque Sensor", "description": "Bottom bracket torque sensor", "sku": "CTL-TRQ-BB-01", "price": 125.00, "unit": "piece", "category": "Electronics", "reorder_level": 25},
            
            # Drivetrain
            {"name": "Derailleur 11-Speed", "description": "Shimano XT 11-speed rear derailleur", "sku": "DRV-DER-11S-01", "price": 185.00, "unit": "piece", "category": "Drivetrain", "reorder_level": 20},
            {"name": "Chain 11-Speed", "description": "E-bike specific reinforced chain", "sku": "DRV-CHN-11S-01", "price": 42.00, "unit": "piece", "category": "Drivetrain", "reorder_level": 50},
            {"name": "Cassette 11-50T", "description": "11-speed cassette with wide range", "sku": "DRV-CAS-1150-01", "price": 125.00, "unit": "piece", "category": "Drivetrain", "reorder_level": 30},
            {"name": "Crankset 170mm", "description": "Forged aluminum crankset with chainring", "sku": "DRV-CRK-170-01", "price": 95.00, "unit": "piece", "category": "Drivetrain", "reorder_level": 35},
            
            # Accessories & Small Parts
            {"name": "Handlebar Aluminum", "description": "Wide aluminum handlebar 720mm", "sku": "ACC-HBR-720-01", "price": 45.00, "unit": "piece", "category": "Accessories", "reorder_level": 40},
            {"name": "Seatpost 31.6mm", "description": "Aluminum seatpost with quick release", "sku": "ACC-SPT-316-01", "price": 28.00, "unit": "piece", "category": "Accessories", "reorder_level": 45},
            {"name": "Saddle Comfort Plus", "description": "Ergonomic saddle with gel padding", "sku": "ACC-SDL-CP-01", "price": 52.00, "unit": "piece", "category": "Accessories", "reorder_level": 35},
            {"name": "Pedals Platform", "description": "Wide platform pedals with pins", "sku": "ACC-PDL-PLT-01", "price": 35.00, "unit": "pair", "category": "Accessories", "reorder_level": 50},
            {"name": "Grips Ergonomic", "description": "Lock-on ergonomic grips", "sku": "ACC-GRP-ERG-01", "price": 18.00, "unit": "pair", "category": "Accessories", "reorder_level": 80},
            {"name": "LED Light Set", "description": "Front and rear LED lights with USB charging", "sku": "ACC-LGT-SET-01", "price": 48.00, "unit": "set", "category": "Accessories", "reorder_level": 45},
            {"name": "Kickstand Heavy Duty", "description": "Adjustable center kickstand", "sku": "ACC-KST-HD-01", "price": 22.00, "unit": "piece", "category": "Accessories", "reorder_level": 60},
            {"name": "Cable Set Complete", "description": "Brake and shift cables kit", "sku": "ACC-CBL-KIT-01", "price": 15.00, "unit": "kit", "category": "Accessories", "reorder_level": 100},
            {"name": "Bolt Kit Frame", "description": "Complete bolt kit for frame assembly", "sku": "ACC-BLT-FRM-01", "price": 8.50, "unit": "kit", "category": "Accessories", "reorder_level": 150},
            {"name": "Wire Harness Main", "description": "Main electrical wiring harness", "sku": "ACC-WRH-MN-01", "price": 38.00, "unit": "piece", "category": "Electronics", "reorder_level": 55}
        ]
        
        # Add timestamps to each product
        base_time = datetime(2022, 1, 1, 9, 0, 0)
        for i, product in enumerate(products):
            product["created_at"] = base_time + timedelta(hours=i)
            product["updated_at"] = product["created_at"]
        
        return products
    
    def generate_warehouses_data(self) -> List[Dict]:
        """Generate warehouses data matching the DDL schema."""
        warehouses = [
            {
                "name": "Lyon Main Warehouse",
                "location": "Zone Industrielle, 69007 Lyon, France",
                "manager_id": 101,
                "timezone": "Europe/Paris",
                "created_at": datetime(2022, 1, 1, 9, 0, 0),
                "updated_at": datetime(2022, 1, 1, 9, 0, 0)
            },
            {
                "name": "Hamburg Distribution Center", 
                "location": "Hafencity, 20457 Hamburg, Germany",
                "manager_id": 102,
                "timezone": "Europe/Berlin",
                "created_at": datetime(2022, 1, 1, 9, 0, 0),
                "updated_at": datetime(2022, 1, 1, 9, 0, 0)
            },
            {
                "name": "Milan Assembly Hub",
                "location": "Via Industriale, 20090 Segrate MI, Italy", 
                "manager_id": 103,
                "timezone": "Europe/Rome",
                "created_at": datetime(2022, 1, 1, 9, 0, 0),
                "updated_at": datetime(2022, 1, 1, 9, 0, 0)
            }
        ]
        
        return warehouses
    
    def build_product_categories(self):
        """Build product categories mapping from generated products data."""
        categories = {}
        
        for i, product in enumerate(self.products_data):
            category = product["category"]
            if category not in categories:
                categories[category] = {
                    "base_demand": 0.7,  # Default demand
                    "seasonality": 0.3,  # Default seasonality
                    "price_range": (product["price"], product["price"]),
                    "lead_time_days": 14,
                    "bulk_order_frequency": 0.6,
                    "products": []
                }
            
            # Use actual product index (1-based) as product ID
            categories[category]["products"].append(i + 1)
            
            # Update price range
            min_price, max_price = categories[category]["price_range"]
            categories[category]["price_range"] = (min(min_price, product["price"]), max(max_price, product["price"]))
        
        # Set category-specific characteristics
        category_configs = {
            "Motors": {"base_demand": 0.8, "seasonality": 0.3, "lead_time_days": 14, "bulk_order_frequency": 0.7},
            "Batteries": {"base_demand": 0.9, "seasonality": 0.2, "lead_time_days": 21, "bulk_order_frequency": 0.8},
            "Frames": {"base_demand": 0.6, "seasonality": 0.4, "lead_time_days": 28, "bulk_order_frequency": 0.6},
            "Wheels": {"base_demand": 0.7, "seasonality": 0.3, "lead_time_days": 14, "bulk_order_frequency": 0.7},
            "Brakes": {"base_demand": 0.8, "seasonality": 0.2, "lead_time_days": 10, "bulk_order_frequency": 0.8},
            "Electronics": {"base_demand": 0.7, "seasonality": 0.1, "lead_time_days": 7, "bulk_order_frequency": 0.6},
            "Drivetrain": {"base_demand": 0.6, "seasonality": 0.3, "lead_time_days": 14, "bulk_order_frequency": 0.7},
            "Accessories": {"base_demand": 0.5, "seasonality": 0.4, "lead_time_days": 7, "bulk_order_frequency": 0.5}
        }
        
        for category, config in category_configs.items():
            if category in categories:
                categories[category].update(config)
        
        self.product_categories = categories
    
    def initialize_inventory_levels(self) -> Dict[Tuple[int, int], int]:
        """Initialize inventory levels for all product-warehouse combinations."""
        inventory_levels = {}
        
        # Set initial inventory levels based on product categories and reorder levels
        for i, product in enumerate(self.products_data):
            product_id = i + 1
            reorder_level = product["reorder_level"]
            
            for warehouse_id in [1, 2, 3]:
                # Set initial inventory to lean levels: 1.2-2.2x reorder level
                base_stock = reorder_level * random.uniform(1.2, 2.2)
                
                # Adjust by warehouse capacity (lean multipliers)
                if warehouse_id == 1:  # Lyon - high capacity
                    multiplier = random.uniform(1.0, 1.4)
                elif warehouse_id == 2:  # Hamburg - medium capacity
                    multiplier = random.uniform(0.8, 1.2)
                else:  # Milan - low capacity
                    multiplier = random.uniform(0.6, 1.0)
                
                initial_stock = int(base_stock * multiplier)
                inventory_levels[(product_id, warehouse_id)] = max(initial_stock, reorder_level)
        
        return inventory_levels
    
    def get_current_inventory(self, product_id: int, warehouse_id: int) -> int:
        """Get current inventory level for a product-warehouse combination."""
        return self.inventory_levels.get((product_id, warehouse_id), 0)
    
    def update_inventory(self, product_id: int, warehouse_id: int, quantity_change: int):
        """Update inventory level for a product-warehouse combination."""
        key = (product_id, warehouse_id)
        current_level = self.inventory_levels.get(key, 0)
        new_level = max(0, current_level + quantity_change)  # Never go below zero
        self.inventory_levels[key] = new_level
    
    def record_inventory_snapshot(self, date: datetime):
        """Record a snapshot of all inventory levels for a given date."""
        snapshot = {
            'date': date,
            'inventory_levels': {}
        }
        
        for (product_id, warehouse_id), level in self.inventory_levels.items():
            key = f"P{product_id}_W{warehouse_id}"
            snapshot['inventory_levels'][key] = level
        
        self.inventory_history.append(snapshot)
    
    def generate_transaction_number(self, transaction_type: str, date: datetime, sequence: int) -> str:
        """Generate realistic transaction number (max 50 chars)."""
        type_prefix = {
            "inbound": "INB",
            "sale": "SAL", 
            "adjustment": "ADJ"
        }
        
        date_str = date.strftime("%y%m%d")  # Use 2-digit year to save space
        # Use first 6 chars of uuid4 for uniqueness, plus sequence for rare collisions
        '''suffix = uuid.uuid4().hex[:6].upper()
        if sequence > 0:
            suffix += chr(ord('A') + sequence)
        '''
        import string
        chars = string.ascii_uppercase + string.digits
        suffix = ''.join(random.choices(chars, k=5))
        
        # Ensure total length is under 50 characters
        transaction_num = f"{type_prefix[transaction_type]}-{date_str}-{suffix}"
        
        # If still too long, truncate the suffix
        '''if len(transaction_num) > 50:
            max_suffix_len = 50 - len(f"{type_prefix[transaction_type]}-{date_str}")
            if max_suffix_len > 0:
                suffix = suffix[:max_suffix_len]
                transaction_num = f"{type_prefix[transaction_type]}-{date_str}{suffix}"
            else:
                transaction_num = f"{type_prefix[transaction_type]}-{date_str}"
        '''
        
        return transaction_num
    
    def select_product_for_category(self, category: str) -> int:
        """Select a product ID for a given category."""
        products = self.product_categories[category]["products"]
        return random.choice(products)
    
    def select_warehouse(self, product_id: int) -> int:
        """Select warehouse based on product and business logic."""
        # Lyon (1) handles most products
        # Hamburg (2) specializes in city bikes
        # Milan (3) handles cargo bikes
        
        if product_id in [2, 6, 11, 15, 20]:  # City bike components
            return random.choices([1, 2], weights=[0.3, 0.7])[0]
        elif product_id in [3, 7, 12, 16]:  # Cargo bike components
            return random.choices([1, 3], weights=[0.2, 0.8])[0]
        else:  # General components
            return random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    
    def generate_quantity(self, transaction_type: str, category: str, product_id: int, warehouse_id: int) -> int:
        """Generate realistic quantity based on transaction type, category, and current inventory."""
        base_range = self.transaction_types[transaction_type]["quantity_range"]
        current_inventory = self.get_current_inventory(product_id, warehouse_id)
        product = self.products_data[product_id - 1]
        reorder_level = product["reorder_level"]
        
        if transaction_type == "inbound":
            # Inbound transactions - balanced with sales and inventory-aware
            if self.product_categories[category]["bulk_order_frequency"] > 0.7:
                # High bulk frequency - moderate quantities
                multiplier = random.uniform(0.9, 1.4)
            else:
                multiplier = random.uniform(0.7, 1.2)
            
            # Ultra-lean inventory management - minimal excess
            if current_inventory < reorder_level * 0.3:
                # Critical restocking - but controlled
                multiplier *= random.uniform(1.0, 1.4)
            elif current_inventory < reorder_level * 0.8:
                # Normal restocking - minimal quantities
                multiplier *= random.uniform(0.8, 1.2)
            elif current_inventory < reorder_level * 1.2:
                # Light restocking
                multiplier *= random.uniform(0.6, 0.9)
            else:
                # Already well-stocked, very minimal inbound
                multiplier *= random.uniform(0.1, 0.3)
            
            quantity = int(random.uniform(*base_range) * multiplier)
            return max(3, quantity)  # Lower minimum for lean operations
            
        elif transaction_type == "sale":
            # Sale transactions - limited by current inventory and balanced approach
            max_sale = min(current_inventory, base_range[1])
            if max_sale <= 0:
                return 0  # No sales if no inventory
            
            # Reduce sales pressure when inventory is low to maintain balance
            if current_inventory < reorder_level:
                # Very conservative sales when below reorder level
                max_sale = min(max_sale, max(1, int(current_inventory * 0.2)))
            elif current_inventory < reorder_level * 1.5:
                # Moderate sales when approaching reorder level
                max_sale = min(max_sale, max(1, int(current_inventory * 0.4)))
            
            # Generate sale quantity with bias toward smaller quantities for smoother sales
            if max_sale <= 3:
                # For very small max sales, use uniform distribution
                quantity = random.randint(1, max_sale)
            else:
                # For larger max sales, bias toward smaller quantities
                # 80% chance of small quantities (1-4), 20% chance of larger quantities
                if random.random() < 0.8:
                    quantity = random.randint(1, min(4, max_sale))
                else:
                    quantity = random.randint(min(5, max_sale), max_sale)
            
            return quantity
            
        else:  # adjustment
            # Adjustments - small quantities, can be positive or negative
            max_adjustment = min(current_inventory, abs(base_range[1]))
            quantity = random.randint(base_range[0], base_range[1])
            
            # If negative adjustment would make inventory go below zero, limit it
            if quantity < 0 and abs(quantity) > current_inventory:
                quantity = -current_inventory
            
            return quantity
    
    def generate_note(self, transaction_type: str, category: str, date: datetime) -> str:
        """Generate realistic transaction note."""
        templates = self.transaction_types[transaction_type]["note_templates"]
        template = random.choice(templates)
        
        # Replace placeholders
        note = template.format(category=category)
        
        # Add urgency indicators for certain conditions
        if random.random() < 0.1:  # 10% chance of urgency
            if "URGENT" not in note and "emergency" not in note and "rush" not in note:
                note = f"URGENT: {note}"
        
        return note
    
    def generate_time_aware_status(self, transaction_type: str, date: datetime) -> str:
        """Generate transaction status based on how old the transaction is."""
        # Calculate days ago from current end_date
        days_ago = (self.end_date - date).days
        
        # Get base status options and weights
        status_options = self.transaction_types[transaction_type]["status_options"]
        base_weights = self.transaction_types[transaction_type]["status_weights"]
        
        # Adjust weights based on transaction age
        if days_ago > 30:  # Older than 30 days - almost all delivered
            # 98% delivered, 2% other statuses
            adjusted_weights = [0.98] + [0.02 / (len(status_options) - 1)] * (len(status_options) - 1)
        elif days_ago > 14:  # 14-30 days old - mostly delivered
            # 90% delivered, 10% other statuses  
            adjusted_weights = [0.90] + [0.10 / (len(status_options) - 1)] * (len(status_options) - 1)
        elif days_ago > 7:  # 7-14 days old - generally delivered
            # 80% delivered, 20% other statuses
            adjusted_weights = [0.80] + [0.20 / (len(status_options) - 1)] * (len(status_options) - 1)
        elif days_ago > 3:  # 3-7 days old - mix of statuses
            # 65% delivered, 35% other statuses
            adjusted_weights = [0.65] + [0.35 / (len(status_options) - 1)] * (len(status_options) - 1)
        elif days_ago > 1:  # 1-3 days old - more active statuses
            # 35% delivered, 65% other statuses
            adjusted_weights = [0.35] + [0.65 / (len(status_options) - 1)] * (len(status_options) - 1)
        else:  # Very recent (today/yesterday) - use original distribution for variety
            adjusted_weights = base_weights
        
        return random.choices(status_options, weights=adjusted_weights)[0]
    
    def generate_transaction_timestamp(self, date: datetime) -> datetime:
        """Generate realistic transaction timestamp within a day."""
        # Business hours: 6 AM to 6 PM
        # Peak hours: 7-9 AM, 1-3 PM
        
        hours = list(range(6, 19))  # 6 AM to 6 PM (13 hours)
        weights = [0.5, 1.0, 1.0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.5]  # 13 weights
        
        hour = random.choices(hours, weights=weights)[0]
        
        minute = random.randint(0, 59)
        
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def generate_daily_transactions(self, date: datetime) -> List[Dict]:
        """Generate all transactions for a single day."""
        transactions = []
        
        # Calculate daily activity level
        seasonal_mult = self.get_seasonal_multiplier(date)
        growth_mult = self.get_growth_multiplier(date)
        dow_mult = self.get_dow_multiplier(date)
        
        daily_activity = seasonal_mult * growth_mult * dow_mult
        
        # Base number of transactions per day (balanced for realistic business activity)
        base_transactions = int(150 * daily_activity)  # Reduced for more realistic transaction volume
        num_transactions = max(1, int(np.random.poisson(base_transactions)))
        
        # Check for reorder needs more frequently to maintain balanced inventory
        is_business_day = date.weekday() < 5  # Monday=0, Friday=4
        if is_business_day:
            # Higher probability on Mondays (weekly planning), moderate on other days
            if date.weekday() == 0:  # Monday
                reorder_probability = 0.4  # Increased for proactive management
            else:
                reorder_probability = 0.2  # Increased for better responsiveness
            
            if random.random() < reorder_probability:
                reorder_transactions = self.generate_reorder_transactions(date, 0)
                transactions.extend(reorder_transactions)
        
        # Assess inventory health for dynamic balancing
        health_factor = self.assess_inventory_health()
        
        # Adjust transaction type frequencies based on inventory health
        base_frequencies = {t: self.transaction_types[t]["frequency"] for t in self.transaction_types.keys()}
        adjusted_frequencies = base_frequencies.copy()
        
        # Adjust inbound frequency based on inventory health
        adjusted_frequencies["inbound"] *= health_factor
        # Normalize frequencies to sum to 1.0
        total_freq = sum(adjusted_frequencies.values())
        adjusted_frequencies = {k: v/total_freq for k, v in adjusted_frequencies.items()}
        
        # Generate transactions
        for i in range(num_transactions):
            
            # Select transaction type with health-adjusted frequencies
            transaction_type = random.choices(
                list(adjusted_frequencies.keys()),
                weights=list(adjusted_frequencies.values())
            )[0]
            
            # Select product category
            categories = list(self.product_categories.keys())
            weights = [self.product_categories[c]["base_demand"] for c in categories]
            category = random.choices(categories, weights=weights)[0]
            
            # Select product and warehouse
            product_id = self.select_product_for_category(category)
            warehouse_id = self.select_warehouse(product_id)
            
            # Generate quantity (inventory-aware)
            quantity = self.generate_quantity(transaction_type, category, product_id, warehouse_id)
            
            # Skip transaction if quantity is 0 (e.g., no inventory for sale)
            if quantity == 0:
                continue
            
            # Make outbound transactions negative
            if transaction_type in ["sale", "adjustment"]:
                quantity = -abs(quantity)
            
            # Update inventory levels
            self.update_inventory(product_id, warehouse_id, quantity)
            
            # Generate time-aware status (older = more likely delivered)
            status = self.generate_time_aware_status(transaction_type, date)
            
            # Generate note
            note = self.generate_note(transaction_type, category, date)
            
            # Generate timestamp
            timestamp = self.generate_transaction_timestamp(date)
            
            # Generate transaction number
            transaction_number = self.generate_transaction_number(transaction_type, date, i)
            
            transaction = {
                "transaction_number": transaction_number,
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "quantity_change": quantity,
                "transaction_type": transaction_type,
                "status": status,
                "notes": note,
                "transaction_timestamp": timestamp,
                "updated_at": timestamp  # updated_at same as transaction_timestamp for simplicity
            }
            
            transactions.append(transaction)
        
        # Record inventory snapshot at end of day
        self.record_inventory_snapshot(date)
        
        return transactions
    
    def generate_reorder_transactions(self, date: datetime, sequence_offset: int) -> List[Dict]:
        """Generate inbound transactions for products that need reordering."""
        reorder_transactions = []
        
        # Check each product-warehouse combination for reorder needs
        for i, product in enumerate(self.products_data):
            product_id = i + 1
            reorder_level = product["reorder_level"]
            
            for warehouse_id in [1, 2, 3]:
                current_inventory = self.get_current_inventory(product_id, warehouse_id)
                key = (product_id, warehouse_id)
                
                # Check if we need to reorder with more proactive thresholds
                needs_reorder = False
                
                # Proactive reordering when inventory is below 1.5x reorder level
                if current_inventory < reorder_level * 1.5:
                    last_reorder = self.reorder_history.get(key)
                    if last_reorder is None:
                        # Never reordered before
                        needs_reorder = True
                    else:
                        days_since_reorder = (date - last_reorder).days
                        # Shorter cooldown for more responsive restocking
                        cooldown_days = 5 if current_inventory < reorder_level else 7
                        if days_since_reorder >= cooldown_days:
                            needs_reorder = True
                
                if needs_reorder:
                    # Generate ultra-lean reorder quantities - just enough to avoid stockout
                    target_stock = reorder_level * 1.2  # Target: 1.2x reorder level for ultra-lean
                    shortage = max(1, target_stock - current_inventory)
                    
                    if current_inventory < reorder_level * 0.3:
                        # Emergency reorder - bring to minimal safe level
                        reorder_quantity = int(shortage * random.uniform(1.0, 1.2))
                    elif current_inventory < reorder_level * 0.8:
                        # Standard reorder - minimal replenishment
                        reorder_quantity = int(shortage * random.uniform(0.8, 1.0))
                    else:
                        # Proactive reorder - tiny top-up
                        reorder_quantity = int(shortage * random.uniform(0.4, 0.6))
                    
                    # Generate transaction
                    timestamp = self.generate_transaction_timestamp(date)
                    transaction_number = self.generate_transaction_number("inbound", date, sequence_offset + len(reorder_transactions))
                    
                    # Update inventory
                    self.update_inventory(product_id, warehouse_id, reorder_quantity)
                    
                    # Record this reorder in history
                    self.reorder_history[key] = date
                    
                    # Determine urgency level based on how far below reorder level
                    if current_inventory == 0:
                        urgency = "CRITICAL"
                    elif current_inventory < reorder_level * 0.5:
                        urgency = "URGENT"
                    else:
                        urgency = "LOW"
                    
                    # Generate time-aware status for reorder transactions
                    reorder_status = self.generate_time_aware_status("inbound", date)
                    
                    transaction = {
                        "transaction_number": transaction_number,
                        "product_id": product_id,
                        "warehouse_id": warehouse_id,
                        "quantity_change": reorder_quantity,
                        "transaction_type": "inbound",
                        "status": reorder_status,
                        "notes": f"{urgency}: {product['category']} reorder - inventory at {current_inventory} (reorder level: {reorder_level})",
                        "transaction_timestamp": timestamp,
                        "updated_at": timestamp
                    }
                    
                    reorder_transactions.append(transaction)
        
        return reorder_transactions
    
    def cleanup_reorder_history(self, current_date: datetime):
        """Clean up old reorder history to prevent memory issues."""
        # Keep only reorder history from the last 30 days
        cutoff_date = current_date - timedelta(days=30)
        keys_to_remove = []
        
        for key, last_reorder_date in self.reorder_history.items():
            if last_reorder_date < cutoff_date:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.reorder_history[key]
    
    def assess_inventory_health(self) -> float:
        """Assess overall inventory health and return a balance factor (0.0 to 2.0)."""
        total_products = 0
        healthy_products = 0
        
        for i, product in enumerate(self.products_data):
            product_id = i + 1
            reorder_level = product["reorder_level"]
            
            for warehouse_id in [1, 2, 3]:
                current_inventory = self.get_current_inventory(product_id, warehouse_id)
                total_products += 1
                
                # Consider inventory healthy if it's above 1.2x reorder level
                if current_inventory > reorder_level * 1.2:
                    healthy_products += 1
        
        if total_products == 0:
            return 1.0
        
        health_ratio = healthy_products / total_products
        
        # Return balance factor for lean operations:
        # - Target 70-80% healthy ratio for lean inventory
        # - More aggressive reduction when overstocked
        if health_ratio < 0.4:
            return 1.5  # Crisis mode - moderate increase
        elif health_ratio < 0.6:
            return 1.2  # Recovery mode
        elif health_ratio < 0.8:
            return 1.0  # Normal operations - lean target zone
        elif health_ratio < 0.9:
            return 0.6  # Reduce inbound - getting overstocked
        else:
            return 0.3  # Minimal inbound - overstocked
    
    def generate_all_transactions(self) -> pd.DataFrame:
        """Generate all transactions for the entire period."""
        all_transactions = []
        
        current_date = self.start_date
        total_days = (self.end_date - self.start_date).days
        
        print(f"Generating transactions from {self.start_date.date()} to {self.end_date.date()}")
        print(f"Total days: {total_days}")
        
        for day in range(total_days):
            if day % 100 == 0:
                progress = (day / total_days) * 100
                print(f"Progress: {progress:.1f}% - Processing {current_date.date()}")
            
            daily_transactions = self.generate_daily_transactions(current_date)
            all_transactions.extend(daily_transactions)
            
            # Clean up old reorder history periodically
            if day % 30 == 0:  # Every 30 days
                self.cleanup_reorder_history(current_date)
            
            current_date += timedelta(days=1)
        
        print(f"Generated {len(all_transactions)} total transactions")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_transactions)
        
        # Sort by timestamp
        df = df.sort_values("transaction_timestamp").reset_index(drop=True)
        
        # Add transaction_id
        df["transaction_id"] = range(1, len(df) + 1)
        
        return df
    
    def add_special_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add special events like supply chain disruptions, holidays, etc."""
        
        # Black Friday effect (November)
        black_friday_dates = [
            datetime(2022, 11, 25),
            datetime(2023, 11, 24),
            datetime(2024, 11, 29)
        ]
        
        for bf_date in black_friday_dates:
            if bf_date >= self.start_date and bf_date <= self.end_date:
                # Add extra transactions around Black Friday
                bf_start = bf_date - timedelta(days=3)
                bf_end = bf_date + timedelta(days=3)
                
                mask = (df["transaction_timestamp"] >= bf_start) & (df["transaction_timestamp"] <= bf_end)
                df.loc[mask, "notes"] = df.loc[mask, "notes"] + " - Black Friday rush"
        
        # COVID-19 supply chain disruption (2022)
        covid_start = datetime(2022, 3, 1)
        covid_end = datetime(2022, 6, 30)
        
        if covid_start >= self.start_date and covid_end <= self.end_date:
            mask = (df["transaction_timestamp"] >= covid_start) & (df["transaction_timestamp"] <= covid_end)
            df.loc[mask, "notes"] = df.loc[mask, "notes"] + " - Supply chain disruption"
        
        return df
    
    def save_to_sql(self, df: pd.DataFrame, filename: str = "historical_transactions.sql"):
        """Save transactions to SQL file."""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w') as f:
            f.write("-- Historical Transaction Data for E-Bike Inventory Management\n")
            f.write("-- Generated by generate_historical_transactions.py\n")
            f.write("-- Date range: {} to {}\n\n".format(
                self.start_date.strftime("%Y-%m-%d"),
                self.end_date.strftime("%Y-%m-%d")
            ))
            
            f.write("-- Clear existing data\n")
            f.write("TRUNCATE TABLE inventory_transactions CASCADE;\n")
            f.write("TRUNCATE TABLE products CASCADE;\n")
            f.write("TRUNCATE TABLE warehouses CASCADE;\n")
            f.write("ALTER SEQUENCE inventory_transactions_transaction_id_seq RESTART WITH 1;\n")
            f.write("ALTER SEQUENCE products_product_id_seq RESTART WITH 1;\n")
            f.write("ALTER SEQUENCE warehouses_warehouse_id_seq RESTART WITH 1;\n\n")
            
            # Insert products
            f.write("-- Insert products\n")
            f.write("INSERT INTO products (name, description, sku, price, unit, category, reorder_level, created_at, updated_at) VALUES\n")
            
            for i, product in enumerate(self.products_data):
                f.write("('{}', '{}', '{}', {}, '{}', '{}', {}, '{}', '{}')".format(
                    product["name"].replace("'", "''"),
                    product["description"].replace("'", "''"),
                    product["sku"],
                    product["price"],
                    product["unit"],
                    product["category"],
                    product["reorder_level"],
                    product["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    product["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                if i < len(self.products_data) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n\n")
            
            # Insert warehouses
            f.write("-- Insert warehouses\n")
            f.write("INSERT INTO warehouses (name, location, manager_id, timezone, created_at, updated_at) VALUES\n")
            
            for i, warehouse in enumerate(self.warehouses_data):
                f.write("('{}', '{}', {}, '{}', '{}', '{}')".format(
                    warehouse["name"].replace("'", "''"),
                    warehouse["location"].replace("'", "''"),
                    warehouse["manager_id"],
                    warehouse["timezone"],
                    warehouse["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    warehouse["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                if i < len(self.warehouses_data) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n\n")
            
            # Insert transactions
            f.write("-- Insert inventory transactions\n")
            f.write("INSERT INTO inventory_transactions (transaction_number, product_id, warehouse_id, quantity_change, transaction_type, status, notes, transaction_timestamp, updated_at) VALUES\n")
            
            for i, row in df.iterrows():
                f.write("('{}', {}, {}, {}, '{}', '{}', '{}', '{}', '{}')".format(
                    row["transaction_number"],
                    row["product_id"],
                    row["warehouse_id"],
                    row["quantity_change"],
                    row["transaction_type"],
                    row["status"],
                    row["notes"].replace("'", "''"),  # Escape single quotes
                    row["transaction_timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    row["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                if i < len(df) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
        
        print(f"SQL file saved to: {filepath}")
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = "historical_transactions.csv"):
        """Save transactions to CSV file."""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        df.to_csv(filepath, index=False)
        print(f"CSV file saved to: {filepath}")
    
    def save_products_to_csv(self, filename: str = "products.csv"):
        """Save products to CSV file."""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        products_df = pd.DataFrame(self.products_data)
        products_df.to_csv(filepath, index=False)
        print(f"Products CSV file saved to: {filepath}")
    
    def save_warehouses_to_csv(self, filename: str = "warehouses.csv"):
        """Save warehouses to CSV file."""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        warehouses_df = pd.DataFrame(self.warehouses_data)
        warehouses_df.to_csv(filepath, index=False)
        print(f"Warehouses CSV file saved to: {filepath}")
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the generated data."""
        
        summary = {
            "total_transactions": len(df),
            "total_products": len(self.products_data),
            "total_warehouses": len(self.warehouses_data),
            "date_range": {
                "start": df["transaction_timestamp"].min().strftime("%Y-%m-%d"),
                "end": df["transaction_timestamp"].max().strftime("%Y-%m-%d")
            },
            "transaction_types": df["transaction_type"].value_counts().to_dict(),
            "warehouses": df["warehouse_id"].value_counts().to_dict(),
            "products": df["product_id"].value_counts().to_dict(),
            "status_distribution": df["status"].value_counts().to_dict(),
            "monthly_totals": {str(k): v for k, v in df.groupby(df["transaction_timestamp"].dt.to_period("M")).size().to_dict().items()},
            "total_quantity_changes": {
                "inbound": df[df["transaction_type"] == "inbound"]["quantity_change"].sum(),
                "sale": df[df["transaction_type"] == "sale"]["quantity_change"].sum(),
                "adjustment": df[df["transaction_type"] == "adjustment"]["quantity_change"].sum()
            },
            "product_categories": {
                category: len([p for p in self.products_data if p["category"] == category])
                for category in set(p["category"] for p in self.products_data)
            },
            "warehouse_details": [
                {
                    "warehouse_id": i + 1,
                    "name": warehouse["name"],
                    "location": warehouse["location"],
                    "manager_id": warehouse["manager_id"]
                }
                for i, warehouse in enumerate(self.warehouses_data)
            ]
        }
        
        return summary
    
    def generate_inventory_summary(self) -> Dict:
        """Generate final inventory levels summary."""
        inventory_summary = {
            "final_inventory_levels": {},
            "inventory_statistics": {
                "total_products": len(self.products_data),
                "total_warehouses": len(self.warehouses_data),
                "total_combinations": len(self.inventory_levels)
            }
        }
        
        # Calculate statistics for each product-warehouse combination
        for (product_id, warehouse_id), level in self.inventory_levels.items():
            product = self.products_data[product_id - 1]
            warehouse = self.warehouses_data[warehouse_id - 1]
            
            key = f"P{product_id}_W{warehouse_id}"
            inventory_summary["final_inventory_levels"][key] = {
                "product_name": product["name"],
                "product_category": product["category"],
                "warehouse_name": warehouse["name"],
                "current_inventory": level,
                "reorder_level": product["reorder_level"],
                "status": "healthy" if level > product["reorder_level"] else "needs_reorder"
            }
        
        return inventory_summary
    
    def save_inventory_history_to_csv(self):
        """Save inventory history to CSV file."""
        if not self.inventory_history:
            print("No inventory history to save")
            return
        
        # Convert inventory history to DataFrame format
        rows = []
        for snapshot in self.inventory_history:
            date = snapshot['date']
            for key, level in snapshot['inventory_levels'].items():
                # Extract product_id and warehouse_id from key like "P1_W2"
                parts = key.split('_')
                product_id = int(parts[0][1:])  # Remove 'P' prefix
                warehouse_id = int(parts[1][1:])  # Remove 'W' prefix
                
                rows.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'product_id': product_id,
                    'warehouse_id': warehouse_id,
                    'inventory_level': level
                })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(rows)
        
        # Sort by date, product_id, warehouse_id for better organization
        df = df.sort_values(['date', 'product_id', 'warehouse_id'])
        
        file_path = os.path.join(os.path.dirname(__file__), "historical_inventory_levels.csv")
        df.to_csv(file_path, index=False)
        print(f"Inventory history CSV file saved to: {file_path}")
        return file_path
    
    def save_inventory_history_to_json(self):
        """Save inventory history to JSON file (more compact for large datasets)."""
        if not self.inventory_history:
            print("No inventory history to save")
            return
        
        # Convert dates to strings for JSON serialization
        json_history = []
        for snapshot in self.inventory_history:
            json_snapshot = {
                'date': snapshot['date'].strftime('%Y-%m-%d'),
                'inventory_levels': snapshot['inventory_levels']
            }
            json_history.append(json_snapshot)
        
        file_path = os.path.join(os.path.dirname(__file__), "historical_inventory_levels.json")
        with open(file_path, 'w') as f:
            json.dump(json_history, f, indent=2)
        print(f"Inventory history JSON file saved to: {file_path}")
        return file_path


def generate_data():
    """Main function to generate historical transaction data."""
    print("🚀 Starting Historical Transaction Data Generation")
    print("=" * 60)
    
    # Initialize generator
    generator = TransactionGenerator()
    
    # Generate all transactions
    print("\n📊 Generating transaction data...")
    df = generator.generate_all_transactions()
    
    # Add special events
    print("\n🎯 Adding special events...")
    df = generator.add_special_events(df)
    
    # Generate summary report
    print("\n📈 Generating summary report...")
    summary = generator.generate_summary_report(df)
    inventory_summary = generator.generate_inventory_summary()
    
    # Save data
    print("\n💾 Saving data...")
    generator.save_to_csv(df)
    generator.save_products_to_csv()
    generator.save_warehouses_to_csv()
    generator.save_inventory_history_to_csv()
    generator.save_inventory_history_to_json()
    
    # Save summary reports
    summary_file = os.path.join(os.path.dirname(__file__), "transaction_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary report saved to: {summary_file}")
    
    inventory_file = os.path.join(os.path.dirname(__file__), "inventory_summary.json")
    with open(inventory_file, 'w') as f:
        json.dump(inventory_summary, f, indent=2, default=str)
    print(f"Inventory summary saved to: {inventory_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total transactions generated: {summary['total_transactions']:,}")
    print(f"Total products generated: {summary['total_products']}")
    print(f"Total warehouses generated: {summary['total_warehouses']}")
    print(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"Transaction types: {summary['transaction_types']}")
    print(f"Warehouse distribution: {summary['warehouses']}")
    print(f"Product categories: {summary['product_categories']}")
    print(f"Total inbound quantity: {summary['total_quantity_changes']['inbound']:,}")
    print(f"Total sale quantity: {summary['total_quantity_changes']['sale']:,}")
    print(f"Total adjustment quantity: {summary['total_quantity_changes']['adjustment']:,}")
    
    print("\n✅ Data generation completed successfully!")
    print("Files created:")
    print("  - historical_transactions.csv")
    print("  - products.csv")
    print("  - warehouses.csv")
    print("  - historical_inventory_levels.csv")
    print("  - historical_inventory_levels.json")
    print("  - transaction_summary.json")
    print("  - inventory_summary.json")


if __name__ == "__main__":
    generate_data()
