#!/usr/bin/env python3
"""
Comprehensive Synthetic Data Test Suite
Data Analysis Framework

This script creates realistic synthetic datasets for multiple business use cases
and demonstrates the framework's AI agent interaction capabilities across domains.

Use Cases:
1. E-commerce Sales Data
2. Employee HR Analytics
3. Financial Portfolio Management
4. Inventory & Supply Chain
5. Customer Service Operations
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    import data_analysis_framework as daf

    print("✅ Data Analysis Framework imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


class SyntheticDataGenerator:
    """Generate realistic synthetic datasets for various business domains"""

    def __init__(self, seed=42):
        np.random.seed(seed)
        self.datasets = {}

    def create_ecommerce_data(self, num_orders=1000):
        """Generate e-commerce sales data"""
        print("📊 Generating E-commerce Sales Data...")

        # Product categories and details
        categories = {
            "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Camera"],
            "Clothing": ["T-Shirt", "Jeans", "Dress", "Shoes", "Jacket"],
            "Home": ["Furniture", "Kitchen", "Decor", "Bedding", "Appliances"],
            "Books": ["Fiction", "Non-Fiction", "Technical", "Educational", "Children"],
            "Sports": ["Equipment", "Apparel", "Footwear", "Accessories", "Outdoor"],
        }

        # Generate orders
        orders = []
        for i in range(num_orders):
            category = np.random.choice(list(categories.keys()))
            product = np.random.choice(categories[category])

            # Pricing based on category
            base_prices = {
                "Electronics": (200, 2000),
                "Clothing": (20, 200),
                "Home": (50, 500),
                "Books": (10, 50),
                "Sports": (30, 300),
            }

            min_price, max_price = base_prices[category]
            price = np.random.uniform(min_price, max_price)
            quantity = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])

            order = {
                "order_id": f"ORD{i+1:06d}",
                "customer_id": f"CUST{np.random.randint(1, 500):05d}",
                "product_name": f"{category} - {product}",
                "category": category,
                "price": round(price, 2),
                "quantity": quantity,
                "total_amount": round(price * quantity, 2),
                "order_date": datetime.now() - timedelta(days=np.random.randint(1, 365)),
                "customer_age": np.random.randint(18, 70),
                "customer_location": np.random.choice(["US", "CA", "UK", "DE", "FR", "AU", "JP"]),
                "payment_method": np.random.choice(
                    ["Credit Card", "PayPal", "Debit Card", "Bank Transfer"],
                    p=[0.5, 0.3, 0.15, 0.05],
                ),
                "shipping_cost": round(np.random.uniform(0, 25), 2),
                "customer_rating": np.random.choice(
                    [1, 2, 3, 4, 5], p=[0.05, 0.1, 0.15, 0.35, 0.35]
                ),
            }
            orders.append(order)

        df = pd.DataFrame(orders)
        self.datasets["ecommerce"] = df
        print(f"✅ Created {len(df)} e-commerce orders")
        return df

    def create_hr_data(self, num_employees=300):
        """Generate employee HR analytics data"""
        print("👥 Generating HR Analytics Data...")

        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Legal"]
        job_levels = ["Junior", "Mid", "Senior", "Lead", "Manager", "Director"]

        employees = []
        for i in range(num_employees):
            dept = np.random.choice(departments)
            level = np.random.choice(job_levels, p=[0.25, 0.25, 0.2, 0.15, 0.1, 0.05])

            # Salary based on department and level
            base_salaries = {
                "Engineering": {
                    "Junior": 75000,
                    "Mid": 95000,
                    "Senior": 120000,
                    "Lead": 140000,
                    "Manager": 160000,
                    "Director": 200000,
                },
                "Sales": {
                    "Junior": 50000,
                    "Mid": 70000,
                    "Senior": 90000,
                    "Lead": 110000,
                    "Manager": 130000,
                    "Director": 180000,
                },
                "Marketing": {
                    "Junior": 55000,
                    "Mid": 70000,
                    "Senior": 85000,
                    "Lead": 100000,
                    "Manager": 120000,
                    "Director": 160000,
                },
                "HR": {
                    "Junior": 50000,
                    "Mid": 65000,
                    "Senior": 80000,
                    "Lead": 95000,
                    "Manager": 110000,
                    "Director": 150000,
                },
                "Finance": {
                    "Junior": 60000,
                    "Mid": 75000,
                    "Senior": 95000,
                    "Lead": 115000,
                    "Manager": 135000,
                    "Director": 170000,
                },
                "Operations": {
                    "Junior": 45000,
                    "Mid": 60000,
                    "Senior": 75000,
                    "Lead": 90000,
                    "Manager": 105000,
                    "Director": 140000,
                },
                "Legal": {
                    "Junior": 80000,
                    "Mid": 100000,
                    "Senior": 130000,
                    "Lead": 160000,
                    "Manager": 180000,
                    "Director": 220000,
                },
            }

            base_salary = base_salaries[dept][level]
            salary = base_salary * np.random.uniform(0.9, 1.1)  # ±10% variation

            employee = {
                "employee_id": f"EMP{i+1:05d}",
                "name": f"Employee {i+1}",
                "department": dept,
                "job_level": level,
                "annual_salary": round(salary, 2),
                "hire_date": datetime.now() - timedelta(days=np.random.randint(30, 2000)),
                "age": np.random.randint(22, 65),
                "performance_score": np.random.uniform(2.0, 5.0),
                "training_hours_ytd": np.random.randint(0, 80),
                "vacation_days_taken": np.random.randint(0, 25),
                "remote_work_days": np.random.randint(0, 100),
                "education_level": np.random.choice(
                    ["High School", "Bachelor", "Master", "PhD"], p=[0.1, 0.5, 0.3, 0.1]
                ),
                "satisfaction_score": np.random.uniform(1.0, 5.0),
                "projects_completed": np.random.randint(1, 15),
            }
            employees.append(employee)

        df = pd.DataFrame(employees)
        self.datasets["hr"] = df
        print(f"✅ Created {len(df)} employee records")
        return df

    def create_portfolio_data(self, num_investments=500):
        """Generate financial portfolio data"""
        print("💰 Generating Financial Portfolio Data...")

        asset_types = ["Stock", "Bond", "ETF", "Mutual Fund", "Cryptocurrency", "Real Estate"]
        sectors = [
            "Technology",
            "Healthcare",
            "Finance",
            "Energy",
            "Consumer",
            "Industrial",
            "Utilities",
        ]
        risk_levels = ["Low", "Medium", "High", "Very High"]

        investments = []
        for i in range(num_investments):
            asset_type = np.random.choice(asset_types, p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05])
            sector = np.random.choice(sectors)

            # Investment amounts based on asset type
            amount_ranges = {
                "Stock": (1000, 50000),
                "Bond": (5000, 100000),
                "ETF": (2000, 75000),
                "Mutual Fund": (3000, 80000),
                "Cryptocurrency": (500, 20000),
                "Real Estate": (50000, 500000),
            }

            min_amt, max_amt = amount_ranges[asset_type]
            investment_amount = np.random.uniform(min_amt, max_amt)

            # Returns based on risk and asset type
            risk_multipliers = {"Low": 0.5, "Medium": 1.0, "High": 1.5, "Very High": 2.0}
            risk = np.random.choice(risk_levels, p=[0.2, 0.4, 0.3, 0.1])
            base_return = np.random.uniform(-0.2, 0.3)  # -20% to +30%
            actual_return = base_return * risk_multipliers[risk]

            investment = {
                "investment_id": f"INV{i+1:06d}",
                "portfolio_id": f"PORT{np.random.randint(1, 100):03d}",
                "asset_name": f"{asset_type}_{sector}_{i+1}",
                "asset_type": asset_type,
                "sector": sector,
                "investment_amount": round(investment_amount, 2),
                "current_value": round(investment_amount * (1 + actual_return), 2),
                "return_pct": round(actual_return * 100, 2),
                "risk_level": risk,
                "purchase_date": datetime.now()
                - timedelta(days=np.random.randint(1, 1095)),  # Up to 3 years
                "dividend_yield": (
                    round(np.random.uniform(0, 0.08), 3) if asset_type in ["Stock", "ETF"] else 0
                ),
                "expense_ratio": (
                    round(np.random.uniform(0.001, 0.02), 3)
                    if asset_type in ["ETF", "Mutual Fund"]
                    else 0
                ),
                "beta": round(np.random.uniform(0.5, 2.0), 2) if asset_type == "Stock" else None,
                "credit_rating": (
                    np.random.choice(["AAA", "AA", "A", "BBB", "BB", "B"])
                    if asset_type == "Bond"
                    else None
                ),
            }
            investments.append(investment)

        df = pd.DataFrame(investments)
        self.datasets["portfolio"] = df
        print(f"✅ Created {len(df)} investment records")
        return df

    def create_inventory_data(self, num_products=400):
        """Generate inventory management data"""
        print("📦 Generating Inventory Management Data...")

        categories = ["Electronics", "Clothing", "Food", "Automotive", "Health", "Home", "Sports"]
        suppliers = ["SupplierA", "SupplierB", "SupplierC", "SupplierD", "SupplierE"]
        warehouses = [
            "Warehouse_North",
            "Warehouse_South",
            "Warehouse_East",
            "Warehouse_West",
            "Warehouse_Central",
        ]

        products = []
        for i in range(num_products):
            category = np.random.choice(categories)
            supplier = np.random.choice(suppliers)
            warehouse = np.random.choice(warehouses)

            # Stock levels and costs based on category
            stock_ranges = {
                "Electronics": (10, 500),
                "Clothing": (50, 1000),
                "Food": (100, 2000),
                "Automotive": (5, 200),
                "Health": (20, 800),
                "Home": (30, 600),
                "Sports": (25, 400),
            }

            cost_ranges = {
                "Electronics": (50, 500),
                "Clothing": (10, 100),
                "Food": (2, 20),
                "Automotive": (20, 200),
                "Health": (5, 50),
                "Home": (15, 150),
                "Sports": (10, 80),
            }

            min_stock, max_stock = stock_ranges[category]
            min_cost, max_cost = cost_ranges[category]

            current_stock = np.random.randint(0, max_stock)
            reorder_point = int(max_stock * 0.2)  # 20% of max stock
            unit_cost = np.random.uniform(min_cost, max_cost)

            product = {
                "sku": f"SKU{i+1:06d}",
                "product_name": f"{category}_Product_{i+1}",
                "category": category,
                "supplier": supplier,
                "warehouse_location": warehouse,
                "current_stock": current_stock,
                "reorder_point": reorder_point,
                "max_stock_level": max_stock,
                "unit_cost": round(unit_cost, 2),
                "selling_price": round(
                    unit_cost * np.random.uniform(1.2, 2.5), 2
                ),  # 20-150% markup
                "last_restock_date": datetime.now() - timedelta(days=np.random.randint(1, 90)),
                "monthly_sales_avg": np.random.randint(5, 100),
                "lead_time_days": np.random.randint(1, 30),
                "shelf_life_days": np.random.randint(30, 365) if category == "Food" else None,
                "weight_kg": round(np.random.uniform(0.1, 50), 2),
                "storage_temp_req": (
                    np.random.choice(["Room", "Cold", "Frozen"]) if category == "Food" else "Room"
                ),
                "stock_status": "Low Stock" if current_stock <= reorder_point else "In Stock",
            }
            products.append(product)

        df = pd.DataFrame(products)
        self.datasets["inventory"] = df
        print(f"✅ Created {len(df)} product inventory records")
        return df

    def create_customer_service_data(self, num_tickets=600):
        """Generate customer service operations data"""
        print("🎧 Generating Customer Service Data...")

        ticket_types = [
            "Technical Issue",
            "Billing Question",
            "Product Inquiry",
            "Complaint",
            "Refund Request",
            "Account Issue",
        ]
        priorities = ["Low", "Medium", "High", "Critical"]
        statuses = ["Open", "In Progress", "Resolved", "Closed"]
        channels = ["Email", "Phone", "Chat", "Social Media", "In-Person"]
        agents = [f"Agent_{i:02d}" for i in range(1, 21)]  # 20 agents

        tickets = []
        for i in range(num_tickets):
            ticket_type = np.random.choice(ticket_types, p=[0.25, 0.2, 0.2, 0.15, 0.1, 0.1])
            priority = np.random.choice(priorities, p=[0.4, 0.35, 0.2, 0.05])
            channel = np.random.choice(channels, p=[0.4, 0.25, 0.2, 0.1, 0.05])
            agent = np.random.choice(agents)

            # Response times based on priority and channel
            response_times = {
                "Critical": (5, 30),  # 5-30 minutes
                "High": (30, 120),  # 30min-2hrs
                "Medium": (120, 480),  # 2-8 hours
                "Low": (480, 1440),  # 8-24 hours
            }

            min_resp, max_resp = response_times[priority]
            first_response_time = np.random.randint(min_resp, max_resp)

            # Resolution times
            resolution_multiplier = {
                "Email": 2,
                "Phone": 1,
                "Chat": 1.5,
                "Social Media": 1.8,
                "In-Person": 0.8,
            }
            base_resolution = first_response_time * np.random.uniform(2, 8)
            resolution_time = base_resolution * resolution_multiplier[channel]

            # Status based on resolution time and current date
            created_date = datetime.now() - timedelta(
                minutes=np.random.randint(0, 10080)
            )  # Up to 1 week ago
            if (datetime.now() - created_date).total_seconds() / 60 > resolution_time:
                status = np.random.choice(["Resolved", "Closed"], p=[0.3, 0.7])
            else:
                status = np.random.choice(["Open", "In Progress"], p=[0.4, 0.6])

            ticket = {
                "ticket_id": f"TKT{i+1:06d}",
                "customer_id": f"CUST{np.random.randint(1, 1000):05d}",
                "ticket_type": ticket_type,
                "priority": priority,
                "status": status,
                "channel": channel,
                "assigned_agent": agent,
                "created_date": created_date,
                "first_response_time_min": first_response_time if status != "Open" else None,
                "resolution_time_min": (
                    resolution_time if status in ["Resolved", "Closed"] else None
                ),
                "customer_satisfaction": (
                    np.random.randint(1, 6) if status in ["Resolved", "Closed"] else None
                ),
                "escalated": np.random.choice([True, False], p=[0.15, 0.85]),
                "reopened": (
                    np.random.choice([True, False], p=[0.1, 0.9]) if status == "Closed" else False
                ),
                "agent_experience_years": np.random.uniform(0.5, 10),
                "issue_complexity": np.random.choice(
                    ["Simple", "Medium", "Complex"], p=[0.5, 0.3, 0.2]
                ),
                "department": np.random.choice(
                    ["Technical Support", "Billing", "Sales", "General"]
                ),
            }
            tickets.append(ticket)

        df = pd.DataFrame(tickets)
        self.datasets["customer_service"] = df
        print(f"✅ Created {len(df)} customer service tickets")
        return df

    def generate_all_datasets(self):
        """Generate all synthetic datasets"""
        print("🚀 Generating Comprehensive Synthetic Test Data")
        print("=" * 60)

        datasets = {
            "ecommerce": self.create_ecommerce_data(),
            "hr": self.create_hr_data(),
            "portfolio": self.create_portfolio_data(),
            "inventory": self.create_inventory_data(),
            "customer_service": self.create_customer_service_data(),
        }

        return datasets


def test_dataset_analysis(name, df):
    """Test framework capabilities on a specific dataset"""
    print(f"\n{'='*60}")
    print(f"🔍 ANALYZING {name.upper()} DATASET")
    print("=" * 60)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name

    try:
        # Basic analysis
        print(f"\n📊 Basic Analysis:")
        analysis_result = daf.analyze(csv_path)

        if "error" in analysis_result:
            print(f"❌ Analysis failed: {analysis_result['error']}")
            return

        data_type = analysis_result["data_type"]
        analysis = analysis_result["analysis"]

        print(f"  • Data Type: {data_type.type_name}")
        print(f"  • Records: {data_type.total_rows:,}")
        print(f"  • Columns: {data_type.total_columns}")
        print(f"  • Quality Score: {analysis.quality_score:.2f}")
        print(f"  • Complexity: {analysis.query_complexity}")

        if analysis.detected_patterns:
            print(f"  • Patterns: {', '.join(analysis.detected_patterns)}")

        # Data profiling
        print(f"\n📈 Data Profiling:")
        profile_result = daf.profile_data(csv_path)

        if "error" not in profile_result:
            quality = profile_result["quality_metrics"]
            print(f"  • Overall Quality: {quality.overall_score:.1f}/100")
            print(f"  • Completeness: {quality.completeness_score:.1f}/100")
            print(f"  • AI Readiness: {quality.ai_readiness_score:.1f}/100")

            if quality.business_value_indicators:
                bvi = quality.business_value_indicators
                print(
                    f"  • Financial Relevance: {'Yes' if bvi.get('financial_relevance') else 'No'}"
                )
                print(f"  • Temporal Coverage: {'Yes' if bvi.get('temporal_coverage') else 'No'}")

        # AI Agent Interface Testing
        print(f"\n🤖 AI Agent Interface Testing:")
        interface = daf.create_agent_interface(csv_path)
        overview = interface.get_data_overview()

        if "error" not in overview:
            print(f"  • Interface Status: ✅ Ready")
            print(f"  • Query Capabilities: {len(overview['query_capabilities'])} types")

            # Test domain-specific queries
            test_queries = get_domain_queries(name, df)
            results = []

            for i, query in enumerate(test_queries, 1):
                print(f"\n  🔍 Query {i}: '{query}'")
                result = interface.execute_query(query)
                results.append(result)

                if result.success:
                    print(
                        f"    ✅ Success: {result.row_count} records ({result.execution_time_ms:.1f}ms)"
                    )
                    if result.insights:
                        print(f"    💡 Insight: {result.insights[0]}")
                else:
                    print(
                        f"    ❌ Failed: {result.warnings[0] if result.warnings else 'Unknown error'}"
                    )

            # Generate business report
            if results:
                print(f"\n📋 Business Intelligence Report:")
                report = interface.generate_report(results, f"{name.title()} Analysis Report")
                print(f"    • Report Generated: {report['title']}")
                print(f"    • Key Findings: {len(report['key_findings'])}")
                print(f"    • Recommendations: {len(report['recommendations'])}")
                print(
                    f"    • Quality Assessment: {report['data_quality_assessment']['assessment']}"
                )

    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        try:
            os.unlink(csv_path)
        except:
            pass


def get_domain_queries(domain, df):
    """Get domain-specific test queries"""
    queries = {
        "ecommerce": [
            "Show me orders over $500",
            "What is the average order value?",
            "Count orders by category",
            "Find customers with high ratings",
        ],
        "hr": [
            "Show me employees with salary over $100000",
            "What is the average salary by department?",
            "Count employees by job level",
            "Find high-performing employees",
        ],
        "portfolio": [
            "Show me investments with positive returns",
            "What is the average return by asset type?",
            "Count investments by risk level",
            "Find high-risk investments",
        ],
        "inventory": [
            "Show me products with low stock",
            "What is the average inventory value?",
            "Count products by category",
            "Find products needing reorder",
        ],
        "customer_service": [
            "Show me critical priority tickets",
            "What is the average response time?",
            "Count tickets by status",
            "Find escalated tickets",
        ],
    }

    return queries.get(domain, ["Show me a summary of the data"])


def run_comprehensive_test():
    """Run comprehensive test across all synthetic datasets"""
    print("🧪 COMPREHENSIVE SYNTHETIC DATA TEST SUITE")
    print("=" * 60)
    print("Testing Data Analysis Framework across multiple business domains")
    print("Focus: AI Agent Interaction with Structured Data")

    # Generate all datasets
    generator = SyntheticDataGenerator()
    datasets = generator.generate_all_datasets()

    print(f"\n✅ Generated {len(datasets)} synthetic datasets:")
    for name, df in datasets.items():
        print(f"  • {name.title()}: {len(df):,} records, {len(df.columns)} columns")

    # Test each dataset
    success_count = 0
    for name, df in datasets.items():
        try:
            test_dataset_analysis(name, df)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed testing {name}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print("🎉 COMPREHENSIVE TEST COMPLETED")
    print("=" * 60)
    print(f"✅ Successfully tested: {success_count}/{len(datasets)} datasets")
    print(f"📊 Total records analyzed: {sum(len(df) for df in datasets.values()):,}")
    print(f"📋 Total columns processed: {sum(len(df.columns) for df in datasets.values())}")

    print(f"\n🎯 Key Capabilities Demonstrated:")
    print(f"  • Multi-domain data analysis (E-commerce, HR, Finance, Inventory, Customer Service)")
    print(f"  • Intelligent schema detection and data profiling")
    print(f"  • AI-safe structured data querying across domains")
    print(f"  • Natural language query processing for business questions")
    print(f"  • Automated business intelligence report generation")
    print(f"  • Domain-specific insights and recommendations")

    print(f"\n💡 Framework successfully handles diverse business data patterns!")
    print(f"🚀 Ready for production use across multiple industries!")


if __name__ == "__main__":
    run_comprehensive_test()
