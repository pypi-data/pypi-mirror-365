

"""
Dear Reader: Interactive Notebook Kernel for HeartbreakCode.

This module provides the core logic for running HeartbreakCode within interactive notebook
environments like Jupyter or Visual Studio Code. It enables cell-by-cell execution,
rich output display for 'Tracklists' and 'Liner Notes', and integration with Markdown.
"""

def execute_heartbreak_code_cell(code_cell_content: str) -> dict:
    """
    Executes a single cell of HeartbreakCode and returns the output.

    Args:
        code_cell_content (str): The HeartbreakCode source code within a notebook cell.

    Returns:
        dict: A dictionary containing the execution results, including stdout, stderr, and rich outputs.
    """
    print("Executing HeartbreakCode cell...")
    # Placeholder for actual HeartbreakCode interpreter execution
    # This would typically involve calling the main interpreter logic.
    try:
        # Simulate execution and capture output
        simulated_output = f"// Cell executed successfully.\n// Output for: \'{code_cell_content[:50]}...\''"
        return {
            "status": "ok",
            "stdout": simulated_output,
            "stderr": "",
            "rich_output": {
                "mime_type": "text/plain",
                "data": simulated_output
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e),
            "rich_output": {
                "mime_type": "text/plain",
                "data": f"// Error during cell execution: {e}"
            }
        }

def display_tracklist_as_rich_output(tracklist_data: dict) -> dict:
    """
    Formats and returns a 'Tracklist' (dictionary) for rich display in a notebook.

    Args:
        tracklist_data (dict): A dictionary representing a HeartbreakCode tracklist.

    Returns:
        dict: A dictionary suitable for rich output display in a notebook.
    """
    print("Displaying Tracklist as rich output...")
    formatted_html = "<h3>Tracklist:</h3><ul>"
    for song, lyrics in tracklist_data.items():
        formatted_html += f"<li><b>{song}:</b> {lyrics[:50]}...</li>"
    formatted_html += "</ul>"
    return {
        "mime_type": "text/html",
        "data": formatted_html
    }

def display_liner_notes_as_markdown(liner_notes_content: str) -> dict:
    """
    Formats and returns 'Liner Notes' (text) as Markdown for rich display.

    Args:
        liner_notes_content (str): The text content of the liner notes.

    Returns:
        dict: A dictionary suitable for rich output display in a notebook.
    """
    print("Displaying Liner Notes as Markdown...")
    return {
        "mime_type": "text/markdown",
        "data": liner_notes_content
    }

