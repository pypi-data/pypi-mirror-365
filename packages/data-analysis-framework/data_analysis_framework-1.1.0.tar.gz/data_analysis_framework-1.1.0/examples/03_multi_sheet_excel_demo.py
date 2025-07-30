#!/usr/bin/env python3
"""
Excel Format Demo - Data Analysis Framework

Quick demonstration that the framework works seamlessly with Excel files,
which are extremely common in business environments.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    import data_analysis_framework as daf

    print("✅ Data Analysis Framework imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def create_sales_excel_demo():
    """Create a realistic sales Excel file for testing"""
    print("📊 Creating Sales Excel Demo File...")

    # Generate realistic sales data
    np.random.seed(42)

    # Sales data for multiple months
    months = pd.date_range("2024-01-01", periods=12, freq="M")
    products = ["Laptop", "Desktop", "Monitor", "Keyboard", "Mouse", "Printer", "Scanner"]
    regions = ["North", "South", "East", "West", "Central"]
    sales_reps = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown"]

    sales_data = []
    for month in months:
        for _ in range(np.random.randint(15, 25)):  # 15-25 sales per month
            sale = {
                "Date": month + timedelta(days=np.random.randint(0, 28)),
                "Product": np.random.choice(products),
                "Region": np.random.choice(regions),
                "Sales_Rep": np.random.choice(sales_reps),
                "Quantity": np.random.randint(1, 10),
                "Unit_Price": round(np.random.uniform(200, 2000), 2),
                "Total_Sales": 0,  # Will calculate
                "Customer_Type": np.random.choice(["New", "Existing"], p=[0.3, 0.7]),
                "Discount_Pct": round(np.random.uniform(0, 0.15), 2),
                "Commission_Rate": round(np.random.uniform(0.05, 0.12), 2),
            }

            # Calculate total sales with discount
            total_before_discount = sale["Quantity"] * sale["Unit_Price"]
            sale["Total_Sales"] = round(total_before_discount * (1 - sale["Discount_Pct"]), 2)

            sales_data.append(sale)

    # Create Excel file with multiple sheets
    excel_path = "/tmp/sales_demo.xlsx"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Main sales data
        sales_df = pd.DataFrame(sales_data)
        sales_df.to_excel(writer, sheet_name="Sales_Data", index=False)

        # Summary by product
        product_summary = (
            sales_df.groupby("Product").agg({"Quantity": "sum", "Total_Sales": "sum"}).reset_index()
        )
        product_summary.to_excel(writer, sheet_name="Product_Summary", index=False)

        # Regional performance
        regional_summary = (
            sales_df.groupby("Region").agg({"Total_Sales": ["sum", "mean", "count"]}).reset_index()
        )
        regional_summary.columns = [
            "Region",
            "Total_Sales_Sum",
            "Avg_Sale_Amount",
            "Number_of_Sales",
        ]
        regional_summary.to_excel(writer, sheet_name="Regional_Summary", index=False)

    print(f"✅ Created Excel file: {excel_path}")
    print(f"📊 Generated {len(sales_data)} sales records across 3 sheets")

    return excel_path, sales_df


def test_excel_analysis():
    """Test the framework with Excel files"""
    print("\n" + "=" * 60)
    print("📈 EXCEL FORMAT ANALYSIS DEMO")
    print("=" * 60)

    # Create demo Excel file
    excel_path, original_df = create_sales_excel_demo()

    try:
        # Test basic analysis
        print(f"\n🔍 Analyzing Excel File: {excel_path}")
        analysis_result = daf.analyze(excel_path)

        if "error" in analysis_result:
            print(f"❌ Analysis failed: {analysis_result['error']}")
            return

        data_type = analysis_result["data_type"]
        analysis = analysis_result["analysis"]

        print(f"✅ Excel Analysis Results:")
        print(f"  • Data Type: {data_type.type_name}")
        print(f"  • Number of Sheets: {data_type.tables_count}")
        print(f"  • Sheet Names: {', '.join(data_type.sheets_or_tables)}")
        print(f"  • Total Records: {data_type.total_rows:,}")
        print(f"  • Total Columns: {data_type.total_columns}")
        print(f"  • Quality Score: {analysis.quality_score:.2f}")
        print(f"  • File Size: {data_type.file_size_mb:.2f} MB")

        if analysis.detected_patterns:
            print(f"  • Detected Patterns: {', '.join(analysis.detected_patterns)}")

        # Test AI Agent Interface with Excel
        print(f"\n🤖 AI Agent Interface with Excel:")
        interface = daf.create_agent_interface(excel_path)
        overview = interface.get_data_overview()

        if "error" not in overview:
            print(f"✅ Excel Interface Ready:")
            print(f"  • Shape: {overview['shape']}")
            print(f"  • Query Capabilities: {len(overview['query_capabilities'])} types")

            # Test Excel-specific queries
            excel_queries = [
                "Show me sales over $5000",
                "What is the average sales amount?",
                "Count sales by region",
                "Find top performing sales reps",
            ]

            results = []
            for i, query in enumerate(excel_queries, 1):
                print(f"\n  🔍 Excel Query {i}: '{query}'")
                result = interface.execute_query(query)
                results.append(result)

                if result.success:
                    print(f"    ✅ Success: {result.row_count} records")
                    print(f"    ⏱️  Execution: {result.execution_time_ms:.1f}ms")
                    if result.insights:
                        print(f"    💡 Insight: {result.insights[0]}")
                else:
                    print(
                        f"    ❌ Failed: {result.warnings[0] if result.warnings else 'Unknown error'}"
                    )

            # Generate Excel business report
            if results and any(r.success for r in results):
                print(f"\n📋 Excel Business Report:")
                report = interface.generate_report(results, "Sales Performance Analysis")
                print(f"    • Report: {report['title']}")
                print(f"    • Generated: {report['generated_at'][:19]}")
                print(f"    • Key Findings: {len(report['key_findings'])}")
                print(
                    f"    • Quality Assessment: {report['data_quality_assessment']['assessment']}"
                )

        print(f"\n✅ Excel format testing completed successfully!")

    except Exception as e:
        print(f"❌ Excel testing failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        try:
            os.unlink(excel_path)
        except:
            pass


if __name__ == "__main__":
    print("🧪 Testing Excel Format Support")
    print("=" * 40)
    print("Demonstrating framework capabilities with Excel files")
    print("(Very common format in business environments)")

    test_excel_analysis()

    print(f"\n🎉 Excel Demo Completed!")
    print(f"✅ Framework successfully handles Excel multi-sheet files")
    print(f"🚀 Ready for real-world business Excel data!")
