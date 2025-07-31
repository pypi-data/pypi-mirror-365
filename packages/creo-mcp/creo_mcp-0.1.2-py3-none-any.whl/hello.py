import io
import traceback
import json
from contextlib import redirect_stdout
import creopyson
from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("python-code-executor")


def get_creo_connection():
    c = creopyson.Client()
    c.connect()
    if not c.is_creo_running():
        raise Exception("Creo is not running")
    return c


@mcp.tool()
def execute_python_code(code: str) -> str:
    """
    Execute arbitrary Python code. Make sure to do it step-by-step by breaking it into smaller chunks.

    Parameters:
    - code: The Python code to execute

    Returns:
        A string containing the standard output of the executed code
        or an error message if the code fails.
    """
    # ctx.info(f"Attempting to execute the following code:\n---\n{code}\n---")

    # Use StringIO to create an in-memory text buffer to capture stdout
    try:
        # The 'with' statement ensures that stdout is restored even if errors occur
        exec(code)
        return "Code executed successfully"

    except Exception as e:
        # Capture the full traceback to return to the LLM for debugging
        # The traceback module provides more detail than just the exception message
        error_details = traceback.format_exc()
        return f"An error occurred:\n---\n{error_details}"


@mcp.tool()
def open_file_in_cad(file_path: str, name: str, dirname: str) -> str:
    """Opens a file in CAD software and returns the file path.

    Parameters:
    - file_path: The path to the file to open in CAD software.
    - name: The name to give the file in CAD software.
    - dirname: The absolute path to the directory which contains the file.

    Returns:
        The path to the file opened in CAD software.
    """
    try:
        c = get_creo_connection()
        path = c.interface_import_file(
            filename=file_path,
            file_type="STEP",
            new_name=name,
            new_model_type="prt",
            dirname=dirname,
        )
        c.file_open(path, display=True)
        return path
    except Exception as e:
        return f"An error occurred:\n---\n{e}"


@mcp.tool()
def print_something(text: str) -> str:
    """Prints the given text to the console.

    Parameters:
    - text: The text to print to the console.

    Returns:
        The text that was printed to the console.
    """
    try:
        print(text)
        return f"Excuted successfully:\n---\n{text}"
    except Exception as e:
        return f"An error occurred:\n---\n{e}"


@mcp.tool()
def do_nothing() -> str:
    """Does nothing."""
    return "I did nothing."


KNOWLEDGE_BASE_DOMAIN = "api-knowledgebase.mlp.cn-beijing.volces.com"


@mcp.tool()
def retrieve_from_knowledge_base(
    query: str,
) -> str:
    """
    Performs a retrieval-type request from a Volcengine knowledge base service.
    This tool is designed for services configured for "retrieval", not "question-answering".
    It will return the list of retrieved document chunks without a generated answer.

    Parameters:
    - query (str): The search query or question to retrieve relevant documents for.

    Returns:
    - str: A JSON string containing the list of retrieved results ('result_list') or an error message.
    """
    try:
        # --- 1. Prepare Request Details ---
        api_path = "/api/knowledge/service/chat"
        request_url = f"http://{KNOWLEDGE_BASE_DOMAIN}{api_path}"

        # Set up the necessary headers, including authentication
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "Bearer 8b71a257-1138-40a2-b478-2798926f4151",
        }

        # --- 2. Construct the Request Payload ---
        # The 'messages' array should contain the current user query
        payload = {
            "service_resource_id": "kb-service-ecff228107ae9d6",
            "messages": [{"role": "user", "content": query}],
            "stream": False,  # Set to False for a single, complete retrieval response
        }

        # --- 3. Make the API Call ---
        response = requests.post(
            request_url,
            headers=headers,
            json=payload,
            timeout=30,  # Set a reasonable timeout for the request
        )

        # Check for HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
        response.raise_for_status()

        # Ensure the response is decoded correctly
        response.encoding = "utf-8"

        # Return the raw JSON response as a string
        return response.text

    except requests.exceptions.RequestException as e:
        # Handle network-related errors and bad HTTP status codes
        error_body = e.response.text if e.response else "No response body"
        return f"An HTTP error occurred: {e}\nResponse: {error_body}"
    except Exception:
        # Handle any other unexpected errors and provide a detailed traceback
        error_details = traceback.format_exc()
        return f"An unexpected error occurred:\n---\n{error_details}"


if __name__ == "__main__":
    mcp.run()
