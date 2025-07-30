"""
Data Analysis Framework - Examples Package

This package contains comprehensive examples demonstrating the capabilities
of the Data Analysis Framework for structured data analysis and AI-agent interaction.

Examples are organized by complexity and use case:
- 00_car_sales_demo.py: Simple business scenario (car dealership)
- 01_basic_framework_demo.py: Basic framework functionality
- 02_comprehensive_business_demo.py: Multi-domain business analysis
- 03_multi_sheet_excel_demo.py: Complex Excel file handling
- 04_logistics_optimization_demo.py: Enterprise logistics optimization

Each example is fully self-contained and can be run independently.
"""

__version__ = "1.0.0"
__author__ = "AI Building Blocks"


def list_examples():
    """List all available examples with descriptions"""
    examples = {
        "00_car_sales_demo": "Simple car dealership analysis with budget filtering",
        "01_basic_framework_demo": "Basic framework functionality and API usage",
        "02_comprehensive_business_demo": "Multi-domain business analysis (5 sectors)",
        "03_multi_sheet_excel_demo": "Complex Excel files with multiple sheets",
        "04_logistics_optimization_demo": "Enterprise logistics with route optimization",
    }

    print("📚 Data Analysis Framework Examples:")
    print("=" * 50)
    for name, description in examples.items():
        print(f"  {name}: {description}")

    return examples


def run_example(example_name: str):
    """Run a specific example by name"""
    import subprocess
    import sys
    import os

    example_file = f"{example_name}.py"
    example_path = os.path.join(os.path.dirname(__file__), example_file)

    if not os.path.exists(example_path):
        print(f"❌ Example '{example_name}' not found")
        return False

    try:
        print(f"🚀 Running example: {example_name}")
        result = subprocess.run([sys.executable, example_path], capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run example: {e}")
        return False


__all__ = ["list_examples", "run_example"]
