from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend import agent
from rich.console import Console

# Initialize the FastAPI application
# This app acts as the central server for our AI application.
app = FastAPI(title="ContentBlitz AI Agent")

# Initialize Rich Console for pretty logging in the terminal
console = Console()

# Define the data model for the request body
# This ensures that the client sends a JSON object with a "query" field which is a string.
class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    """
    Root endpoint to verify that the server is running.
    """
    return {"message": "ContentBlitz AI Agent API is running"}

@app.post("/query")
def query_agent(request: QueryRequest):
    """
    Endpoint to process user queries via the Multi-Agent System.
    
    Flow:
    1. Receives a POST request with a user query.
    2. Logs the receipt of the query.
    3. Calls the `agent.run_multi_agent_system` function.
    4. Logs the successful receipt of the structured response.
    5. Returns the structured response (Research, Plan, Content, Images) to the client.
    """
    # [LOGGING] Log the incoming query to the console
    console.print(f"[bold magenta]Backend:[/bold magenta] Received query: '{request.query}'")
    
    try:
        # [STEP 1] Delegate the query processing to the Agent module
        console.print("[bold magenta]Backend:[/bold magenta] Delegating to Multi-Agent System...")
        
        # This function call triggers the LangGraph workflow
        response_data = agent.run_multi_agent_system(request.query)
        
        # [STEP 2] Log success after receiving the response
        console.print("[bold magenta]Backend:[/bold magenta] Workflow completed successfully.")
        
        # [STEP 3] Return the result as a JSON response
        return response_data
        
    except Exception as e:
        # [ERROR HANDLING] Log any errors and return a 500 status code
        console.print(f"[bold red]Backend Error:[/bold red] {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the server using Uvicorn
    # host="0.0.0.0" makes it accessible from other machines (if needed)
    # port=8000 is the standard port for FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
