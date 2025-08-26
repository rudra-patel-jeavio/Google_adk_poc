"""
Streamlit chat interface for the multi-agent content creation system.
Provides an interactive chat UI with workflow tracking and session management.
"""

import streamlit as st
import asyncio
import uuid
import nest_asyncio
from typing import Dict, List, Any
import sys
import os
from google.adk.events import Event

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.session_manager import session_manager

# Apply nest_asyncio for Streamlit compatibility
nest_asyncio.apply()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Content Creator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'workflow_status' not in st.session_state:
        st.session_state.workflow_status = {}
    
    if 'session_initialized' not in st.session_state:
        st.session_state.session_initialized = False

async def create_new_session():
    """Create a new ADK session."""
    try:
        session_id = await session_manager.create_session(
            user_id=st.session_state.user_id
        )
        st.session_state.session_id = session_id
        st.session_state.session_initialized = True
        st.session_state.messages = []
        st.session_state.workflow_status = {}
        return True
    except Exception as e:
        st.error(f"Failed to create session: {e}")
        return False

async def get_workflow_status():
    """Get current workflow status from session manager."""
    if st.session_state.session_id:
        try:
            status = await session_manager.get_workflow_status(
                st.session_state.user_id,
                st.session_state.session_id
            )
            st.session_state.workflow_status = status
            return status
        except Exception as e:
            st.error(f"Failed to get workflow status: {e}")
            return {}
    return {}

async def send_message(message: str):
    """Send a message to the multi-agent system."""
    print(f"Sending message: {message}")
    if not st.session_state.session_id:
        st.error("No active session. Please start a new session.")
        return
    
    try:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": message
        })
        
        # Get response from agent system with tracking
        result = await session_manager.run_agent_with_tracking(
            st.session_state.user_id,
            st.session_state.session_id,
            message
        )
        
        # Extract response and agent information
        response = result["response"]
        agents_called = result["agents_called"]
        total_agents = result["total_agents"]
        execution_flow = result["execution_flow"]
        llm_calls = result.get("llm_calls", [])
        total_llm_calls = result.get("total_llm_calls", 0)
        llm_call_stats = result.get("llm_call_stats", {})
        
        # Create agent tracking info string
        agent_info = f"\n\n---\n**🤖 Agents & LLM Calls:**\n"
        agent_info += f"• **Total LLM Calls:** {total_llm_calls}\n"
        agent_info += f"• **Agents Used:** {total_agents}\n\n"
        
        # Show LLM calls per agent
        if llm_call_stats:
            agent_info += "**📞 LLM Calls by Agent:**\n"
            sorted_agents = sorted(llm_call_stats.items(), key=lambda x: x[1]["total_calls"], reverse=True)
            for agent_name, stats in sorted_agents:
                agent_info += f"• {agent_name}: {stats['total_calls']} calls"
                if stats['function_calls'] > 0:
                    agent_info += f" ({stats['function_calls']} with functions)"
                agent_info += "\n"
        
        # Add execution flow summary
        if execution_flow:
            agent_info += f"\n**📊 Execution Flow:** {len(execution_flow)} events\n"
            for i, event in enumerate(execution_flow[:5]):  # Show first 5 events
                if event.get("type") == "transfer":
                    agent_info += f"{i+1}. Transfer: {event['details']['from_agent']} → {event['details']['to_agent']}\n"
                else:
                    agent_info += f"{i+1}. {event['agent_name']} (ID: {event['event_id'][:8]}...)\n"
            if len(execution_flow) > 5:
                agent_info += f"... and {len(execution_flow) - 5} more events\n"
        
        # Add agent response to chat with tracking info
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response + agent_info
        })

        # Print agent response and triggered agent info
        print(f"\n\n=== AGENT RESPONSE ===")
        print(f"Agent Response: {response}")
        print(f"Agents Called: {[agent['agent_name'] for agent in agents_called]}")
        print(f"Total Agents: {total_agents}")
        print(f"Total LLM Calls: {total_llm_calls}")
        if llm_call_stats:
            print("LLM Calls by Agent:")
            for agent_name, stats in llm_call_stats.items():
                print(f"  • {agent_name}: {stats['total_calls']} calls")
        print(f"\n\n=== END AGENT RESPONSE ===\n\n")
        
        # Update workflow status
        await get_workflow_status()
        
        return response
    except Exception as e:
        st.error(f"Failed to send message: {e}")
        return None

