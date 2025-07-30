tool_dict = {
"read_file" : """
Reads content from a file with optional line-based pagination.

This tool is intended for reading text files only. It tracks read operations
for later validation in write/edit commands. If the file is binary or unreadable
due to permissions or encoding, it returns a structured error.

Usage:
    await read_file("README.md", offset=1, limit=50)

Args:
    path (str): File path to read.
    offset (Optional[int]): Starting line number (1-based). Defaults to config default.
    limit (Optional[int]): Number of lines to read. Defaults to config default.
    encoding (Optional[str]): Encoding to use. Defaults to system default.

Returns:
    FileReadResponse:
        - content (str): File content (possibly truncated).
        - lines_shown (int), total_lines (int), is_truncated (bool)

Possible Failures:
    - File not found
    - Invalid encoding
    - Binary file (unsupported)
    - Permission issues

Suggestions:
    - Use `list_directory()` or `glob_files()` to find valid file paths.
    - Ensure encoding matches file format.
""",

"write_file" : """
Writes text content to a file, with overwrite protection.

To avoid accidental modification of unknown files, writing to an existing file
requires it to have been read first — unless `force=True`.

Usage:
    await write_file("example.txt", "new content", force=True)

Args:
    path (str): Path to file to write.
    content (str): Text content to write.
    force (bool): Set to True to bypass read-before-write check.
    encoding (Optional[str]): Text encoding (default: system default).

Returns:
    FileWriteResponse:
        - bytes_written (int)

Possible Failures:
    - Path invalid or unwritable
    - File not read beforehand (if force=False)
    - Permission or disk issues

Suggestions:
    - Use `read_file()` before editing.
    - Set `force=True` if you're sure you want to overwrite.
""",

"edit_file" : """
Performs text replacement in a file.

Supports both single and full replacement modes. The file must be read first
before edits are allowed for safety.

Usage:
    await edit_file("code.py", "old_function()", "new_function()", replace_all=True)

Args:
    path (str): Path to the file to edit.
    old_string (str): Text to search for.
    new_string (str): Replacement text.
    replace_all (bool): If True, replace all instances. Default is first match only.

Returns:
    FileEditResponse:
        - replacements_made (int)
        - preview (str): Change preview (first line diff)

Possible Failures:
    - File unread or not previously read
    - Match string not found
    - Write failure after edit

Suggestions:
    - Use `read_file()` before edit.
    - Ensure exact match in whitespace and formatting.
""",

"list_directory" : """
Lists files and directories in a path with metadata.

Supports ignore patterns (regex) for filtering out noisy entries such as `.git`
or `node_modules`.

Usage:
    await list_directory(".", ignore=["__pycache__"])

Args:
    path (str): Path to the directory to list.
    ignore (List[str]): Regex patterns to ignore (e.g., r"\\.git", r"__pycache__").

Returns:
    List[Dict]:
        - name, path, type ("file"/"directory"), size, is_text, etc.

Possible Failures:
    - Invalid or inaccessible directory path
    - Permission issues

Suggestions:
    - Use `glob_files()` to match specific file types.
    - Double-check directory path if result is empty.
""",

"create_bash_session" : """
Creates a named persistent bash session.

Sessions preserve environment, working directory, and state across commands.
Use when chaining multiple operations or running interactive shells.

Usage:
    await create_bash_session("dev-shell")

Args:
    session_name (Optional[str]): Name for the session. Defaults to config.

Returns:
    ToolResponse with session creation status.

Possible Failures:
    - Session already exists

Suggestions:
    - Use `get_bash_sessions()` to list existing ones.
    - Use `close_bash_session()` to close stale sessions.
""",

"run_command" : """
Executes a one-time shell command in non-interactive mode.

Recommended for simple commands with no state persistence.
Avoid using for REPLs, interactive scripts, or multi-step commands.

Usage:
    await run_command("ls -al", directory="src")

Args:
    command (str): Shell command to run.
    directory (Optional[str]): Working directory.

Returns:
    CommandResponse:
        - stdout, stderr, exit_code, command

Possible Failures:
    - Command not found
    - Syntax errors
    - Permission issues

Suggestions:
    - Use `run_bash_session()` for stateful or interactive operations.
""",

"run_bash_session" : """
Runs a command in a persistent interactive bash session.

Use this for programs that require input/output interactivity,
environment continuity, or multi-step workflows.

Suggestion : 
Interactive commands (use interactiev=False more often): Avoid commands that require interactive user input, as this can cause the tool to hang. Use non-interactive flags if available (e.g., npm init -y).

Usage:
    await run_bash_session("python3", session_name="py-dev", interactive=True)

Args:
    command (str): Command to run.
    session_name (Optional[str]): Session name. Defaults to config.
    timeout (Optional[float]): Max run time in seconds.
    interrupt (bool): Interrupt session instead of running command.
    interactive (Optional[bool]): Force interactive mode. checks using possible interactive expects using pyexpect.

Returns:
    CommandResponse:
        - stdout, stderr, session_name, is_interactive, expect_string

Possible Failures:
    - Session creation failed
    - Unexpected command behavior in interactive mode

Suggestions:
    - Avoid long-running sessions without timeout.
    - Use `interrupt=True` to stop hanging sessions.
""",


"glob_files" : """
Finds files matching a glob pattern, sorted by modification time.

This tool scans recursively and filters out common noise like `.git`, `node_modules`.
Results are sorted with the newest files first.

Usage:
    await glob_files("*.ts", path="src", case_sensitive=False)

Args:
    pattern (str): Glob pattern (e.g., "*.py", "**/*.md").
    path (str): Base directory to search.
    case_sensitive (bool): If True, pattern match is case-sensitive.

Returns:
    List[str]: List of matching file paths.

Possible Failures:
    - No matches
    - Invalid path
    - Permission denied

Suggestions:
    - Validate pattern correctness.
    - Use `list_directory()` to confirm path contents.
""",

"glob_files" : """
Search for a regex pattern across multiple files.

Supports directory-wide search using `grep` combined with `find`. Useful for
tracing usage of functions, variables, or keywords. Allows file filtering via extension.

Usage:
    await grep_files(pattern="def ", path="src", include="*.py")

Args:
    pattern (str): Regex pattern to search for (e.g., "import .*").
    path (str): Base directory to search in.
    include (str): File glob to restrict search scope (e.g., "*.js").

Returns:
    List[Dict]:
        - file (str): File path
        - line (int): Line number
        - content (str): Line text

Possible Failures:
    - No matches
    - Invalid regex
    - Permission errors on files

Suggestions:
    - Use `glob_files()` first to preview candidate files.
    - Keep patterns simple for performance.
""",

"format_code" : """
Format a source code file using the appropriate formatter.

Auto-selects formatter based on file extension. Supports Python, JS/TS, Go,
Rust, C/C++, Java, and more. You can override the formatter explicitly.

Usage:
    await format_code("app.py")
    await format_code("style.scss", formatter="prettier")

Args:
    file_path (str): Path to the file to format.
    formatter (Optional[str]): Formatter name (e.g., "black", "prettier").

Returns:
    bool: True if formatting succeeded, or error dict on failure.

Possible Failures:
    - Unsupported file type
    - Missing formatter binary
    - Invalid syntax in file

Suggestions:
    - Use `read_file()` to inspect file content first.
    - Ensure formatter is installed in runtime environment.
""",

"analyze_project_structure" : """
Scans a project directory and summarizes its structure.

Detects language distribution, file type breakdown, project type (e.g., Python, Node),
main directories (e.g., src/, tests/), config files, and overall stats.

Usage:
    await analyze_project_structure(".")

Args:
    path (str): Root directory to analyze.

Returns:
    Dict:
        - root_path (str)
        - total_files (int), total_size (bytes)
        - files_by_type (Dict[str, int])
        - languages (Dict[str, int])
        - project_type (str)
        - config_files (List[str])
        - main_directories (List[str])

Possible Failures:
    - Invalid or non-directory path
    - Permission denied while traversing

Suggestions:
    - Use `list_directory()` to verify path first.
    - Clean up large or unused directories before analyzing.
""",

"get_file_dependencies" : """
Extracts import or dependency statements from a source file.

Supports multiple languages (Python, JS/TS, Go, Rust, Java). Returns only
static imports; dynamic or runtime-loading statements are not detected.

Usage:
    await get_file_dependencies("main.py")

Args:
    file_path (str): Path to the file to scan.

Returns:
    List[str]: Lines representing dependency statements.

Possible Failures:
    - File not found or unreadable
    - Unsupported file type
    - Binary or non-text file

Suggestions:
    - Use `read_file()` to confirm text content.
    - Manually inspect complex import styles.
""",

"find_references" : """
Find references to a symbol in the codebase.

Searches for exact word-boundary matches across code files using `grep`. Can
be filtered by file type (e.g., only `.py` or `.js` files).

Usage:
    await find_references("my_function", file_types=[".py", ".pyi"])

Args:
    symbol (str): Symbol name to search for.
    file_types (List[str]): List of file extensions to restrict search.

Returns:
    List[Dict]:
        - symbol (str), file (str), line (int), content (str)

Possible Failures:
    - Symbol not found
    - Grep execution error

Suggestions:
    - Ensure symbol is a full identifier (e.g., function, class name).
    - Use `grep_files()` for more flexible pattern search.
"""
}
# print(tool_dic)

