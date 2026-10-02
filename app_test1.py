# app.py
import streamlit as st
import os
from dotenv import load_dotenv
import aisuite as ai

# Import your real tool
from tools_real import web_search

# Load environment variables (API keys)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🤖",
    layout="centered"
)

# --- Agent Setup (Cached so it doesn't reload on every message) ---
@st.cache_resource
def get_agent_and_client():
    system_prompt = """
    You are a meticulous Research Assistant. Your job is to answer research questions with accurate, well-sourced information.

    Follow this process:
    1. Deconstruct the user's question into researchable sub-questions.
    2. Use the `web_search` tool to find information for each sub-question.
    3. Synthesize the findings into a clear, structured answer.
    4. Always cite your sources with URLs.

    IMPORTANT CONTEXT: 
    - "aisuite" is a specific open-source Python library created by Andrew Ng. It is NOT related to ASUS hardware or "AI Suite" software. Always search for "aisuite" as a single word.
    - If the `web_search` tool returns a "Direct Answer:", use that as your primary source of truth.
    - If the `web_search` tool returns "No specific results" after 2 attempts, STOP searching. Use your own internal knowledge to answer the question and clearly state that you could not find external sources.

    Never make up information. Never get stuck in a loop.
    """
    
    agent = ai.Agent(
        name="ResearchAssistant",
        model="groq:openai/gpt-oss-120b",
        instructions=system_prompt,
        tools=[web_search],
    )
    
    client = ai.Client()
    return agent, client

# Initialize the agent and client
agent, client = get_agent_and_client()

# --- UI Header ---
st.title("🤖 AI Research Agent")
st.markdown("Ask me anything. I'll search the web, synthesize the findings, and give you a cited report.")
st.divider()

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
if prompt := st.chat_input("What would you like me to research?"):
    
    # 1. Display the user's message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Add the user's message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Generate the agent's response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Researching... (this may take a moment)"):
            try:
                # Run the agent
                result = ai.Runner.run_sync(
                    agent,
                    prompt,
                    client=client,
                    max_turns=5,
                )
                
                # Extract the final output
                if result.final_output:
                    response = result.final_output
                else:
                    # Fallback if the agent didn't produce a final output
                    last_message = result.messages[-1]
                    if isinstance(last_message, dict):
                        response = f"Agent stopped without a final answer. Last message:\n\n{last_message.get('content', 'No content available')}"
                    else:
                        response = f"Agent stopped without a final answer. Last message:\n\n{last_message}"
                        
            except Exception as e:
                response = f"❌ An error occurred: {e}"
            
            # Display the agent's response
            st.markdown(response)
    
    # 4. Add the agent's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": response})