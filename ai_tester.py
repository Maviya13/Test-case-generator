# # ai_tester.py
# import ast
# import os
# import subprocess
# import logging
# from dotenv import load_dotenv
# import google.genai as genai # Gemini SDK
# import sys, os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import sample_module

# # -------------------------
# # Setup logging
# # -------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)

# # -------------------------
# # Load API Key from .env
# # -------------------------
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY not found in .env file.")

# # -------------------------
# # Initialize Gemini Client
# # -------------------------
# client = genai.Client(api_key=GEMINI_API_KEY)
# # -------------------------
# # Phase 1: Baseline Test Generator
# # -------------------------
# def generate_baseline_tests(module_path, test_file="tests/test_generated.py"):
#     os.makedirs(os.path.dirname(test_file), exist_ok=True)

#     with open(module_path, "r") as f:
#         tree = ast.parse(f.read())

#     functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
#     classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]

#     with open(test_file, "w") as f:
#         f.write(f"import sys, os\nimport pytest\nsys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '..'))\n")
#         module_name = os.path.splitext(os.path.basename(module_path))[0]
#         f.write(f"import {module_name}\n\n")

#         for func in functions:
#             args = ", ".join([a.arg for a in func.args.args])
#             f.write(f"def test_{func.name}():\n")
#             f.write(f"    # baseline auto-generated\n")
#             f.write(f"    result = {module_name}.{func.name}({', '.join(['0']*len(func.args.args))})\n")
#             f.write(f"    assert result is not None\n\n")

#         for cls in classes:
#             f.write(f"def test_{cls.name}():\n")
#             f.write(f"    # baseline auto-generated for class\n")
#             f.write(f"    obj = {module_name}.{cls.name}()\n")
#             f.write(f"    assert obj is not None\n\n")

#     logger.info(f"✅ Baseline tests written to {test_file}")
#     return functions, classes, test_file

# # -------------------------
# # Phase 2: LLM-enhanced Test Generator (Gemini)
# # -------------------------
# def call_gemini_for_tests(func_name, signature, docstring=None, max_cases=3):
#     prompt = f"""
# You are an expert Python developer.
# Generate up to {max_cases} pytest test functions for the following Python function:

# Function Name: {func_name}
# Signature: {signature}
# Docstring: {docstring}

# Requirements:
# - Use meaningful dummy inputs based on type hints.
# - Include edge cases and negative tests if possible.
# - Each test must be a valid Python function starting with "def test_".
# - Include assert statements verifying expected output.
# - Return only Python code, nothing else.
# """
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5",
#             contents=prompt,
#         )
#         return response.text.split("\n\n")
#     except Exception as e:
#         logger.error(f"Error generating tests for {func_name}: {e}")
#         return []


# def generate_llm_tests(module_path, test_file, functions):
#     module_name = os.path.splitext(os.path.basename(module_path))[0]
#     with open(test_file, "a") as f:
#         for func in functions:
#             func_name = func.name
#             signature = f"def {func_name}({', '.join([a.arg for a in func.args.args])})"
#             docstring = ast.get_docstring(func)
#             llm_tests = call_gemini_for_tests(func_name, signature, docstring)
#             for t in llm_tests:
#                 if t.strip():
#                     f.write("\n" + t.strip() + "\n")
#     logger.info(f"✅ LLM-generated tests appended to {test_file}")

# # -------------------------
# # Run pytest and save results
# # -------------------------
# def run_tests(test_file, results_file="results/test_results.json"):
#     os.makedirs(os.path.dirname(results_file), exist_ok=True)
#     cmd = [
#         "pytest",
#         test_file,
#         "--json-report",
#         f"--json-report-file={results_file}",
#         "-q",
#         "--tb=short"
#     ]
#     logger.info(f"Running pytest on {test_file}...")
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     logger.info(result.stdout)
#     if result.stderr:
#         logger.error(result.stderr)

#     if os.path.exists(results_file):
#         logger.info(f"Structured JSON results saved to {results_file}")
#     else:
#         logger.warning("❌ JSON report not generated. Check pytest-json-report plugin.")

# # -------------------------
# # Main Execution
# # -------------------------
# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser(description="AI-powered Test Generator with Gemini API")
#     parser.add_argument("module", help="Python module to test")
#     args = parser.parse_args()

#     funcs, classes, test_file = generate_baseline_tests(args.module)
#     generate_llm_tests(args.module, test_file, funcs)
#     run_tests(test_file)



# ai_tester.py
import ast
import os
import subprocess
import logging
import json
from typing import List, Tuple
import sys
from dotenv import load_dotenv
import google.generativeai as genai  # Gemini SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# -------------------------
# Setup logging
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Gemini client is initialized lazily in main() only if LLM generation is enabled

