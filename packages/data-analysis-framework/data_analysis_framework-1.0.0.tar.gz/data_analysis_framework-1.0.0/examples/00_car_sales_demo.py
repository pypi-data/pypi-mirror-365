#!/usr/bin/env python3
"""
Car Sales Demo - Data Analysis Framework

This demo shows how AI agents can safely interact with structured data
using the data-analysis-framework. It demonstrates the key differentiator:
instead of chunking documents, we provide intelligent APIs for querying data.

Use Case: Car sales database where agents can filter by budget and criteria,
then generate business intelligence reports with recommendations.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    import data_analysis_framework as daf

    print("✅ Successfully imported data_analysis_framework")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("💡 Make sure you're running from the data-analysis-framework directory")
    sys.exit(1)


def create_sample_car_data():
    """Create sample car sales data for demonstration"""
    np.random.seed(42)  # For reproducible data

    # Car data
    makes = [
        "Toyota",
        "Honda",
        "Ford",
        "Chevrolet",
        "Nissan",
        "BMW",
        "Mercedes",
        "Audi",
        "Hyundai",
        "Kia",
    ]
    models = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Prius", "Highlander"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Insight"],
        "Ford": ["Focus", "Mustang", "F-150", "Explorer", "Escape"],
        "Chevrolet": ["Cruze", "Malibu", "Tahoe", "Equinox", "Silverado"],
        "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Leaf"],
        "BMW": ["3 Series", "5 Series", "X3", "X5", "i3"],
        "Mercedes": ["C-Class", "E-Class", "GLC", "GLE", "EQC"],
        "Audi": ["A4", "A6", "Q5", "Q7", "e-tron"],
        "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Ioniq"],
        "Kia": ["Forte", "Optima", "Sorento", "Sportage", "Niro"],
    }
    conditions = ["Excellent", "Good", "Fair", "Poor"]
    colors = ["White", "Black", "Silver", "Red", "Blue", "Gray", "Green", "Yellow"]
    fuel_types = ["Gasoline", "Hybrid", "Electric", "Diesel"]

    # Generate 500 car records
    num_cars = 500
    data = []

    for i in range(num_cars):
        make = np.random.choice(makes)
        model = np.random.choice(models[make])
        year = np.random.randint(2010, 2024)

        # Price based on make, model, year, and condition
        base_price = {
            "BMW": 45000,
            "Mercedes": 50000,
            "Audi": 42000,
            "Toyota": 25000,
            "Honda": 24000,
            "Nissan": 23000,
            "Ford": 28000,
            "Chevrolet": 27000,
            "Hyundai": 22000,
            "Kia": 21000,
        }[make]

        # Adjust for year (depreciation)
        age = 2024 - year
        price = base_price * (0.95**age)  # 5% depreciation per year

        # Adjust for condition
        condition = np.random.choice(conditions, p=[0.3, 0.4, 0.2, 0.1])
        condition_multiplier = {"Excellent": 1.0, "Good": 0.85, "Fair": 0.7, "Poor": 0.5}
        price *= condition_multiplier[condition]

        # Add some randomness
        price *= np.random.uniform(0.9, 1.1)
        price = round(price, 2)

        # Mileage based on age and some randomness
        mileage = age * np.random.uniform(8000, 15000)
        mileage = round(mileage)

        # Create record
        record = {
            "car_id": f"CAR{i+1:04d}",
            "make": make,
            "model": model,
            "year": year,
            "price": price,
            "mileage": mileage,
            "condition": condition,
            "color": np.random.choice(colors),
            "fuel_type": np.random.choice(fuel_types, p=[0.7, 0.15, 0.1, 0.05]),
            "transmission": np.random.choice(["Automatic", "Manual"], p=[0.85, 0.15]),
            "listed_date": datetime.now() - timedelta(days=np.random.randint(1, 365)),
            "dealer_location": np.random.choice(
                ["Downtown", "North Side", "South Side", "West End", "East Side"]
            ),
            "mpg_city": np.random.randint(18, 35),
            "mpg_highway": np.random.randint(25, 45),
        }

        data.append(record)

    return pd.DataFrame(data)


def demo_basic_analysis():
    """Demonstrate basic data analysis capabilities"""
    print("\n" + "=" * 60)
    print("🚗 CAR SALES DATA ANALYSIS DEMO")
    print("=" * 60)

    # Create sample data
    print("\n📊 Creating sample car sales data...")
    car_data = create_sample_car_data()

    # Save to CSV for analysis
    csv_path = "/tmp/car_sales_data.csv"
    car_data.to_csv(csv_path, index=False)
    print(f"✅ Created {len(car_data)} car records")
    print(f"💾 Saved to: {csv_path}")

    # Analyze the data
    print("\n🔍 Analyzing car sales data...")
    analysis_result = daf.analyze(csv_path)

    if "error" in analysis_result:
        print(f"❌ Analysis failed: {analysis_result['error']}")
        return None

    # Display analysis results
    data_type = analysis_result["data_type"]
    analysis = analysis_result["analysis"]

    print(f"✅ Data Type: {data_type.type_name}")
    print(f"📈 Records: {data_type.total_rows:,}")
    print(f"📋 Columns: {data_type.total_columns}")
    print(f"⭐ Quality Score: {analysis.quality_score:.2f}")
    print(f"🎯 Query Complexity: {analysis.query_complexity}")

    print(f"\n🔍 Detected Patterns:")
    for pattern in analysis.detected_patterns:
        print(f"  • {pattern}")

    print(f"\n💡 Recommended Operations:")
    for op in analysis.recommended_operations:
        print(f"  • {op}")

    return csv_path


def demo_agent_interface():
    """Demonstrate AI agent interaction with car data"""
    print("\n" + "=" * 60)
    print("🤖 AI AGENT INTERFACE DEMO")
    print("=" * 60)

    # Create sample data
    car_data = create_sample_car_data()
    csv_path = "/tmp/car_sales_data.csv"
    car_data.to_csv(csv_path, index=False)

    # Create agent interface
    print("\n🔧 Creating AI agent interface...")
    interface = daf.create_agent_interface(csv_path)

    # Get data overview
    print("\n📋 Data Overview:")
    overview = interface.get_data_overview()
    print(f"  • Shape: {overview['shape']}")
    print(f"  • Memory Usage: {overview['memory_usage']:,} bytes")
    print(f"  • Query Capabilities: {len(overview['query_capabilities'])} types")

    # Show sample data
    print(f"\n📄 Sample Records:")
    for i, record in enumerate(overview["sample_data"][:3]):
        print(
            f"  {i+1}. {record['year']} {record['make']} {record['model']} - ${record['price']:,.2f}"
        )

    return interface


def demo_natural_language_queries(interface):
    """Demonstrate natural language querying"""
    print("\n" + "=" * 60)
    print("💬 NATURAL LANGUAGE QUERIES")
    print("=" * 60)

    # Test queries that demonstrate the car sales use case
    test_queries = [
        "Find all cars under $25000",
        "Show me cars under $30000 with good condition",
        "What is the average price of all cars?",
        "Count how many Toyota cars we have",
        "Show me the most expensive cars",
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        print("-" * 50)

        result = interface.execute_query(query)
        results.append(result)

        if result.success:
            print(f"✅ Success: Found {result.row_count} records")
            print(f"⏱️  Execution time: {result.execution_time_ms:.1f}ms")
            print(f"📊 Data quality: {result.data_quality_score:.2f}")

            # Show insights
            if result.insights:
                print(f"💡 Insights:")
                for insight in result.insights[:3]:
                    print(f"   • {insight}")

            # Show recommendations
            if result.recommendations:
                print(f"🎯 Recommendations:")
                for rec in result.recommendations[:2]:
                    print(f"   • {rec}")

            # Show sample results for filter queries
            if (
                result.query_id.startswith("query_")
                and result.data is not None
                and len(result.data) > 0
            ):
                print(f"📋 Sample Results:")
                sample_data = result.data.head(3)
                for idx, row in sample_data.iterrows():
                    if "make" in row and "model" in row and "price" in row:
                        print(
                            f"   • {row.get('year', 'N/A')} {row['make']} {row['model']} - ${row['price']:,.2f}"
                        )
        else:
            print(f"❌ Failed: {result.warnings}")

    return results


def demo_business_report(interface, query_results):
    """Demonstrate business intelligence report generation"""
    print("\n" + "=" * 60)
    print("📈 BUSINESS INTELLIGENCE REPORT")
    print("=" * 60)

    # Generate comprehensive business report
    report = interface.generate_report(
        query_results, "Car Sales Analysis Report", report_type="detailed"
    )

    print(f"\n📊 {report['title']}")
    print(f"📅 Generated: {report['generated_at'][:19]}")
    print(f"📝 Type: {report['report_type']}")

    print(f"\n📋 Executive Summary:")
    print(f"  {report['executive_summary']}")

    print(f"\n🔍 Key Findings:")
    for finding in report["key_findings"][:5]:
        print(f"  • {finding}")

    print(f"\n💡 Recommendations:")
    for rec in report["recommendations"][:5]:
        print(f"  • {rec}")

    print(f"\n📊 Data Quality Assessment:")
    quality = report["data_quality_assessment"]
    print(f"  • Overall Score: {quality['overall_score']:.2f}")
    print(f"  • Assessment: {quality['assessment']}")
    print(f"  • Queries Analyzed: {quality['queries_analyzed']}")

    print(f"\n📋 Analysis Statistics:")
    appendix = report["appendix"]
    print(f"  • Total Queries: {appendix['queries_executed']}")
    print(f"  • Records Analyzed: {appendix['total_records_analyzed']:,}")
    print(f"  • Data Sources: {len(appendix['data_sources'])} columns")

    return report


def demo_advanced_scenarios():
    """Demonstrate advanced use cases"""
    print("\n" + "=" * 60)
    print("🚀 ADVANCED USE CASE SCENARIOS")
    print("=" * 60)

    # Create sample data
    car_data = create_sample_car_data()
    csv_path = "/tmp/car_sales_data.csv"
    car_data.to_csv(csv_path, index=False)

    # Create interface
    interface = daf.create_agent_interface(csv_path)

    # Scenario 1: Budget-conscious buyer
    print(f"\n💰 Scenario 1: Budget-Conscious Buyer ($20,000 budget)")
    print("-" * 50)

    budget_query = "Find cars under $20000 with good condition"
    budget_result = interface.execute_query(budget_query)

    if budget_result.success and budget_result.data is not None:
        affordable_cars = budget_result.data
        print(f"✅ Found {len(affordable_cars)} affordable cars in good condition")

        if len(affordable_cars) > 0:
            avg_price = affordable_cars["price"].mean()
            avg_mileage = affordable_cars["mileage"].mean()
            most_common_make = (
                affordable_cars["make"].mode().iloc[0]
                if len(affordable_cars["make"].mode()) > 0
                else "N/A"
            )

            print(f"📊 Analysis:")
            print(f"   • Average Price: ${avg_price:,.2f}")
            print(f"   • Average Mileage: {avg_mileage:,.0f} miles")
            print(f"   • Most Common Make: {most_common_make}")

            print(f"🚗 Top 3 Recommendations:")
            top_3 = affordable_cars.nsmallest(3, "mileage")  # Lowest mileage first
            for idx, (_, car) in enumerate(top_3.iterrows(), 1):
                print(
                    f"   {idx}. {car['year']} {car['make']} {car['model']} - ${car['price']:,.2f} ({car['mileage']:,} miles)"
                )

    # Scenario 2: Luxury car buyer
    print(f"\n💎 Scenario 2: Luxury Car Buyer (Premium brands)")
    print("-" * 50)

    luxury_query = "Find BMW or Mercedes cars"
    luxury_result = interface.execute_query(luxury_query)

    if luxury_result.success:
        print(f"✅ Found luxury vehicles")
        print(
            f"💡 Insights: {luxury_result.insights[0] if luxury_result.insights else 'Premium selection available'}"
        )

        # Get suggestions for next steps
        suggestions = interface.get_query_suggestions("luxury cars")
        print(f"🎯 Suggested follow-up queries:")
        for suggestion in suggestions[:3]:
            print(f"   • {suggestion['query']}")

    # Scenario 3: Fuel efficiency focus
    print(f"\n⛽ Scenario 3: Fuel-Efficient Vehicle Search")
    print("-" * 50)

    efficiency_query = "Show me hybrid or electric cars"
    efficiency_result = interface.execute_query(efficiency_query)

    if efficiency_result.success:
        print(f"✅ Found eco-friendly vehicles")
        if efficiency_result.recommendations:
            print(f"💡 Recommendation: {efficiency_result.recommendations[0]}")

    return [budget_result, luxury_result, efficiency_result]


def main():
    """Run the complete car sales demo"""
    print("🚀 Starting Data Analysis Framework Demo")
    print("Focus: AI Agent Interaction with Structured Data")
    print("Use Case: Car Sales Database Analysis")

    try:
        # Basic analysis demo
        csv_path = demo_basic_analysis()
        if not csv_path:
            return

        # Agent interface demo
        interface = demo_agent_interface()

        # Natural language queries
        query_results = demo_natural_language_queries(interface)

        # Business report generation
        report = demo_business_report(interface, query_results)

        # Advanced scenarios
        advanced_results = demo_advanced_scenarios()

        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n✅ Key Capabilities Demonstrated:")
        print("  • Intelligent data analysis and profiling")
        print("  • AI-safe structured data querying")
        print("  • Natural language query processing")
        print("  • Business intelligence report generation")
        print("  • Real-world use case scenarios")

        print(f"\n🎯 This demonstrates the key differentiator:")
        print(f"  Instead of document chunking, we provide intelligent")
        print(f"  APIs for AI agents to safely interact with structured data!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
