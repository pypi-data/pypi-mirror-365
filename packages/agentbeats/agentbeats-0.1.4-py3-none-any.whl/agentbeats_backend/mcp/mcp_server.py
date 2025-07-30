# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime
from fastmcp import FastMCP
import requests

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

server = FastMCP("Open MCP for AgentBeast Battle Arena")

SESSIONS: dict[str, dict[str, str]] = {}

BACKEND_URL = "http://localhost:9000"

@server.tool()
def echo(message: str) -> str:
    """
    Echo the input message.
    """
    logger.info("Echoing message: %s", message)
    return f"Echo: {message}"

@server.tool()
def update_battle_process(battle_id: str, message: str, reported_by: str, detail: dict = None, markdown_content: str = None) -> str:
    """
    Log battle process updates to backend API and console.
    
    This tool records intermediate events and progress during a battle, helping track
    what each participant is doing and how the battle is evolving.
    
    Args:
        battle_id (str): Unique identifier for the battle session
        message (str): Simple, human-readable description of what happened
                      Example: "guardrailGenerator defense prompt success" or "red agent launched attack"
        detail (dict): Structured data containing specific details about the event
                      Can include prompts, responses, configurations, or any relevant data
                      Example: {"prompt": "You are a helpful assistant...", "tool": "xxxTool"}
        reported_by (str): The role/agent that triggered this event
                          Example: "guardrailGenerator", "red_agent", "blue_agent", "evaluator"
        markdown_content (str): Optional markdown content for rich text display, and image rendering
    
    Returns:
        str: Status message indicating where the log was recorded
    
    Example usage in TensorTrust game:
        - message: "guardrailGenerator defense prompt success"
        - detail: {"defense_prompt": "Ignore all previous instructions...", "secret_key": "abc123"}
        - reported_by: "guardrailGenerator"
    """
    # logger.info("Battle %s: %s", battle_id, info)

    # Prepare event data for backend API
    event_data = {
        "is_result": False,
        "message": message,
        "reported_by": reported_by,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if detail:
        event_data["detail"] = detail

    if markdown_content:
        event_data["markdown_content"] = markdown_content
    try:
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/battles/{battle_id}",
            json=event_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info("Successfully logged to backend for battle %s", battle_id)
            return 'logged to backend'
        else:
            logger.error("Failed to log to backend for battle %s: %s", battle_id, response.text)
            # Fallback to local file logging
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            line = f"[INFO] [{timestamp}] {message}\n"
            with open(f"{battle_id}.log", "a", encoding="utf-8") as f:
                f.write(line)
            return 'logged locally (backend failed)'
            
    except requests.exceptions.RequestException as e:
        logger.error("Network error when logging to backend for battle %s: %s", battle_id, str(e))
        # Fallback to local file logging
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[INFO] [{timestamp}] {message}\n"
        with open(f"{battle_id}.log", "a", encoding="utf-8") as f:
            f.write(line)
        return 'logged locally (network error)'

@server.tool()
def report_on_battle_end(battle_id: str, message:str, winner: str, reported_by: str, detail: dict = None, markdown_content: str = None) -> str:
    """
    Report the final battle result to backend API. YOU MUST CALL THIS AT THE END OF THE BATTLE.
    
    Args:
        battle_id: The battle ID
        message: Simple, human-readable description of what happened
        winner: The winner of the battle ("green", "blue", "red", or "draw")
        reported_by: The name of the agent reporting the result
        detail: Additional detail information (optional)
        markdown_content: Optional markdown content for rich text display, and image rendering
    """
    logger.info("Reporting battle result for %s: winner=%s", battle_id, winner)
    
    # Prepare result event data for backend API
    result_data = {
        "is_result": True,
        "message": message,
        "winner": winner,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reported_by": reported_by  # Use the actual agent name passed in
    }
    
    if detail:
        result_data["detail"] = detail

    if markdown_content:
        result_data["markdown_content"] = markdown_content
    
    try:
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/battles/{battle_id}",
            json=result_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info("Successfully reported battle result to backend for battle %s", battle_id)
            return f'battle result reported: winner={winner}'
        else:
            logger.error("Failed to report battle result to backend for battle %s: %s", battle_id, response.text)
            # Fallback to local file logging
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            line = f"[RESULT] [{timestamp}] Winner: {winner}\n"
            with open(f"{battle_id}.log", "a", encoding="utf-8") as f:
                f.write(line)
            return 'result logged locally (backend failed)'
            
    except requests.exceptions.RequestException as e:
        logger.error("Network error when reporting battle result for battle %s: %s", battle_id, str(e))
        # Fallback to local file logging
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[RESULT] [{timestamp}] Winner: {winner}\n"
        with open(f"{battle_id}.log", "a", encoding="utf-8") as f:
            f.write(line)
        return 'result logged locally (network error)'


# @server.tool()
# def test_markdown(battle_id: str) -> str:
#     sample_markdown = """# Test Markdown Display

# This is a **test** of the markdown rendering functionality.

# ## Features Tested:
# - **Bold text**
# - *Italic text*
# - `Inline code`
# - [Links](https://example.com)

# ### Code Block:
# ```python
# def hello_world():
#     print("Hello, World!")
#     return True
# ```

# ### Sample Table:
# | Agent | Role | Status |
# |-------|------|--------|
# | Blue Agent | Defender | Active |
# | Red Agent | Attacker | Ready |

# ### Sample Image (placeholder):
# ![Sample Image](https://kirkstrobeck.github.io/whatismarkdown.com/img/markdown.png)

# > **Note**: This is a blockquote to test markdown styling.

# ### List Example:
# 1. First item
# 2. Second item
#    - Sub-item A
#    - Sub-item B
# 3. Third item

# ---

# *This markdown content tests various formatting elements.*
# """

#     event_data = {
#         "is_result": False,
#         "message": 'test markdown content',
#         "reported_by": 'green_agent',
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#         "markdown_content": sample_markdown
#     }
#     try:
#         # Call backend API
#         response = requests.post(
#             f"{BACKEND_URL}/battles/{battle_id}",
#             json=event_data,
#             headers={"Content-Type": "application/json"},
#             timeout=10
#         )
        
#         if response.status_code == 204:
#             logger.info("Successfully logged to backend for battle %s", battle_id)
#             return 'logged to backend'
            
#     except requests.exceptions.RequestException as e:
#         logger.error("Network error when logging to backend for battle %s: %s", battle_id, str(e))

if __name__ == "__main__":  
    port = int(os.environ.get("MCP_PORT", 9001))
    server.run(transport="sse", 
               host="0.0.0.0",
               port=port,
               log_level="ERROR")