# -------------------------
# Helper Functions
# -------------------------
def extract_function_info(func_node: ast.FunctionDef) -> dict:
    """Extract detailed information about a function for better test generation."""
    info = {
        'name': func_node.name,
        'args': [arg.arg for arg in func_node.args.args],
        'arg_types': [],
        'return_type': None,
        'docstring': ast.get_docstring(func_node)
    }
    
    # Extract type hints if available
    for arg in func_node.args.args:
        if arg.annotation:
            try:
                info['arg_types'].append(ast.unparse(arg.annotation))
            except:
                info['arg_types'].append('Any')
        else:
            info['arg_types'].append('Any')
    
    if func_node.returns:
        try:
            info['return_type'] = ast.unparse(func_node.returns)
        except:
            info['return_type'] = 'Any'
    
    return info

def get_default_value_for_type(type_hint: str) -> str:
    """Generate appropriate default values based on type hints."""
    type_defaults = {
        'int': '0',
        'str': '""',
        'float': '0.0',
        'bool': 'True',
        'list': '[]',
        'dict': '{}',
        'tuple': '()',
        'set': 'set()',
        'List': '[]',
        'Dict': '{}',
        'Optional': 'None'
    }
    
    # Handle Union types like Optional[int]
    if "Optional[" in type_hint:
        inner_type = type_hint.split("[")[1].split("]")[0]
        return type_defaults.get(inner_type, 'None')
    
    if type_hint == 'Any':
        return '0' # Default to int for untyped arguments in baseline tests

    for type_name, default in type_defaults.items():
        if type_name.lower() in type_hint.lower():
            return default
    return 'None'  # fallback

# -------------------------
# Phase 1: Enhanced Baseline Test Generator
# -------------------------
def generate_baseline_tests(module_path: str, test_file: str = "tests/test_generated.py") -> Tuple[List[dict], List[ast.ClassDef], str]:
    """Generate baseline tests with improved parameter handling."""
    os.makedirs(os.path.dirname(test_file), exist_ok=True)

    with open(module_path, "r", encoding='utf-8') as f:
        tree = ast.parse(f.read())

    functions = [extract_function_info(n) for n in tree.body if isinstance(n, ast.FunctionDef)]
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]

    module_name = os.path.splitext(os.path.basename(module_path))[0]
    
    with open(test_file, "w", encoding='utf-8') as f:
        # Write imports
        f.write("import sys\nimport os\nimport pytest\n")
        f.write("sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n")
        f.write(f"import {module_name}\n\n")

        # Generate function tests
        for func_info in functions:
            func_name = func_info['name']
            args = func_info['args']
            arg_types = func_info['arg_types']
            
            # Skip private methods and __init__
            if func_name.startswith('_'):
                continue
                
            f.write(f"def test_{func_name}_baseline():\n")
            f.write(f"    \"\"\"Baseline auto-generated test for {func_name}.\"\"\"\n")
            
            # Generate appropriate arguments based on type hints
            test_args = []
            for i, (arg, arg_type) in enumerate(zip(args, arg_types)):
                if arg == 'self':  # Skip self parameter
                    continue
                test_args.append(get_default_value_for_type(arg_type))
            
            args_str = ', '.join(test_args)
            f.write(f"    try:\n")
            f.write(f"        result = {module_name}.{func_name}({args_str})\n")
            f.write(f"        assert result is not None or result == 0 or result == '' or result == []\n")
            f.write(f"    except Exception as e:\n")
            f.write(f"        pytest.fail(f'Function {func_name} raised {{type(e).__name__}}: {{e}}')\n\n")

        # Generate class tests
        for cls in classes:
            cls_name = cls.name
            if cls_name.startswith('_'):
                continue
                
            f.write(f"def test_{cls_name}_instantiation():\n")
            f.write(f"    \"\"\"Baseline test for {cls_name} class instantiation.\"\"\"\n")
            f.write(f"    try:\n")
            f.write(f"        obj = {module_name}.{cls_name}()\n")
            f.write(f"        assert obj is not None\n")
            f.write(f"    except TypeError:\n")
            f.write(f"        # Class might require arguments\n")
            f.write(f"        pytest.skip('Class {cls_name} requires constructor arguments')\n\n")

    logger.info(f"✅ Enhanced baseline tests written to {test_file}")
    return functions, classes, test_file