def display_workflow_progress():
    """Display workflow progress in the sidebar."""
    st.sidebar.markdown("### 📊 Workflow Progress")
    
    if not st.session_state.workflow_status:
        st.sidebar.info("Start chatting to see workflow progress!")
        return
    
    status = st.session_state.workflow_status
    current_step = status.get('current_step', 'starting')
    
    # Progress steps
    steps = [
        ("💡 Ideas", "ideas_generated", "Ideas have been generated"),
        ("📋 Outline", "outline_created", "Content outline created"),
        ("📝 Draft", "draft_written", "Content draft written"),
        ("👨‍💼 Feedback", "feedback_received", "Expert feedback provided"),
        ("🔍 SEO", "seo_optimized", "Content SEO optimized")
    ]
    
    st.sidebar.markdown("**Current Step:** " + current_step.replace('_', ' ').title())
    
    for step_name, step_key, step_desc in steps:
        if status.get(step_key, False):
            st.sidebar.success(f"✅ {step_name}")
        else:
            st.sidebar.info(f"⏳ {step_name}")
    
    # Show available data
    if status.get('available_data'):
        st.sidebar.markdown("### 📦 Available Data")
        for data_key in status['available_data']:
            st.sidebar.text(f"• {data_key}")

def display_session_info():
    """Display session information in the sidebar."""
    st.sidebar.markdown("### 🔧 Session Info")
    
    if st.session_state.session_initialized:
        st.sidebar.success("✅ Session Active")
        st.sidebar.text(f"Session ID: {st.session_state.session_id[:8]}...")
    else:
        st.sidebar.warning("⚠️ No Active Session")
    
    # Session controls
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 New Session", help="Start a new conversation"):
            asyncio.run(create_new_session())
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat", help="Clear chat messages"):
            st.session_state.messages = []
            st.rerun()

def display_agent_info():
    """Display information about available agents."""
    with st.sidebar.expander("🤖 Available Agents"):
        agents_info = {
            "💡 Ideate Agent": "Generates creative ideas and concepts",
            "📋 Outline Agent": "Creates structured content outlines", 
            "📝 Draft Agent": "Writes complete content drafts",
            "👨‍💼 Persona Feedback": "Provides expert feedback and chat",
            "🔍 SEO Agent": "Optimizes content for search engines"
        }
        
        for agent, description in agents_info.items():
            st.markdown(f"**{agent}**")
            st.text(description)
            st.markdown("---")

def display_quick_actions():
    """Display quick action buttons."""
    st.sidebar.markdown("### ⚡ Quick Actions")
    
    quick_actions = [
        ("💡 Generate Ideas", "Give me some creative ideas for a blog post about artificial intelligence"),
        ("📋 Create Outline", "Create an outline for my content"),
        ("📝 Write Draft", "Write a draft based on the outline"),
        ("💬 Get Feedback", "I'd like feedback on my content"),
        ("🔍 SEO Optimize", "Optimize my content for SEO")
    ]
    
    for action_name, action_prompt in quick_actions:
        if st.sidebar.button(action_name, key=f"quick_{action_name}"):
            st.session_state.quick_message = action_prompt

def display_agent_tracking():
    """Display agent and LLM call tracking information in the sidebar."""
    with st.sidebar.expander("🔍 Agent & LLM Call Tracking", expanded=False):
        st.markdown("""
        **Tracking Features:**
        - 📞 **LLM Call Counting**: Track total LLM calls and per-agent usage
        - 🤖 **Agent Monitoring**: View all agents called for each request
        - 🔄 **Execution Flow**: See detailed event sequences and transfers  
        - 📊 **Performance Stats**: Monitor function calls and content lengths
        - 🌿 **Branch Tracking**: Track agent transfers and parallel execution
        
        **New Enhanced Tracking:**
        ```python
        # Get comprehensive tracking info
        result = await session_manager.run_agent_with_tracking(
            user_id, session_id, message
        )
        
        # Access LLM call statistics
        total_calls = result["total_llm_calls"]
        per_agent_stats = result["llm_call_stats"]
        individual_calls = result["llm_calls"]
        
        # Format for display
        formatted = session_manager.format_llm_call_stats(result)
        ```
        """)
        
        if st.session_state.messages:
            # Extract tracking info from recent messages
            total_llm_calls_recent = 0
            agent_llm_usage = {}
            
            for msg in st.session_state.messages[-5:]:  # Last 5 messages
                if msg["role"] == "assistant" and "🤖 Agents & LLM Calls:" in msg["content"]:
                    content = msg["content"]
                    
                    # Extract total LLM calls
                    if "Total LLM Calls:" in content:
                        lines = content.split("\n")
                        for line in lines:
                            if "Total LLM Calls:" in line:
                                try:
                                    calls = int(line.split("Total LLM Calls:")[-1].strip())
                                    total_llm_calls_recent += calls
                                except:
                                    pass
                    
                    # Extract per-agent LLM usage
                    if "📞 LLM Calls by Agent:" in content:
                        lines = content.split("\n")
                        in_agent_section = False
                        for line in lines:
                            if "📞 LLM Calls by Agent:" in line:
                                in_agent_section = True
                                continue
                            elif in_agent_section and line.strip().startswith("• ") and ":" in line:
                                try:
                                    agent_part = line.strip()[2:].split(":")[0].strip()
                                    calls_part = line.split(":")[1].split("calls")[0].strip()
                                    calls = int(calls_part)
                                    agent_llm_usage[agent_part] = agent_llm_usage.get(agent_part, 0) + calls
                                except:
                                    pass
                            elif in_agent_section and not line.strip().startswith("• "):
                                break
            
            if total_llm_calls_recent > 0:
                st.markdown("**Recent Session Stats:**")
                st.text(f"🔢 Total LLM Calls: {total_llm_calls_recent}")
                
                if agent_llm_usage:
                    st.markdown("**LLM Calls by Agent:**")
                    sorted_usage = sorted(agent_llm_usage.items(), key=lambda x: x[1], reverse=True)
                    for agent, calls in sorted_usage:
                        st.text(f"• {agent}: {calls} calls")

