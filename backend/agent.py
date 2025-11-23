import time
from rich.console import Console
from rich.panel import Panel
from backend.graph import app as graph_app

# Initialize Rich Console for logging
console = Console()

def log_step(step: str, details: str, style: str = "bold blue"):
    """
    Helper function to log steps with Rich.
    """
    console.print(Panel(f"[{style}]{step}[/{style}]\n{details}", title="Agent Log", border_style=style))

def run_multi_agent_system(prompt: str) -> dict:
    """
    Runs the Multi-Agent Content System using LangGraph.
    
    Flow:
    1. Initializes the graph state with the user request.
    2. Invokes the graph.
    3. Collects outputs from all agents.
    4. Returns a structured dictionary with all content pieces.
    """
    start_time = time.time()
    log_step("Action", f"Starting Multi-Agent System for: '{prompt}'", style="bold yellow")

    try:
        # [STEP 1] Initialize State
        initial_state = {
            "request": prompt,
            "logs": []
        }
        
        # [STEP 2] Invoke Graph
        log_step("Orchestration", "Invoking LangGraph Workflow...", style="bold cyan")
        final_state = graph_app.invoke(initial_state)
        
        # [TIMING] Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        
        # [LOGGING] Log success
        log_step("Success", f"Workflow completed in {duration:.2f}s", style="bold green")
        
        # [STEP 3] Return Structured Output
        return {
            "research_data": final_state.get("research_data", ""),
            "content_plan": final_state.get("content_plan", ""),
            "blog_post": final_state.get("blog_post", ""),
            "linkedin_post": final_state.get("linkedin_post", ""),
            "image_prompt": final_state.get("image_prompt", ""),
            "image_url": final_state.get("image_url", ""),
            "logs": final_state.get("logs", [])
        }
        
    except Exception as e:
        log_step("Error", f"Workflow failed: {e}", style="bold red")
        raise e