# -------------------------
# Phase 2: Enhanced LLM Test Generator (Gemini)
# -------------------------
def call_gemini_for_tests(func_info: dict, module_name: str, max_cases: int = 3) -> List[str]:
    """Generate tests using Gemini with improved prompting."""
    func_name = func_info['name']
    args = func_info['args']
    arg_types = func_info['arg_types']
    return_type = func_info['return_type']
    docstring = func_info['docstring']

    # Create a detailed function signature
    typed_args = []
    for arg, arg_type in zip(args, arg_types):
        if arg == 'self':
            continue
        typed_args.append(f"{arg}: {arg_type}")

    signature = f"def {func_name}({', '.join(typed_args)})"
    if return_type:
        signature += f" -> {return_type}"

    prompt = f"""
You are an expert Python test engineer. Generate {max_cases} comprehensive pytest test functions for this Python function:

**Function Details:**
- Name: {func_name}
- Signature: {signature}
- Docstring: {docstring or "No docstring provided"}
- Module: {module_name}

**Requirements:**
1. Each test function must start with "def test_{func_name}_"
2. Use realistic test data based on the parameter types
3. Include edge cases (empty inputs, None values, boundary conditions)
4. Add both positive and negative test cases
5. Use descriptive assertions that explain what's being tested
6. Handle potential exceptions appropriately
7. Import the module as: {module_name}.{func_name}()
8. For TypeError when concatenating str and int, the message is likely 'can only concatenate str (not "int") to str'
9. For hello(None), the expected return is "Hello, World!"
10. If a numeric value is passed to hello(name), it should be treated as a string and return a personalized greeting.

**Example format:**
```python
def test_{func_name}_valid_input():
    \"\"\"Test {func_name} with valid input.\"\"\"
    result = {module_name}.{func_name}(valid_args)
    assert result == expected_value

def test_{func_name}_edge_case():
    \"\"\"Test {func_name} with edge case.\"\"\"
    result = {module_name}.{func_name}(edge_case_args)
    assert isinstance(result, expected_type)
```

Generate only the test functions, no explanations.
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")  # Updated to latest model
        response = model.generate_content(
            contents=prompt,
        )

        # Parse the response to extract individual test functions
        response_text = response.text
        if '```python' in response_text:
            # Extract code blocks
            code_blocks = []
            lines = response_text.split('\n')
            in_code_block = False
            current_block = []

            for line in lines:
                if line.strip().startswith('```python'):
                    in_code_block = True
                    current_block = []
                elif line.strip() == '```' and in_code_block:
                    in_code_block = False
                    if current_block:
                        code_blocks.append('\n'.join(current_block))
                elif in_code_block:
                    current_block.append(line)

            return code_blocks
        else:
            # Split by function definitions
            functions = []
            current_func = []
            lines = response_text.split('\n')

            for line in lines:
                if line.startswith('def test_') and current_func:
                    functions.append('\n'.join(current_func))
                    current_func = [line]
                elif line.startswith('def test_'):
                    current_func = [line]
                elif current_func:
                    current_func.append(line)

            if current_func:
                functions.append('\n'.join(current_func))

            return functions

    except Exception as e:
        logger.error(f"Error generating tests for {func_name}: {e}")
        return []

def generate_llm_tests(module_path: str, test_file: str, functions: List[dict], max_cases: int = 3) -> None:
    """Generate LLM-enhanced tests and append to test file."""
    module_name = os.path.splitext(os.path.basename(module_path))[0]

    with open(test_file, "a", encoding='utf-8') as f:
        f.write("\n# =============================\n")
        f.write("# LLM-Generated Enhanced Tests\n")
        f.write("# =============================\n\n")

        for func_info in functions:
            func_name = func_info['name']

            # Skip private methods
            if func_name.startswith('_'):
                continue

            logger.info(f"Generating LLM tests for {func_name}...")
            llm_tests = call_gemini_for_tests(func_info, module_name, max_cases=max_cases)

            if llm_tests:
                f.write(f"# Tests for {func_name}\n")
                for test_code in llm_tests:
                    if test_code.strip():
                        f.write(test_code.strip() + "\n\n")
            else:
                logger.warning(f"No LLM tests generated for {func_name}")

    logger.info(f"✅ LLM-generated tests appended to {test_file}")

# -------------------------
# Test Execution with Enhanced Reporting
# -------------------------
def run_tests(test_file: str, results_file: str = "results/test_results.json", coverage_file: str = "results/coverage.json") -> dict:
    """Run pytest and generate detailed results, including code coverage."""
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    # Check if pytest-json-report is installed
    try:
        import pytest_jsonreport
        use_json_report = True
    except ImportError:
        logger.warning("pytest-json-report not installed. Using basic output.")
        use_json_report = False

    # Determine module name for coverage
    module_name = os.path.splitext(os.path.basename(test_file))[0].replace('test_', '')
    
    # Construct pytest command
    cmd = [
        "pytest",
        test_file,
        f"--cov={module_name}",
        f"--cov-report=json:{coverage_file}",
        "-v",
        "--tb=short"
    ]

    if use_json_report:
        cmd.extend([
            "--json-report",
            f"--json-report-file={results_file}",
        ])
    
    logger.info(f"Running pytest on {test_file} with coverage for {module_name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log output
    if result.stdout:
        logger.info("STDOUT:\n" + result.stdout)
    if result.stderr:
        logger.error("STDERR:\n" + result.stderr)
    
    # Load and return results
    test_results = {
        'return_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }
    
    if use_json_report and os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                json_results = json.load(f)
                test_results['json_report'] = json_results
                logger.info(f"✅ Detailed JSON results saved to {results_file}")
        except Exception as e:
            logger.error(f"Error reading JSON results: {e}")

    if os.path.exists(coverage_file):
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
                test_results['coverage_report'] = coverage_data
                logger.info(f"✅ Coverage report saved to {coverage_file}")
        except Exception as e:
            logger.error(f"Error reading coverage results: {e}")
    else:
        logger.warning("❌ Coverage report not generated. Check coverage plugin.")
    
    return test_results

# -------------------------
# Results Analysis
# -------------------------
def analyze_results(results: dict, module_name: str = "sample_module") -> None:
    """Analyze and report test and coverage results."""
    if 'json_report' in results:
        json_data = results['json_report']
        summary = json_data.get('summary', {})
        
        logger.info("=" * 50)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total tests: {summary.get('total', 0)}")
        logger.info(f"Passed: {summary.get('passed', 0)}")
        logger.info(f"Failed: {summary.get('failed', 0)}")
        logger.info(f"Skipped: {summary.get('skipped', 0)}")
        logger.info(f"Errors: {summary.get('error', 0)}")
        
        if summary.get('failed', 0) > 0:
            logger.info("\nFAILED TESTS:")
            for test in json_data.get('tests', []):
                if test.get('outcome') == 'failed':
                    logger.info(f"- {test.get('nodeid')}: {test.get('call', {}).get('longrepr', 'Unknown error')}")

    if 'coverage_report' in results:
        coverage_data = results['coverage_report']
        logger.info("=" * 50)
        logger.info("CODE COVERAGE SUMMARY")
        logger.info("=" * 50)
        
        # Extract coverage for the relevant module
        files = coverage_data.get('files', {})
        if module_name + '.py' in files:
            module_coverage = files[module_name + '.py']
            summary = module_coverage.get('summary', {})
            logger.info(f"File: {module_name}.py")
            logger.info(f"Statements: {summary.get('num_statements', 0)}")
            logger.info(f"Missing: {summary.get('missing_lines', [])}")
            logger.info(f"Covered: {summary.get('covered_lines', [])}")
            logger.info(f"Branch Coverage: {summary.get('percent_covered_display', 'N/A')}%")
        else:
            logger.warning(f"No coverage data found for {module_name}.py")
    else:
        logger.warning("❌ No coverage report available.")

    logger.info("=" * 50)

# -------------------------
# Main Execution
# -------------------------
def main():
    """Main function to orchestrate test generation and execution."""
    import argparse
    parser = argparse.ArgumentParser(description="AI-powered Test Generator with Gemini API")
    parser.add_argument("module", help="Python module to test")
    parser.add_argument("--test-file", default="tests/test_generated.py", help="Output test file")
    parser.add_argument("--results-file", default="results/test_results.json", help="Results file")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM test generation")
    parser.add_argument("--max-cases", type=int, default=3, help="Max test cases per function")
    
    args = parser.parse_args()
    
    try:
        # Phase 1: Generate baseline tests
        logger.info("Starting Phase 1: Baseline test generation...")
        functions, classes, test_file = generate_baseline_tests(args.module, args.test_file)
        
        # Phase 2: Generate LLM tests (unless skipped)
        if not args.skip_llm:
            logger.info("Starting Phase 2: LLM-enhanced test generation...")
            load_dotenv()
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY not found. Skipping LLM test generation.")
            else:
                genai.configure(api_key=gemini_api_key)
                generate_llm_tests(args.module, test_file, functions, max_cases=args.max_cases)
        else:
            logger.info("Skipping LLM test generation as requested")
        
        # Phase 3: Run tests
        logger.info("Starting Phase 3: Test execution...")
        results = run_tests(test_file, args.results_file)
        
        # Phase 4: Analyze results
        logger.info("Starting Phase 4: Results analysis...")
        analyze_results(results)
        
        logger.info("🎉 AI Test Generator completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during execution: {e}")
        # Re-raise the exception after logging it, so the script exits with an error code.
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in main execution: {e}")
        sys.exit(1)