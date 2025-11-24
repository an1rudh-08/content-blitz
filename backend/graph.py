import os
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from ddgs import DDGS
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .FreeSearchAggregator import FreeSearchAggregator

# Load environment variables
load_dotenv()

# Initialize Rich Console
console = Console()

def log_node_start(node_name: str, input_data: str):
    """Logs the start of a node execution with input data."""
    console.print(Panel(Text(f"Input:\n{input_data}", style="cyan"), title=f"[bold green]Node Started: {node_name}[/bold green]", border_style="green"))

def log_node_end(node_name: str, output_data: str):
    """Logs the end of a node execution with output data."""
    console.print(Panel(Text(f"Output:\n{output_data}", style="yellow"), title=f"[bold blue]Node Finished: {node_name}[/bold blue]", border_style="blue"))

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
    node_details: Annotated[List[dict], operator.add]

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
        console.print(f"Search failed: {e}", style="bold red")
        return f"Search failed: {e}"

# --- Nodes ---

def research_node(state: AgentState):
    """
    Deep Research Agent: Conducts comprehensive web research.
    """
    query = state['request']
    log_node_start("Deep Research Agent", f"Query: {query}")
    state['logs'].append(f"Researcher: Searching for '{query}'...")
    
    # Perform search
    searcher = FreeSearchAggregator()

    # Search across multiple free sources
    raw_results = searcher.aggregate_search(
        query, 
        sources=["duckduckgo", "wikipedia", "reddit"]  # Choose your sources
    )
    
    log_node_end("Deep Research Agent", f"Found {len(raw_results)} chars of data")
    
    return {
        "research_data": raw_results,
        "logs": [f"Researcher: Found data on '{query}'."],
        "node_details": [{
            "node": "Deep Research Agent",
            "input": f"Query: {query}",
            "output": f"Search Results: {raw_results[:500]}..."
        }]
    }

def strategist_node(state: AgentState):
    """
    Content Strategist Agent: Formats and organizes research into a plan.
    """
    research = state['research_data']
    request = state['request']
    
    log_node_start("Content Strategist Agent", f"Request: {request}\nResearch Size: {len(research)} chars")
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
    
    log_node_end("Content Strategist Agent", f"Plan: {response.content[:200]}...")
    
    return {
        "content_plan": response.content,
        "logs": ["Strategist: Content plan created."],
        "node_details": [{
            "node": "Content Strategist Agent",
            "input": f"Request: {request}\nResearch Data: {research[:200]}...",
            "output": f"Content Plan: {response.content[:500]}..."
        }]
    }

def seo_writer_node(state: AgentState):
    """
    SEO Blog Writer Agent: Creates search-optimized long-form content.
    """
    plan = state['content_plan']
    log_node_start("SEO Blog Writer Agent", f"Plan Size: {len(plan)} chars")
    
    state['logs'].append("SEO Writer: Drafting blog post...")
    
    prompt = f"""
    You are an SEO Blog Writer.
    Content Plan: {plan}
    
    Write a high-quality, SEO-optimized blog post based on the plan.
    Include a catchy title, headers, and engaging content.
    """
    response = llm.invoke(prompt)
    
    log_node_end("SEO Blog Writer Agent", f"Blog Post: {response.content[:200]}...")
    
    return {
        "blog_post": response.content,
        "logs": ["SEO Writer: Blog post drafted."],
        "node_details": [{
            "node": "SEO Blog Writer Agent",
            "input": f"Content Plan: {plan[:200]}...",
            "output": f"Blog Post: {response.content[:500]}..."
        }]
    }

def linkedin_writer_node(state: AgentState):
    """
    LinkedIn Post Writer Agent: Generates engaging professional social content.
    """
    plan = state['content_plan']
    log_node_start("LinkedIn Writer Agent", f"Plan Size: {len(plan)} chars")
    
    state['logs'].append("LinkedIn Writer: Drafting social post...")
    
    prompt = f"""
    You are a LinkedIn Content Creator.
    Content Plan: {plan}
    
    Write an engaging LinkedIn post based on the plan.
    Use professional yet conversational tone, bullet points, and hashtags.
    """
    response = llm.invoke(prompt)
    
    log_node_end("LinkedIn Writer Agent", f"LinkedIn Post: {response.content[:200]}...")
    
    return {
        "linkedin_post": response.content,
        "logs": ["LinkedIn Writer: Post drafted."],
        "node_details": [{
            "node": "LinkedIn Writer Agent",
            "input": f"Content Plan: {plan[:200]}...",
            "output": f"LinkedIn Post: {response.content[:500]}..."
        }]
    }

def image_gen_node(state: AgentState):
    """
    Image Generation Agent: Produces custom visuals (Prompts for now).
    """
    plan = state['content_plan']
    log_node_start("Image Generation Agent", f"Plan Size: {len(plan)} chars")
    
    state['logs'].append("Designer: Creating visual concepts...")
    
    prompt = f"""
    You are a Visual Designer.
    Content Plan: {plan}
    
    Create a detailed image generation prompt for DALL-E 3 or Midjourney that would visually represent this content.
    """
    response = llm.invoke(prompt)
    image_prompt = response.content
    
    console.print(f"[bold magenta]Generated Prompt:[/bold magenta] {image_prompt}")
    state['logs'].append(f"Image prompt: '{image_prompt}'")

    # Generate actual image using DALL-E 3
    try:
        # Check for OpenAI Key
        if not os.getenv("OPENAI_API_KEY"):
             raise ValueError("OPENAI_API_KEY not found")
             
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = image_response.data[0].url
        log_node_end("Image Generation Agent", f"Image URL: {image_url}")
        
        return {
            "image_prompt": image_prompt,
            "image_url": image_url,
            "logs": ["Designer: Image generated successfully."],
            "node_details": [{
                "node": "Image Generation Agent",
                "input": f"Content Plan: {plan[:200]}...",
                "output": f"Image Prompt: {image_prompt}\nImage URL: {image_url}"
            }]
        }
    except Exception as e:
        console.print(f"[bold red]Image Generation Failed:[/bold red] {e}")
        return {
            "image_prompt": image_prompt,
            "image_url": "https://placehold.co/600x400?text=Image+Generation+Failed",
            "logs": [f"Designer: Image generation failed: {e}"],
            "node_details": [{
                "node": "Image Generation Agent",
                "input": f"Content Plan: {plan[:200]}...",
                "output": f"Error: {e}"
            }]
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
