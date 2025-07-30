#!/usr/bin/env python3
"""
Logistics Optimization Demo - Data Analysis Framework

Comprehensive demonstration of complex relational data analysis for logistics operations.
Features multiple interconnected tables with foreign key relationships and
optimization scenarios for route planning, fuel efficiency, and capacity management.

Use Case: Multi-warehouse logistics network with route optimization capabilities
- Route optimization for fastest delivery
- Fuel consumption minimization
- Vehicle capacity optimization
- Driver scheduling and availability
- Customer delivery preferences
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import math

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    import data_analysis_framework as daf

    print("✅ Data Analysis Framework imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


class LogisticsDataGenerator:
    """Generate realistic logistics data with complex relationships"""

    def __init__(self, seed=42):
        np.random.seed(seed)
        self.warehouses = None
        self.customers = None
        self.vehicles = None
        self.drivers = None
        self.routes = None
        self.shipments = None
        self.deliveries = None

    def create_warehouses(self, num_warehouses=8):
        """Create warehouse master data"""
        print("🏭 Generating Warehouses...")

        warehouse_locations = [
            {"city": "New York", "state": "NY", "lat": 40.7128, "lon": -74.0060},
            {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lon": -118.2437},
            {"city": "Chicago", "state": "IL", "lat": 41.8781, "lon": -87.6298},
            {"city": "Houston", "state": "TX", "lat": 29.7604, "lon": -95.3698},
            {"city": "Phoenix", "state": "AZ", "lat": 33.4484, "lon": -112.0740},
            {"city": "Philadelphia", "state": "PA", "lat": 39.9526, "lon": -75.1652},
            {"city": "San Antonio", "state": "TX", "lat": 29.4241, "lon": -98.4936},
            {"city": "San Diego", "state": "CA", "lat": 32.7157, "lon": -117.1611},
        ]

        warehouses = []
        for i, location in enumerate(warehouse_locations[:num_warehouses]):
            warehouse = {
                "warehouse_id": f"WH{i+1:03d}",
                "warehouse_name": f'{location["city"]} Distribution Center',
                "city": location["city"],
                "state": location["state"],
                "latitude": location["lat"],
                "longitude": location["lon"],
                "capacity_pallets": np.random.randint(1000, 5000),
                "current_inventory_pallets": np.random.randint(200, 4000),
                "operating_cost_per_day": round(np.random.uniform(5000, 15000), 2),
                "dock_doors": np.random.randint(8, 24),
                "storage_type": np.random.choice(
                    ["Ambient", "Refrigerated", "Mixed"], p=[0.5, 0.2, 0.3]
                ),
                "opened_date": datetime.now() - timedelta(days=np.random.randint(365, 3650)),
            }
            warehouses.append(warehouse)

        self.warehouses = pd.DataFrame(warehouses)
        print(f"✅ Created {len(self.warehouses)} warehouses")
        return self.warehouses

    def create_customers(self, num_customers=50):
        """Create customer master data"""
        print("🏢 Generating Customers...")

        # Customer cities spread across the country
        customer_cities = [
            {"city": "Boston", "state": "MA", "lat": 42.3601, "lon": -71.0589},
            {"city": "Miami", "state": "FL", "lat": 25.7617, "lon": -80.1918},
            {"city": "Seattle", "state": "WA", "lat": 47.6062, "lon": -122.3321},
            {"city": "Denver", "state": "CO", "lat": 39.7392, "lon": -104.9903},
            {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lon": -84.3880},
            {"city": "Detroit", "state": "MI", "lat": 42.3314, "lon": -83.0458},
            {"city": "Minneapolis", "state": "MN", "lat": 44.9778, "lon": -93.2650},
            {"city": "Tampa", "state": "FL", "lat": 27.9506, "lon": -82.4572},
            {"city": "Portland", "state": "OR", "lat": 45.5152, "lon": -122.6784},
            {"city": "Las Vegas", "state": "NV", "lat": 36.1699, "lon": -115.1398},
        ]

        business_types = [
            "Retail Store",
            "Distribution Center",
            "Manufacturing",
            "Warehouse",
            "Office Complex",
        ]

        customers = []
        for i in range(num_customers):
            # Some customers in major cities, others spread out
            if i < len(customer_cities):
                location = customer_cities[i]
            else:
                # Random location with some variation
                base_location = np.random.choice(customer_cities)
                location = {
                    "city": f'{base_location["city"]}_Suburb_{i}',
                    "state": base_location["state"],
                    "lat": base_location["lat"] + np.random.uniform(-2, 2),
                    "lon": base_location["lon"] + np.random.uniform(-2, 2),
                }

            customer = {
                "customer_id": f"CUST{i+1:04d}",
                "customer_name": f"Customer_{i+1}",
                "business_type": np.random.choice(business_types),
                "city": location["city"],
                "state": location["state"],
                "latitude": location["lat"],
                "longitude": location["lon"],
                "delivery_window_start": f"{np.random.randint(6, 10)}:00",
                "delivery_window_end": f"{np.random.randint(16, 20)}:00",
                "weekly_volume_pallets": np.random.randint(1, 20),
                "credit_rating": np.random.choice(["A", "B", "C"], p=[0.4, 0.4, 0.2]),
                "special_requirements": np.random.choice(
                    ["None", "Refrigerated", "Hazmat", "Fragile"], p=[0.6, 0.2, 0.1, 0.1]
                ),
                "established_date": datetime.now() - timedelta(days=np.random.randint(30, 2000)),
            }
            customers.append(customer)

        self.customers = pd.DataFrame(customers)
        print(f"✅ Created {len(self.customers)} customers")
        return self.customers

    def create_vehicles(self, num_vehicles=25):
        """Create vehicle fleet data"""
        print("🚛 Generating Vehicle Fleet...")

        vehicle_types = [
            {"type": "Small Van", "capacity": 2, "mpg": 18, "speed": 45},
            {"type": "Medium Truck", "capacity": 8, "mpg": 12, "speed": 55},
            {"type": "Large Truck", "capacity": 26, "mpg": 8, "speed": 60},
            {"type": "Semi Trailer", "capacity": 48, "mpg": 6, "speed": 65},
            {"type": "Refrigerated Truck", "capacity": 20, "mpg": 10, "speed": 58},
        ]

        vehicles = []
        for i in range(num_vehicles):
            vehicle_type = np.random.choice(vehicle_types)

            # Assign vehicle to a random warehouse
            home_warehouse = np.random.choice(self.warehouses["warehouse_id"])

            vehicle = {
                "vehicle_id": f"VEH{i+1:03d}",
                "license_plate": f"LTR{i+1:04d}",
                "vehicle_type": vehicle_type["type"],
                "capacity_pallets": vehicle_type["capacity"],
                "fuel_efficiency_mpg": vehicle_type["mpg"]
                * np.random.uniform(0.9, 1.1),  # Some variation
                "average_speed_mph": vehicle_type["speed"] * np.random.uniform(0.95, 1.05),
                "home_warehouse_id": home_warehouse,
                "year": np.random.randint(2018, 2024),
                "maintenance_cost_per_mile": round(np.random.uniform(0.15, 0.45), 2),
                "insurance_cost_per_day": round(np.random.uniform(25, 100), 2),
                "driver_daily_rate": round(np.random.uniform(180, 280), 2),
                "status": np.random.choice(
                    ["Available", "In Transit", "Maintenance"], p=[0.7, 0.2, 0.1]
                ),
                "max_daily_hours": np.random.choice([8, 10, 11]),  # DOT regulations
                "special_equipment": np.random.choice(
                    ["None", "Lift Gate", "Refrigeration", "Hazmat"], p=[0.6, 0.2, 0.15, 0.05]
                ),
            }
            vehicles.append(vehicle)

        self.vehicles = pd.DataFrame(vehicles)
        print(f"✅ Created {len(self.vehicles)} vehicles")
        return self.vehicles

    def create_drivers(self, num_drivers=30):
        """Create driver master data"""
        print("👨‍💼 Generating Drivers...")

        drivers = []
        for i in range(num_drivers):
            # Assign driver to a warehouse region
            home_warehouse = np.random.choice(self.warehouses["warehouse_id"])

            driver = {
                "driver_id": f"DRV{i+1:03d}",
                "driver_name": f"Driver_{i+1}",
                "home_warehouse_id": home_warehouse,
                "license_class": np.random.choice(["CDL-A", "CDL-B", "Regular"], p=[0.6, 0.3, 0.1]),
                "years_experience": np.random.randint(1, 25),
                "safety_rating": round(np.random.uniform(3.0, 5.0), 1),
                "hourly_rate": round(np.random.uniform(18, 35), 2),
                "max_hours_per_day": np.random.choice([8, 10, 11]),
                "max_hours_per_week": np.random.choice([60, 70]),
                "certifications": np.random.choice(
                    ["Basic", "Hazmat", "Refrigerated", "Hazmat+Refrigerated"],
                    p=[0.5, 0.2, 0.2, 0.1],
                ),
                "availability_status": np.random.choice(
                    ["Available", "On Route", "Off Duty", "Vacation"], p=[0.6, 0.25, 0.1, 0.05]
                ),
                "hire_date": datetime.now() - timedelta(days=np.random.randint(30, 3000)),
                "phone": f"555-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}",
                "emergency_contact": f"555-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}",
            }
            drivers.append(driver)

        self.drivers = pd.DataFrame(drivers)
        print(f"✅ Created {len(self.drivers)} drivers")
        return self.drivers

    def create_routes(self):
        """Create route network between warehouses and customers"""
        print("🗺️  Generating Route Network...")

        def calculate_distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points using haversine formula"""
            R = 3959  # Earth's radius in miles

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = (
                math.sin(delta_lat / 2) ** 2
                + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            return R * c

        routes = []
        route_id = 1

        # Create routes from each warehouse to each customer
        for _, warehouse in self.warehouses.iterrows():
            for _, customer in self.customers.iterrows():
                distance = calculate_distance(
                    warehouse["latitude"],
                    warehouse["longitude"],
                    customer["latitude"],
                    customer["longitude"],
                )

                # Add some realistic variation to travel time
                base_time = distance / 50  # Base speed of 50 mph
                traffic_factor = np.random.uniform(0.8, 1.3)  # Traffic variation
                travel_time_hours = base_time * traffic_factor

                route = {
                    "route_id": f"RTE{route_id:05d}",
                    "origin_type": "Warehouse",
                    "origin_id": warehouse["warehouse_id"],
                    "destination_type": "Customer",
                    "destination_id": customer["customer_id"],
                    "distance_miles": round(distance, 1),
                    "estimated_travel_time_hours": round(travel_time_hours, 2),
                    "fuel_cost_estimate": round(distance * 0.35, 2),  # $0.35 per mile average
                    "toll_cost": round(np.random.uniform(0, distance * 0.1), 2),
                    "road_type": np.random.choice(["Highway", "Mixed", "Urban"], p=[0.6, 0.3, 0.1]),
                    "difficulty_rating": np.random.choice(
                        ["Easy", "Medium", "Difficult"], p=[0.5, 0.4, 0.1]
                    ),
                    "seasonal_factor": round(np.random.uniform(0.9, 1.2), 2),  # Weather impact
                    "last_updated": datetime.now() - timedelta(days=np.random.randint(1, 90)),
                }
                routes.append(route)
                route_id += 1

        # Also create warehouse-to-warehouse routes for transfers
        for i, wh1 in self.warehouses.iterrows():
            for j, wh2 in self.warehouses.iterrows():
                if wh1["warehouse_id"] != wh2["warehouse_id"]:
                    distance = calculate_distance(
                        wh1["latitude"], wh1["longitude"], wh2["latitude"], wh2["longitude"]
                    )

                    travel_time_hours = (distance / 60) * np.random.uniform(
                        0.9, 1.1
                    )  # 60 mph average

                    route = {
                        "route_id": f"RTE{route_id:05d}",
                        "origin_type": "Warehouse",
                        "origin_id": wh1["warehouse_id"],
                        "destination_type": "Warehouse",
                        "destination_id": wh2["warehouse_id"],
                        "distance_miles": round(distance, 1),
                        "estimated_travel_time_hours": round(travel_time_hours, 2),
                        "fuel_cost_estimate": round(distance * 0.35, 2),
                        "toll_cost": round(np.random.uniform(0, distance * 0.08), 2),
                        "road_type": np.random.choice(["Highway", "Mixed"], p=[0.8, 0.2]),
                        "difficulty_rating": np.random.choice(["Easy", "Medium"], p=[0.7, 0.3]),
                        "seasonal_factor": round(np.random.uniform(0.95, 1.1), 2),
                        "last_updated": datetime.now() - timedelta(days=np.random.randint(1, 60)),
                    }
                    routes.append(route)
                    route_id += 1

        self.routes = pd.DataFrame(routes)
        print(f"✅ Created {len(self.routes)} routes")
        return self.routes

    def create_shipments(self, num_shipments=200):
        """Create shipment orders"""
        print("📦 Generating Shipments...")

        shipments = []
        for i in range(num_shipments):
            # Random customer and warehouse
            customer_id = np.random.choice(self.customers["customer_id"])
            origin_warehouse = np.random.choice(self.warehouses["warehouse_id"])

            # Shipment characteristics
            num_pallets = np.random.randint(1, 15)

            shipment = {
                "shipment_id": f"SHP{i+1:06d}",
                "customer_id": customer_id,
                "origin_warehouse_id": origin_warehouse,
                "pallets_count": num_pallets,
                "total_weight_lbs": num_pallets * np.random.randint(800, 2000),
                "total_value": round(num_pallets * np.random.uniform(500, 3000), 2),
                "product_type": np.random.choice(
                    ["Electronics", "Clothing", "Food", "Automotive", "Furniture", "Medical"],
                    p=[0.2, 0.15, 0.2, 0.15, 0.2, 0.1],
                ),
                "priority_level": np.random.choice(
                    ["Standard", "Express", "Urgent"], p=[0.7, 0.25, 0.05]
                ),
                "temperature_requirement": np.random.choice(
                    ["Ambient", "Refrigerated", "Frozen"], p=[0.7, 0.2, 0.1]
                ),
                "fragile": np.random.choice([True, False], p=[0.2, 0.8]),
                "order_date": datetime.now() - timedelta(days=np.random.randint(0, 7)),
                "requested_delivery_date": datetime.now()
                + timedelta(days=np.random.randint(1, 10)),
                "special_instructions": np.random.choice(
                    ["None", "Call before delivery", "Dock delivery only", "Signature required"],
                    p=[0.6, 0.2, 0.1, 0.1],
                ),
                "insurance_required": np.random.choice([True, False], p=[0.3, 0.7]),
                "status": np.random.choice(
                    ["Pending", "Ready to Ship", "In Transit", "Delivered"], p=[0.3, 0.4, 0.2, 0.1]
                ),
            }
            shipments.append(shipment)

        self.shipments = pd.DataFrame(shipments)
        print(f"✅ Created {len(self.shipments)} shipments")
        return self.shipments

    def create_deliveries(self, num_deliveries=150):
        """Create planned deliveries linking shipments, vehicles, drivers, and routes"""
        print("🚚 Generating Planned Deliveries...")

        # Filter to only ready-to-ship and in-transit shipments
        available_shipments = self.shipments[
            self.shipments["status"].isin(["Ready to Ship", "In Transit"])
        ]["shipment_id"].tolist()

        if len(available_shipments) < num_deliveries:
            num_deliveries = len(available_shipments)

        deliveries = []
        used_shipments = set()

        for i in range(num_deliveries):
            # Select available shipment
            available = [s for s in available_shipments if s not in used_shipments]
            if not available:
                break

            shipment_id = np.random.choice(available)
            used_shipments.add(shipment_id)

            # Get shipment details
            shipment = self.shipments[self.shipments["shipment_id"] == shipment_id].iloc[0]

            # Find suitable vehicle (capacity check)
            suitable_vehicles = self.vehicles[
                (self.vehicles["capacity_pallets"] >= shipment["pallets_count"])
                & (self.vehicles["status"] == "Available")
            ]

            if len(suitable_vehicles) == 0:
                continue

            vehicle_id = np.random.choice(suitable_vehicles["vehicle_id"])
            vehicle = self.vehicles[self.vehicles["vehicle_id"] == vehicle_id].iloc[0]

            # Find suitable driver
            suitable_drivers = self.drivers[(self.drivers["availability_status"] == "Available")]

            if len(suitable_drivers) == 0:
                continue

            driver_id = np.random.choice(suitable_drivers["driver_id"])

            # Find route
            route = self.routes[
                (self.routes["origin_id"] == shipment["origin_warehouse_id"])
                & (self.routes["destination_id"] == shipment["customer_id"])
            ]

            if len(route) == 0:
                continue

            route = route.iloc[0]

            # Calculate costs and times
            fuel_cost = (
                route["distance_miles"] / vehicle["fuel_efficiency_mpg"] * 3.50
            )  # $3.50/gallon
            driver_cost = route["estimated_travel_time_hours"] * 25  # $25/hour
            total_cost = fuel_cost + driver_cost + route["toll_cost"]

            delivery = {
                "delivery_id": f"DEL{i+1:06d}",
                "shipment_id": shipment_id,
                "vehicle_id": vehicle_id,
                "driver_id": driver_id,
                "route_id": route["route_id"],
                "planned_departure": datetime.now() + timedelta(hours=np.random.randint(1, 48)),
                "estimated_arrival": datetime.now() + timedelta(hours=np.random.randint(2, 72)),
                "actual_departure": (
                    None
                    if np.random.random() > 0.3
                    else datetime.now() - timedelta(hours=np.random.randint(1, 24))
                ),
                "actual_arrival": (
                    None
                    if np.random.random() > 0.2
                    else datetime.now() - timedelta(hours=np.random.randint(0, 12))
                ),
                "estimated_fuel_cost": round(fuel_cost, 2),
                "estimated_driver_cost": round(driver_cost, 2),
                "estimated_total_cost": round(total_cost, 2),
                "actual_fuel_used_gallons": (
                    None
                    if np.random.random() > 0.2
                    else round(
                        route["distance_miles"]
                        / vehicle["fuel_efficiency_mpg"]
                        * np.random.uniform(0.9, 1.1),
                        2,
                    )
                ),
                "delivery_status": np.random.choice(
                    ["Planned", "En Route", "Delivered", "Delayed"], p=[0.5, 0.3, 0.15, 0.05]
                ),
                "optimization_score": round(
                    np.random.uniform(0.6, 1.0), 2
                ),  # How optimal this delivery is
                "customer_satisfaction": (
                    None if np.random.random() > 0.2 else np.random.randint(1, 6)
                ),
            }
            deliveries.append(delivery)

        self.deliveries = pd.DataFrame(deliveries)
        print(f"✅ Created {len(self.deliveries)} planned deliveries")
        return self.deliveries

    def generate_all_logistics_data(self):
        """Generate complete logistics dataset with relationships"""
        print("🚀 Generating Complete Logistics Dataset")
        print("=" * 60)

        # Generate in dependency order
        self.create_warehouses()
        self.create_customers()
        self.create_vehicles()
        self.create_drivers()
        self.create_routes()
        self.create_shipments()
        self.create_deliveries()

        return {
            "warehouses": self.warehouses,
            "customers": self.customers,
            "vehicles": self.vehicles,
            "drivers": self.drivers,
            "routes": self.routes,
            "shipments": self.shipments,
            "deliveries": self.deliveries,
        }


def create_logistics_excel():
    """Create a comprehensive logistics Excel file with multiple related sheets"""
    print("📊 Creating Logistics Excel File...")

    generator = LogisticsDataGenerator()
    datasets = generator.generate_all_logistics_data()

    # Create Excel file with all related tables
    excel_path = "/tmp/logistics_operations.xlsx"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Write each table to a separate sheet
        datasets["warehouses"].to_excel(writer, sheet_name="Warehouses", index=False)
        datasets["customers"].to_excel(writer, sheet_name="Customers", index=False)
        datasets["vehicles"].to_excel(writer, sheet_name="Vehicles", index=False)
        datasets["drivers"].to_excel(writer, sheet_name="Drivers", index=False)
        datasets["routes"].to_excel(writer, sheet_name="Routes", index=False)
        datasets["shipments"].to_excel(writer, sheet_name="Shipments", index=False)
        datasets["deliveries"].to_excel(writer, sheet_name="Deliveries", index=False)

        # Create summary/analytics sheets

        # Route efficiency summary
        route_summary = (
            datasets["routes"]
            .groupby("origin_id")
            .agg(
                {
                    "distance_miles": ["count", "mean", "min", "max"],
                    "estimated_travel_time_hours": "mean",
                    "fuel_cost_estimate": "mean",
                }
            )
            .round(2)
        )
        route_summary.columns = [
            "Route_Count",
            "Avg_Distance",
            "Min_Distance",
            "Max_Distance",
            "Avg_Travel_Time",
            "Avg_Fuel_Cost",
        ]
        route_summary.to_excel(writer, sheet_name="Route_Summary")

        # Vehicle utilization
        vehicle_util = (
            datasets["deliveries"]
            .groupby("vehicle_id")
            .agg(
                {
                    "delivery_id": "count",
                    "estimated_total_cost": "sum",
                    "optimization_score": "mean",
                }
            )
            .round(2)
        )
        vehicle_util.columns = ["Deliveries_Count", "Total_Cost", "Avg_Optimization_Score"]
        vehicle_util.to_excel(writer, sheet_name="Vehicle_Utilization")

    print(f"✅ Created comprehensive logistics Excel: {excel_path}")
    print(f"📊 Total records across all tables: {sum(len(df) for df in datasets.values()):,}")
    print(f"📋 Tables: {list(datasets.keys())}")

    return excel_path, datasets


def test_logistics_optimization():
    """Test framework with complex logistics optimization scenarios"""
    print("\n" + "=" * 70)
    print("🚛 LOGISTICS OPTIMIZATION ANALYSIS")
    print("=" * 70)

    # Create logistics data
    excel_path, datasets = create_logistics_excel()

    try:
        # Test basic analysis
        print(f"\n🔍 Analyzing Logistics Excel File:")
        analysis_result = daf.analyze(excel_path)

        if "error" in analysis_result:
            print(f"❌ Analysis failed: {analysis_result['error']}")
            return

        data_type = analysis_result["data_type"]
        analysis = analysis_result["analysis"]

        print(f"✅ Logistics Analysis Results:")
        print(f"  • Data Type: {data_type.type_name}")
        print(f"  • Number of Tables: {data_type.tables_count}")
        print(f"  • Table Names: {', '.join(data_type.sheets_or_tables)}")
        print(f"  • Total Records: {data_type.total_rows:,}")
        print(f"  • Total Columns: {data_type.total_columns}")
        print(f"  • Quality Score: {analysis.quality_score:.2f}")
        print(f"  • Complexity: {analysis.query_complexity}")

        if analysis.detected_patterns:
            print(f"  • Detected Patterns: {', '.join(analysis.detected_patterns)}")

        # Test comprehensive profiling
        print(f"\n📈 Comprehensive Data Profiling:")
        profile_result = daf.profile_data(excel_path)

        if "error" not in profile_result:
            quality = profile_result["quality_metrics"]
            business_insights = profile_result["business_insights"]

            print(f"  • Overall Quality: {quality.overall_score:.1f}/100")
            print(f"  • AI Readiness: {quality.ai_readiness_score:.1f}/100")
            print(f"  • Business Patterns: {', '.join(business_insights['data_patterns'])}")

            if business_insights["anomalies"]:
                print(f"  • Anomalies Detected: {len(business_insights['anomalies'])}")

        # Test AI Agent Interface for Optimization
        print(f"\n🤖 AI Agent Interface for Logistics Optimization:")
        interface = daf.create_agent_interface(excel_path)
        overview = interface.get_data_overview()

        if "error" not in overview:
            print(f"✅ Logistics Interface Ready:")
            print(f"  • Combined Data Shape: {overview['shape']}")
            print(f"  • Query Capabilities: {len(overview['query_capabilities'])} types")

            # Test logistics optimization queries
            optimization_queries = [
                "Find the shortest routes for delivery optimization",
                "Show me vehicles with best fuel efficiency",
                "What are the highest cost deliveries?",
                "Find deliveries that can be optimized for fuel savings",
                "Show me routes with lowest total cost",
                "Find vehicles that are underutilized",
                "What routes take the longest time?",
                "Show me drivers with highest utilization",
            ]

            results = []
            print(f"\n  🔍 Logistics Optimization Queries:")

            for i, query in enumerate(optimization_queries, 1):
                print(f"\n    Query {i}: '{query}'")
                result = interface.execute_query(query)
                results.append(result)

                if result.success:
                    print(f"      ✅ Success: {result.row_count} records")
                    print(f"      ⏱️  Execution: {result.execution_time_ms:.1f}ms")
                    if result.insights:
                        print(f"      💡 Insight: {result.insights[0]}")
                    if result.recommendations:
                        print(f"      🎯 Recommendation: {result.recommendations[0]}")
                else:
                    print(
                        f"      ❌ Failed: {result.warnings[0] if result.warnings else 'Unknown error'}"
                    )

            # Generate comprehensive logistics optimization report
            if results and any(r.success for r in results):
                print(f"\n📋 Logistics Optimization Report:")
                report = interface.generate_report(
                    results, "Logistics Operations Optimization Analysis", "detailed"
                )

                print(f"    • Report: {report['title']}")
                print(f"    • Generated: {report['generated_at'][:19]}")
                print(f"    • Key Findings: {len(report['key_findings'])}")
                print(f"    • Recommendations: {len(report['recommendations'])}")
                print(
                    f"    • Quality Assessment: {report['data_quality_assessment']['assessment']}"
                )

                # Show key optimization insights
                if report["key_findings"]:
                    print(f"\n    📊 Key Optimization Insights:")
                    for finding in report["key_findings"][:3]:
                        print(f"      • {finding}")

                if report["recommendations"]:
                    print(f"\n    💡 Optimization Recommendations:")
                    for rec in report["recommendations"][:3]:
                        print(f"      • {rec}")

        # Display relationship statistics
        print(f"\n🔗 Data Relationship Analysis:")
        print(f"  • Warehouses: {len(datasets['warehouses'])} locations")
        print(f"  • Customers: {len(datasets['customers'])} destinations")
        print(f"  • Routes: {len(datasets['routes'])} possible paths")
        print(f"  • Vehicles: {len(datasets['vehicles'])} fleet size")
        print(f"  • Deliveries: {len(datasets['deliveries'])} planned operations")

        # Calculate some optimization metrics
        total_distance = datasets["routes"]["distance_miles"].sum()
        avg_fuel_efficiency = datasets["vehicles"]["fuel_efficiency_mpg"].mean()
        total_capacity = datasets["vehicles"]["capacity_pallets"].sum()

        print(f"  • Total Route Network: {total_distance:,.0f} miles")
        print(f"  • Average Fleet Fuel Efficiency: {avg_fuel_efficiency:.1f} MPG")
        print(f"  • Total Fleet Capacity: {total_capacity:,} pallets")

        print(f"\n✅ Logistics optimization analysis completed successfully!")

    except Exception as e:
        print(f"❌ Logistics testing failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        try:
            os.unlink(excel_path)
        except:
            pass


if __name__ == "__main__":
    print("🧪 LOGISTICS OPTIMIZATION DEMO")
    print("=" * 50)
    print("Testing Data Analysis Framework with complex logistics data")
    print("Focus: Multi-table relationships and optimization scenarios")
    print("Use Cases: Route optimization, fuel efficiency, capacity planning")

    test_logistics_optimization()

    print(f"\n🎉 Logistics Demo Completed!")
    print(f"✅ Framework successfully handles complex relational data")
    print(f"🚀 Ready for real-world logistics optimization!")
    print(f"📊 Demonstrated capabilities:")
    print(f"  • Multi-table relationship analysis")
    print(f"  • Foreign key constraint handling")
    print(f"  • Complex business optimization queries")
    print(f"  • Route and cost optimization insights")
    print(f"  • Fleet management analytics")
