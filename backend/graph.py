import os
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from duckduckgo_search import DDGS

# Load environment variables
load_dotenv()

# Initialize Gemini Model
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found")

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)

# --- State Definition ---
class AgentState(TypedDict):
    request: str
    research_data: str
    content_plan: str
    blog_post: str
    linkedin_post: str
    image_prompt: str
    image_url: str
    logs: Annotated[List[str], operator.add]

# --- Tools ---
def run_search(query: str) -> str:
    """
    Runs a DuckDuckGo search and returns the results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            return str(results)
    except Exception as e:
        return f"Search failed: {e}"

# --- Nodes ---

def research_node(state: AgentState):
    """
    Deep Research Agent: Conducts comprehensive web research.
    """
    query = state['request']
    state['logs'].append(f"Researcher: Searching for '{query}'...")
    
    # Perform search
    search_results = run_search(f"{query} latest trends facts")
        
    return {
        "research_data": search_results,
        "logs": [f"Researcher: Found data on '{query}'."]
    }

def strategist_node(state: AgentState):
    """
    Content Strategist Agent: Formats and organizes research into a plan.
    """
    research = state['research_data']
    request = state['request']
    state['logs'].append("Strategist: Analyzing research and creating content plan...")
    
    prompt = f"""
    You are a Content Strategist.
    User Request: {request}
    Research Data: {research}
    
    Create a comprehensive content strategy. 
    1. Identify the target audience.
    2. Define the core message.
    3. Outline the structure for a Blog Post and a LinkedIn Post.
    """
    response = llm.invoke(prompt)
    return {
        "content_plan": response.content,
        "logs": ["Strategist: Content plan created."]
    }

def seo_writer_node(state: AgentState):
    """
    SEO Blog Writer Agent: Creates search-optimized long-form content.
    """
    plan = state['content_plan']
    state['logs'].append("SEO Writer: Drafting blog post...")
    
    prompt = f"""
    You are an SEO Blog Writer.
    Content Plan: {plan}
    
    Write a high-quality, SEO-optimized blog post based on the plan.
    Include a catchy title, headers, and engaging content.
    """
    response = llm.invoke(prompt)
    return {
        "blog_post": response.content,
        "logs": ["SEO Writer: Blog post drafted."]
    }

def linkedin_writer_node(state: AgentState):
    """
    LinkedIn Post Writer Agent: Generates engaging professional social content.
    """
    plan = state['content_plan']
    state['logs'].append("LinkedIn Writer: Drafting social post...")
    
    prompt = f"""
    You are a LinkedIn Content Creator.
    Content Plan: {plan}
    
    Write an engaging LinkedIn post based on the plan.
    Use professional yet conversational tone, bullet points, and hashtags.
    """
    response = llm.invoke(prompt)
    return {
        "linkedin_post": response.content,
        "logs": ["LinkedIn Writer: Post drafted."]
    }

def image_gen_node(state: AgentState):
    """
    Image Generation Agent: Produces custom visuals (Prompts for now).
    """
    plan = state['content_plan']
    state['logs'].append("Designer: Creating visual concepts...")
    
    prompt = f"""
    You are a Visual Designer.
    Content Plan: {plan}
    
    Create a detailed image generation prompt for DALL-E 3 or Midjourney that would visually represent this content.
    """
    response = llm.invoke(prompt)
    
    # In a real scenario, we would call an Image Gen API here.
    # For now, we return the prompt and a placeholder URL.
    return {
        "image_prompt": response.content,
        "image_url": "https://placehold.co/600x400?text=AI+Generated+Image",
        "logs": ["Designer: Image prompt created."]
    }

# --- Graph Construction ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("researcher", research_node)
workflow.add_node("strategist", strategist_node)
workflow.add_node("seo_writer", seo_writer_node)
workflow.add_node("linkedin_writer", linkedin_writer_node)
workflow.add_node("designer", image_gen_node)

# Add Edges
# Flow: Research -> Strategy -> (SEO Writer, LinkedIn Writer, Designer) -> End
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "strategist")
workflow.add_edge("strategist", "seo_writer")
workflow.add_edge("strategist", "linkedin_writer")
workflow.add_edge("strategist", "designer")
workflow.add_edge("seo_writer", END)
workflow.add_edge("linkedin_writer", END)
workflow.add_edge("designer", END)

# Compile
app = workflow.compile()
