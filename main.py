# main.py
import os
from dotenv import load_dotenv
import aisuite as ai

from tools_real import web_search

load_dotenv()

# The agent's persona and instructions — this is the PLANNING pattern in action.
# I added the "IMPORTANT" section to prevent the agent from looping forever when a tool fails.
SYSTEM_PROMPT = """
You are a meticulous Research Assistant. Your job is to answer research questions with accurate, well-sourced information.

Follow this process:
1. Deconstruct the user's question into researchable sub-questions.
2. Use the `web_search` tool to find information for each sub-question.
3. Synthesize the findings into a clear, structured answer.
4. Always cite your sources with URLs.

IMPORTANT CONTEXT: 
- "aisuite" is a specific open-source Python library created by Andrew Ng. It is NOT related to ASUS hardware or "AI Suite" software. Always search for "aisuite" as a single word.
- If the `web_search` tool returns "No specific results" after 2 attempts, STOP searching. Use your own internal knowledge to answer the question and clearly state that you could not find external sources.

Never make up information. Never get stuck in a loop.
"""

def create_agent():
    return ai.Agent(
        name="ResearchAssistant",
        model="groq:openai/gpt-oss-120b",  # Change this one string to swap providers
        instructions=SYSTEM_PROMPT,
        tools=[web_search],
    )

def main():
    print("🤖 Research Agent ready. Type 'quit' to exit.\n")
    
    client = ai.Client()
    agent = create_agent()
    
    while True:
        query = input("Your research question: ").strip()
        if not query or query.lower() == "quit":
            break
        
        print("\n🧠 Thinking...")
        result = ai.Runner.run_sync(
            agent,
            query,
            client=client,
            max_turns=5,  # Cap tool calls to prevent runaway loops
        )
        
        print("\n" + "=" * 60)
        print("📄 FINAL REPORT")
        print("=" * 60)
        
        # This is the updated logic to handle the agent's final response cleanly
        if result.final_output:
            print(result.final_output)
        else:
            # If no final output, print the last message from the agent
            print("Agent stopped without a final answer. Last message:")
            # Safely access the last message dictionary to avoid another crash
            last_message = result.messages[-1]
            if isinstance(last_message, dict):
                print(last_message.get("content", "No content available"))
            else:
                print(last_message)
                
        print()

if __name__ == "__main__":
    main()