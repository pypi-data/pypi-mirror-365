from textwrap import dedent

EXECUTE_DATA_CODE_TOOL_PROMPT = dedent("""
# execute_data_code Tool

Description: Execute Python code in a persistent Jupyter kernel for data analysis. Variables, imports, and data persist across executions.

Parameters:
- code: (string, required) Python code to execute
- timeout: (integer, optional) Maximum execution time in seconds (default: 30)

Output: String containing:
- Execution results (stdout, expression values)
- Error messages with tracebacks (if any)
- Indicators for rich outputs like plots ("[Plot displayed]")
- Success message if no output

Examples:
- execute_data_code("import pandas as pd")
- execute_data_code("df = pd.read_csv('/path/to/data.csv')")
- execute_data_code("df = pd.read_csv('/path/to/large_file.csv')", timeout=120)  # Use higher timeout for large files
- execute_data_code("df_cleaned.to_csv('/path/to/output.csv', index=False)")
- execute_data_code("df.describe()", timeout=10)
- execute_data_code("plt.plot([1,2,3], [4,5,6]); plt.show()")
- execute_data_code("plt.savefig('/path/to/plot.png', dpi=300, bbox_inches='tight')")

Notes:
- State persists between calls - variables remain available
- Rich outputs (plots, HTML) are indicated in output
- Kernel automatically starts on first use
- No user approval required for execution
- Use higher timeouts (60-120s) for operations on large files or datasets
- Default timeout is 30s, which may be insufficient for large CSV files
""")