# tool_dic = {
#     'read_file': '\nReads content from a file with optional line-based pagination.\n\nThis tool is intended for reading text files only. It tracks read operations\nfor later validation in write/edit commands. If the file is binary or unreadable\ndue to permissions or encoding, it returns a structured error.\n\nUsage:\n    await read_file("README.md", offset=1, limit=50)\n\nArgs:\n    path (str): File path to read.\n    offset (Optional[int]): Starting line number (1-based). Defaults to config default.\n    limit (Optional[int]): Number of lines to read. Defaults to config default.\n    encoding (Optional[str]): Encoding to use. Defaults to system default.\n\nReturns:\n    FileReadResponse:\n        - content (str): File content (possibly truncated).\n        - lines_shown (int), total_lines (int), is_truncated (bool)\n\nPossible Failures:\n    - File not found\n    - Invalid encoding\n    - Binary file (unsupported)\n    - Permission issues\n\nSuggestions:\n    - Use `list_directory()` or `glob_files()` to find valid file paths.\n    - Ensure encoding matches file format.\n',
#     'write_file': '\nWrites text content to a file, with overwrite protection.\n\nTo avoid accidental modification of unknown files, writing to an existing file\nrequires it to have been read first — unless `force=True`.\n\nUsage:\n    await write_file("example.txt", "new content", force=True)\n\nArgs:\n    path (str): Path to file to write.\n    content (str): Text content to write.\n    force (bool): Set to True to bypass read-before-write check.\n    encoding (Optional[str]): Text encoding (default: system default).\n\nReturns:\n    FileWriteResponse:\n        - bytes_written (int)\n\nPossible Failures:\n    - Path invalid or unwritable\n    - File not read beforehand (if force=False)\n    - Permission or disk issues\n\nSuggestions:\n    - Use `read_file()` before editing.\n    - Set `force=True` if you\'re sure you want to overwrite.\n',
#     'edit_file': '\nPerforms text replacement in a file.\n\nSupports both single and full replacement modes. The file must be read first\nbefore edits are allowed for safety.\n\nUsage:\n    await edit_file("code.py", "old_function()", "new_function()", replace_all=True)\n\nArgs:\n    path (str): Path to the file to edit.\n    old_string (str): Text to search for.\n    new_string (str): Replacement text.\n    replace_all (bool): If True, replace all instances. Default is first match only.\n\nReturns:\n    FileEditResponse:\n        - replacements_made (int)\n        - preview (str): Change preview (first line diff)\n\nPossible Failures:\n    - File unread or not previously read\n    - Match string not found\n    - Write failure after edit\n\nSuggestions:\n    - Use `read_file()` before edit.\n    - Ensure exact match in whitespace and formatting.\n',
#     'list_directory': '\nLists files and directories in a path with metadata.\n\nSupports ignore patterns (regex) for filtering out noisy entries such as `.git`\nor `node_modules`.\n\nUsage:\n    await list_directory(".", ignore=["__pycache__"])\n\nArgs:\n    path (str): Path to the directory to list.\n    ignore (List[str]): Regex patterns to ignore (e.g., r"\\.git", r"__pycache__").\n\nReturns:\n    List[Dict]:\n        - name, path, type ("file"/"directory"), size, is_text, etc.\n\nPossible Failures:\n    - Invalid or inaccessible directory path\n    - Permission issues\n\nSuggestions:\n    - Use `glob_files()` to match specific file types.\n    - Double-check directory path if result is empty.\n',
#     'create_bash_session': '\nCreates a named persistent bash session.\n\nSessions preserve environment, working directory, and state across commands.\nUse when chaining multiple operations or running interactive shells.\n\nUsage:\n    await create_bash_session("dev-shell")\n\nArgs:\n    session_name (Optional[str]): Name for the session. Defaults to config.\n\nReturns:\n    ToolResponse with session creation status.\n\nPossible Failures:\n    - Session already exists\n\nSuggestions:\n    - Use `get_bash_sessions()` to list existing ones.\n    - Use `close_bash_session()` to close stale sessions.\n',
#     'run_command': '\nExecutes a one-time shell command in non-interactive mode.\n\nRecommended for simple commands with no state persistence.\nAvoid using for REPLs, interactive scripts, or multi-step commands.\n\nUsage:\n    await run_command("ls -al", directory="src")\n\nArgs:\n    command (str): Shell command to run.\n    directory (Optional[str]): Working directory.\n\nReturns:\n    CommandResponse:\n        - stdout, stderr, exit_code, command\n\nPossible Failures:\n    - Command not found\n    - Syntax errors\n    - Permission issues\n\nSuggestions:\n    - Use `run_bash_session()` for stateful or interactive operations.\n',
#     'run_bash_session': '\nRuns a command in a persistent interactive bash session.\n\nUse this for programs that require input/output interactivity,\nenvironment continuity, or multi-step workflows.\n\nSuggestion : \nInteractive commands (use interactiev=False more often): Avoid commands that require interactive user input, as this can cause the tool to hang. Use non-interactive flags if available (e.g., npm init -y).\n\nUsage:\n    await run_bash_session("python3", session_name="py-dev", interactive=True)\n\nArgs:\n    command (str): Command to run.\n    session_name (Optional[str]): Session name. Defaults to config.\n    timeout (Optional[float]): Max run time in seconds.\n    interrupt (bool): Interrupt session instead of running command.\n    interactive (Optional[bool]): Force interactive mode. checks using possible interactive expects using pyexpect.\n\nReturns:\n    CommandResponse:\n        - stdout, stderr, session_name, is_interactive, expect_string\n\nPossible Failures:\n    - Session creation failed\n    - Unexpected command behavior in interactive mode\n\nSuggestions:\n    - Avoid long-running sessions without timeout.\n    - Use `interrupt=True` to stop hanging sessions.\n',
#     'glob_files': '\nSearch for a regex pattern across multiple files.\n\nSupports directory-wide search using `grep` combined with `find`. Useful for\ntracing usage of functions, variables, or keywords. Allows file filtering via extension.\n\nUsage:\n    await grep_files(pattern="def ", path="src", include="*.py")\n\nArgs:\n    pattern (str): Regex pattern to search for (e.g., "import .*").\n    path (str): Base directory to search in.\n    include (str): File glob to restrict search scope (e.g., "*.js").\n\nReturns:\n    List[Dict]:\n        - file (str): File path\n        - line (int): Line number\n        - content (str): Line text\n\nPossible Failures:\n    - No matches\n    - Invalid regex\n    - Permission errors on files\n\nSuggestions:\n    - Use `glob_files()` first to preview candidate files.\n    - Keep patterns simple for performance.\n',
#     'format_code': '\nFormat a source code file using the appropriate formatter.\n\nAuto-selects formatter based on file extension. Supports Python, JS/TS, Go,\nRust, C/C++, Java, and more. You can override the formatter explicitly.\n\nUsage:\n    await format_code("app.py")\n    await format_code("style.scss", formatter="prettier")\n\nArgs:\n    file_path (str): Path to the file to format.\n    formatter (Optional[str]): Formatter name (e.g., "black", "prettier").\n\nReturns:\n    bool: True if formatting succeeded, or error dict on failure.\n\nPossible Failures:\n    - Unsupported file type\n    - Missing formatter binary\n    - Invalid syntax in file\n\nSuggestions:\n    - Use `read_file()` to inspect file content first.\n    - Ensure formatter is installed in runtime environment.\n',
#     'analyze_project_structure': '\nScans a project directory and summarizes its structure.\n\nDetects language distribution, file type breakdown, project type (e.g., Python, Node),\nmain directories (e.g., src/, tests/), config files, and overall stats.\n\nUsage:\n    await analyze_project_structure(".")\n\nArgs:\n    path (str): Root directory to analyze.\n\nReturns:\n    Dict:\n        - root_path (str)\n        - total_files (int), total_size (bytes)\n        - files_by_type (Dict[str, int])\n        - languages (Dict[str, int])\n        - project_type (str)\n        - config_files (List[str])\n        - main_directories (List[str])\n\nPossible Failures:\n    - Invalid or non-directory path\n    - Permission denied while traversing\n\nSuggestions:\n    - Use `list_directory()` to verify path first.\n    - Clean up large or unused directories before analyzing.\n',
#     'get_file_dependencies': '\nExtracts import or dependency statements from a source file.\n\nSupports multiple languages (Python, JS/TS, Go, Rust, Java). Returns only\nstatic imports; dynamic or runtime-loading statements are not detected.\n\nUsage:\n    await get_file_dependencies("main.py")\n\nArgs:\n    file_path (str): Path to the file to scan.\n\nReturns:\n    List[str]: Lines representing dependency statements.\n\nPossible Failures:\n    - File not found or unreadable\n    - Unsupported file type\n    - Binary or non-text file\n\nSuggestions:\n    - Use `read_file()` to confirm text content.\n    - Manually inspect complex import styles.\n',
#     'find_references': '\nFind references to a symbol in the codebase.\n\nSearches for exact word-boundary matches across code files using `grep`. Can\nbe filtered by file type (e.g., only `.py` or `.js` files).\n\nUsage:\n    await find_references("my_function", file_types=[".py", ".pyi"])\n\nArgs:\n    symbol (str): Symbol name to search for.\n    file_types (List[str]): List of file extensions to restrict search.\n\nReturns:\n    List[Dict]:\n        - symbol (str), file (str), line (int), content (str)\n\nPossible Failures:\n    - Symbol not found\n    - Grep execution error\n\nSuggestions:\n    - Ensure symbol is a full identifier (e.g., function, class name).\n    - Use `grep_files()` for more flexible pattern search.\n'
#     }