def display_chat_interface():
    """Display the main chat interface."""
    st.markdown("# 🤖 Multi-Agent Content Creator")
    st.markdown("### Powered by Google ADK")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle quick message injection
    if hasattr(st.session_state, 'quick_message'):
        prompt = st.session_state.quick_message
        del st.session_state.quick_message
        
        # Process the quick message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                result = session_manager.run_agent_with_tracking(
                    st.session_state.user_id,
                    st.session_state.session_id,
                    prompt
                )
                
                # Extract response and agent information
                response = result["response"]
                agents_called = result["agents_called"]
                total_agents = result["total_agents"]
                execution_flow = result["execution_flow"]
                llm_calls = result.get("llm_calls", [])
                total_llm_calls = result.get("total_llm_calls", 0)
                llm_call_stats = result.get("llm_call_stats", {})
                
                # Create agent tracking info string
                agent_info = f"\n\n---\n**🤖 Agents & LLM Calls:**\n"
                agent_info += f"• **Total LLM Calls:** {total_llm_calls}\n"
                agent_info += f"• **Agents Used:** {total_agents}\n\n"
                
                # Show LLM calls per agent
                if llm_call_stats:
                    agent_info += "**📞 LLM Calls by Agent:**\n"
                    sorted_agents = sorted(llm_call_stats.items(), key=lambda x: x[1]["total_calls"], reverse=True)
                    for agent_name, stats in sorted_agents:
                        agent_info += f"• {agent_name}: {stats['total_calls']} calls"
                        if stats['function_calls'] > 0:
                            agent_info += f" ({stats['function_calls']} with functions)"
                        agent_info += "\n"
                
                # Add execution flow summary
                if execution_flow:
                    agent_info += f"\n**📊 Execution Flow:** {len(execution_flow)} events\n"
                    for i, event in enumerate(execution_flow[:5]):  # Show first 5 events
                        if event.get("type") == "transfer":
                            agent_info += f"{i+1}. Transfer: {event['details']['from_agent']} → {event['details']['to_agent']}\n"
                        else:
                            agent_info += f"{i+1}. {event['agent_name']} (ID: {event['event_id'][:8]}...)\n"
                    if len(execution_flow) > 5:
                        agent_info += f"... and {len(execution_flow) - 5} more events\n"
                
                # Add agent response to chat with tracking info
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response + agent_info
                })
                
                if response:
                    st.markdown(response + agent_info)
                    st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Type your message here...", key="chat_input"):
        if not st.session_state.session_initialized:
            st.warning("Creating new session...")
            success = asyncio.run(create_new_session())
            if not success:
                return
        
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })  
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = asyncio.run(send_message(prompt))
                if response:
                    st.markdown(response)
                    st.rerun()

async def display_session_data():
    """Display session data in the sidebar."""

    data = await session_manager.get_session_data(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id
    )
    import json
    st.sidebar.markdown("**Session Data:**")
    st.sidebar.code(json.dumps(data, indent=2), language="json")

def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Create initial session if needed
        if not st.session_state.session_initialized:
            with st.spinner("Initializing session..."):
                asyncio.run(create_new_session())
        
        # Update workflow status
        asyncio.run(get_workflow_status())
        
        # Display sidebar components
        display_session_info()
        display_workflow_progress()
        display_agent_info() 
        display_quick_actions()
        display_agent_tracking()
        asyncio.run(display_session_data())    
        # Display main chat interface
        display_chat_interface()
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown("*Powered by Google ADK & Streamlit*")
        
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please refresh the page to restart the application.")

if __name__ == "__main__":
    main() 