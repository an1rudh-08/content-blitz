import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel

# Initialize Rich Console for logging
console = Console()

def log_step(step: str, details: str, style: str = "bold blue"):
    """
    Helper function to log steps with Rich.
    Creates a visually distinct panel in the terminal for each major action.
    """
    console.print(Panel(f"[{style}]{step}[/{style}]\n{details}", title="Agent Log", border_style=style))

# [INIT] Load environment variables from .env file
log_step("Initialization", "Loading environment variables...")
load_dotenv()

# [INIT] Check for API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    log_step("Error", "GOOGLE_API_KEY not found!", style="bold red")
    raise ValueError("GOOGLE_API_KEY not found")
else:
    log_step("Initialization", "API Key found.", style="bold green")

# [INIT] Configure Gemini API
try:
    log_step("Configuration", "Configuring Google Gemini API...")
    genai.configure(api_key=api_key)
    
    # Initialize the model
    # We are using 'gemini-flash-latest' as it was verified to be available.
    model = genai.GenerativeModel('gemini-flash-latest')
    log_step("Configuration", "Model 'gemini-flash-latest' initialized successfully.", style="bold green")
except Exception as e:
    log_step("Error", f"Failed to configure Gemini: {e}", style="bold red")
    raise

def generate_response(prompt: str) -> str:
    """
    Generates a response from the Gemini model for the given prompt.
    Includes intensive logging of the process.
    
    Flow:
    1. Logs the start of the request and the received prompt.
    2. Sends the prompt to Google Gemini via the SDK.
    3. Measures the time taken for the API call.
    4. Logs the successful response and the duration.
    5. Returns the text content of the response.
    """
    start_time = time.time()
    
    # [LOGGING] Log the received prompt
    log_step("Action", f"Received prompt: '{prompt}'", style="bold yellow")

    try:
        # [STEP 1] Call the Google Gemini API
        log_step("API Call", "Sending request to Google Gemini...", style="bold cyan")
        response = model.generate_content(prompt)
        
        # [TIMING] Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        
        # [LOGGING] Log success and details
        log_step("API Response", f"Received response in {duration:.2f}s", style="bold green")
        log_step("Content", f"Response text: {response.text[:100]}...", style="dim")
        
        return response.text
    except Exception as e:
        # [ERROR HANDLING] Log any API errors
        log_step("Error", f"Error during generation: {e}", style="bold red")
        return f"Error: {e}"
