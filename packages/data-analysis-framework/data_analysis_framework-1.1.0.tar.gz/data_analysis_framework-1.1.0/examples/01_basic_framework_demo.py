#!/usr/bin/env python3
"""
Simple test script to verify data-analysis-framework functionality
"""

import sys
import os
import pandas as pd
import tempfile

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_basic_functionality():
    """Test basic framework functionality"""
    try:
        import data_analysis_framework as daf

        print("✅ Import successful")

        # Test supported formats
        formats = daf.get_supported_formats()
        print(f"✅ Supported formats: {len(formats)} formats")

        # Create test CSV data
        test_data = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie", "Diana"],
                "age": [25, 30, 35, 28],
                "salary": [50000, 65000, 75000, 58000],
                "department": ["Engineering", "Sales", "Engineering", "Marketing"],
            }
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_path = f.name

        print(f"✅ Created test data: {csv_path}")

        # Test analysis
        result = daf.analyze(csv_path)
        if "error" not in result:
            print(f"✅ Analysis successful: {result['data_type'].type_name}")
            print(f"   Records: {result['data_type'].total_rows}")
            print(f"   Quality: {result['analysis'].quality_score:.2f}")
        else:
            print(f"❌ Analysis failed: {result['error']}")
            return False

        # Test agent interface
        interface = daf.create_agent_interface(csv_path)
        overview = interface.get_data_overview()

        if "error" not in overview:
            print(f"✅ Agent interface working: {overview['shape']}")
        else:
            print(f"❌ Agent interface failed: {overview['error']}")
            return False

        # Test query
        query_result = interface.execute_query("Show me a summary of the data")
        if query_result.success:
            print(f"✅ Query successful: {query_result.row_count} results")
        else:
            print(f"❌ Query failed: {query_result.warnings}")
            return False

        # Cleanup
        os.unlink(csv_path)

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Testing Data Analysis Framework")
    print("=" * 40)

    success = test_basic_functionality()

    if success:
        print("\n🎉 All tests passed!")
        print("✅ Framework is ready for use")
    else:
        print("\n❌ Tests failed")
        sys.exit(1)
