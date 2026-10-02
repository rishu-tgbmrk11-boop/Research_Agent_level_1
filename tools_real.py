# tools_real.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def web_search(query: str) -> str:
    """
    Search the web for information about a given query.
    Returns a formatted summary of the top results with source URLs.
    """
    print(f"\n🔧 [TOOL] web_search(query='{query}')")
    
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not found in environment variables."

    # Tavily API endpoint
    url = "https://api.tavily.com/search"
    
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",  # 'basic' is cheaper/faster, 'advanced' is deeper
        "max_results": 2,         # Keep it small for the agent's context window
        "include_answer": True,
        "include_raw_content": False,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Format the results into a clean string for the LLM
        results = data.get("results", [])
        if not results:
            return f"No web results found for '{query}'."
        
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] {r.get('title', 'Untitled')}\n"
                f"URL: {r.get('url', 'No URL')}\n"
                f"Content: {r.get('content', 'No content')}\n"
            )
        
        return "\n---\n".join(formatted)
        
    except requests.exceptions.RequestException as e:
        return f"Error calling Tavily API: {e}"