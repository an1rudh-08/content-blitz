import streamlit as st
import requests
from rich.console import Console

# Initialize Rich Console for logging UI actions to the terminal
console = Console()

def log_ui_action(action: str, details: str):
    """
    Helper function to log UI actions to the terminal.
    This helps visualize the frontend's activity alongside the backend logs.
    """
    console.print(f"[bold cyan]Frontend:[/bold cyan] {action} - {details}")

# [INIT] Set up the Streamlit page configuration
st.set_page_config(page_title="ContentBlitz AI", page_icon="🤖")

st.title("🤖 ContentBlitz AI Agent")
st.markdown("Powered by **Google Gemini** and **FastAPI**")

# [UI COMPONENT] Text Area for User Input
# This is where the user types their question.
query = st.text_area("Enter your query:", height=100)

# [UI COMPONENT] Button to trigger the action
if st.button("Ask Agent", type="primary"):
    # Check if the query is empty
    if not query.strip():
        st.warning("Please enter a query.")
        log_ui_action("Warning", "Empty query submitted")
    else:
        # [LOGGING] Log the user action
        log_ui_action("Action", f"User submitted query: '{query}'")
        
        # [UI FEEDBACK] Show a spinner while waiting for the response
        with st.spinner("Thinking..."):
            try:
                # [API CALL] Send the query to the Backend API
                log_ui_action("API Call", "Sending request to backend...")
                response = requests.post("http://localhost:8000/query", json={"query": query})
                
                # Check if the request was successful (HTTP 200)
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", "No response received.")
                    
                    # [LOGGING] Log success
                    log_ui_action("Success", "Received response from backend")
                    
                    # [UI DISPLAY] Show the response to the user
                    st.success("Response:")
                    st.markdown(answer)
                else:
                    # [ERROR HANDLING] Handle non-200 responses
                    log_ui_action("Error", f"Backend returned status {response.status_code}")
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                # [ERROR HANDLING] Handle connection errors (e.g., backend not running)
                log_ui_action("Error", "Could not connect to backend")
                st.error("Could not connect to the backend server. Is it running?")
            except Exception as e:
                # [ERROR HANDLING] Handle unexpected errors
                log_ui_action("Error", f"Unexpected error: {e}")
                st.error(f"An error occurred: {e}")
