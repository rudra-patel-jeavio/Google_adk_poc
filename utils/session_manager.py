"""
Session management utilities for the multi-agent content creation system.
Handles session creation, state management, and runner setup using Google ADK's InMemorySessionService.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
from agents.orchestrator import orchestrator_agent


class SessionManager:
    """Manages sessions and provides utilities for the multi-agent system."""
    
    def __init__(self, app_name: str = "content_creation_poc"):
        self.app_name = app_name
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.runner = None
        self._setup_runner()
    
    def _setup_runner(self):
        """Set up the runner with orchestrator agent."""
        self.runner = Runner(
            agent=orchestrator_agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service
        )
    
    async def create_session(
        self, 
        user_id: str, 
        session_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session for a user.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Optional session ID, will generate one if not provided
            initial_state: Optional initial state for the session
        
        Returns:
            str: The session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state or {}
        )
        
        return session_id
    
    async def get_session_state(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get the current state of a session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        
        Returns:
            Dict[str, Any]: Current session state
        """
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            return session.state if session else {}
        except Exception as e:
            print(f"Error getting session state: {e}")
            return {}
    
    async def update_session_state(
        self, 
        user_id: str, 
        session_id: str, 
        state_update: Dict[str, Any]
    ):
        """
        Update session state with new data.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            state_update: Dictionary of state updates
        """
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            if session:
                session.state.update(state_update)
        except Exception as e:
            print(f"Error updating session state: {e}")
    
    async def get_session_data(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get the session data.
        """
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        return session.state if session else {}

    def run_agent_simple(
        self, 
        user_id: str, 
        session_id: str, 
        user_message: str
    ) -> str:
        """
        Simple agent execution without tracking details.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            user_message: The user's input message
        
        Returns:
            str: The agent's response
        """
        try:
            # Create content from user message
            content = Content(
                role="user", 
                parts=[Part(text=user_message)]
            )
            
            # Direct execution - returns final result
            result = self.runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            )
            
            # Extract final response text
            if result and result.content and result.content.parts:
                return result.content.parts[0].text.strip()
            
            return "No response received from the agent."
            
        except Exception as e:
            print(f"Error running agent: {e}")
            return f"An error occurred: {str(e)}. Please try again."

    async def run_agent_with_tracking(
        self, 
        user_id: str, 
        session_id: str, 
        user_message: str
    ) -> Dict[str, Any]:
        """
        Run the orchestrator agent with a user message and track all agent calls.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            user_message: The user's input message
        
        Returns:
            Dict[str, Any]: Contains 'response', 'agents_called', 'execution_flow', 'llm_calls', and statistics
        """
        try:
            # Create content from user message
            content = Content(
                role="user", 
                parts=[Part(text=user_message)]
            )
            
            # Track agent calls and execution flow
            agents_called = []
            execution_flow = []
            llm_calls = []  # Track individual LLM calls
            llm_call_stats = {}  # Statistics per agent
            final_response = ""
            total_llm_calls = 0

            # Helper to extract human-readable text from an event's parts
            def _extract_text_from_event_parts(parts) -> str:
                try:
                    # Prefer plain text if present
                    for p in parts or []:
                        if getattr(p, 'text', None):
                            return p.text or ""
                    # Fall back to function_response
                    for p in parts or []:
                        fr = getattr(p, 'function_response', None)
                        if fr and getattr(fr, 'response', None) is not None:
                            resp = fr.response
                            # If the tool returned a primitive, ADK wrapped it under 'result'
                            if isinstance(resp, dict):
                                if 'output' in resp:
                                    out = resp['output']
                                elif 'result' in resp:
                                    out = resp['result']
                                else:
                                    out = resp
                            else:
                                out = resp
                            if isinstance(out, (dict, list)):
                                import json as _json
                                return _json.dumps(out, ensure_ascii=False)
                            return str(out)
                except Exception:
                    pass
                return ""
            
            # Run the agent asynchronously
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                # Track agent information from each event
                agent_info = {
                    "agent_name": event.author,
                    "invocation_id": event.invocation_id,
                    "branch": event.branch,
                    "timestamp": event.timestamp,
                    "event_id": event.id
                }
                
                # Add to agents called list if not already present
                if event.author not in [agent["agent_name"] for agent in agents_called]:
                    agents_called.append({
                        "agent_name": event.author,
                        "first_seen": event.timestamp,
                        "branch": event.branch
                    })
                
                # Track execution flow
                execution_flow.append(agent_info)
                
                # Track LLM calls - events with content typically represent LLM interactions
                if event.content and event.content.parts and not event.author == "user":
                    total_llm_calls += 1

                    extracted_text = _extract_text_from_event_parts(event.content.parts)
                    content_length = len(extracted_text) if extracted_text else 0
                    
                    # Record individual LLM call
                    llm_call_info = {
                        "call_number": total_llm_calls,
                        "agent_name": event.author,
                        "timestamp": event.timestamp,
                        "event_id": event.id,
                        "invocation_id": event.invocation_id,
                        "has_function_calls": bool(event.get_function_calls()),
                        "function_calls": [fc.name for fc in event.get_function_calls()] if event.get_function_calls() else [],
                        "content_length": content_length,
                        "is_final": event.is_final_response()
                    }
                    llm_calls.append(llm_call_info)
                    
                    # Update per-agent statistics
                    if event.author not in llm_call_stats:
                        llm_call_stats[event.author] = {
                            "total_calls": 0,
                            "function_calls": 0,
                            "total_content_length": 0,
                            "first_call": event.timestamp,
                            "last_call": event.timestamp
                        }
                    
                    llm_call_stats[event.author]["total_calls"] += 1
                    llm_call_stats[event.author]["total_content_length"] += content_length
                    llm_call_stats[event.author]["last_call"] = event.timestamp
                    
                    if llm_call_info["has_function_calls"]:
                        llm_call_stats[event.author]["function_calls"] += 1
                
                # Check for agent transfers
                if event.actions and event.actions.transfer_to_agent:
                    transfer_info = {
                        "from_agent": event.author,
                        "to_agent": event.actions.transfer_to_agent,
                        "timestamp": event.timestamp
                    }
                    execution_flow.append({
                        "type": "transfer",
                        "details": transfer_info
                    })
                
                print(f"Event from {event.author}: {event}")
                
                # Capture final response
                if event.is_final_response() and event.content:
                    if event.content.parts:
                        extracted_text = _extract_text_from_event_parts(event.content.parts)
                        if extracted_text:
                            final_response = extracted_text.strip()
                            break
            
            return {
                "response": final_response or "I'm processing your request, but didn't receive a complete response. Please try again.",
                "agents_called": agents_called,
                "execution_flow": execution_flow,
                "total_agents": len(agents_called),
                "llm_calls": llm_calls,
                "total_llm_calls": total_llm_calls,
                "llm_call_stats": llm_call_stats,
                "summary": {
                    "total_agents_used": len(agents_called),
                    "total_llm_calls": total_llm_calls,
                    "agents_with_llm_calls": list(llm_call_stats.keys()),
                    "most_active_agent": max(llm_call_stats.items(), key=lambda x: x[1]["total_calls"])[0] if llm_call_stats else None
                }
            }
            
        except Exception as e:
            print(f"Error running agent: {e}")
            return {
                "response": f"An error occurred: {str(e)}. Please try again.",
                "agents_called": [],
                "execution_flow": [],
                "total_agents": 0,
                "llm_calls": [],
                "total_llm_calls": 0,
                "llm_call_stats": {},
                "summary": {
                    "total_agents_used": 0,
                    "total_llm_calls": 0,
                    "agents_with_llm_calls": [],
                    "most_active_agent": None
                }
            }

    async def run_agent(
        self, 
        user_id: str, 
        session_id: str, 
        user_message: str
    ) -> str:
        """
        Run the orchestrator agent with a user message (backward compatibility).
        Now uses the simple execution method.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            user_message: The user's input message
        
        Returns:
            str: The agent's response
        """
        return await self.run_agent_simple(user_id, session_id, user_message)
    
    def format_llm_call_stats(self, tracking_result: Dict[str, Any]) -> str:
        """
        Format LLM call statistics into a readable string.
        
        Args:
            tracking_result: Result from run_agent_with_tracking
        
        Returns:
            str: Formatted statistics string
        """
        if not tracking_result or "llm_call_stats" not in tracking_result:
            return "No LLM call statistics available."
        
        stats = tracking_result["llm_call_stats"]
        summary = tracking_result.get("summary", {})
        
        output = []
        output.append("=" * 60)
        output.append("🤖 LLM CALL STATISTICS")
        output.append("=" * 60)
        output.append(f"📊 Total LLM Calls: {tracking_result.get('total_llm_calls', 0)}")
        output.append(f"🎯 Total Agents Used: {summary.get('total_agents_used', 0)}")
        output.append(f"⭐ Most Active Agent: {summary.get('most_active_agent', 'None')}")
        output.append("")
        
        if stats:
            output.append("📋 Per-Agent Statistics:")
            output.append("-" * 40)
            
            # Sort agents by total calls (descending)
            sorted_agents = sorted(stats.items(), key=lambda x: x[1]["total_calls"], reverse=True)
            
            for agent_name, agent_stats in sorted_agents:
                output.append(f"\n🔹 Agent: {agent_name}")
                output.append(f"   • Total Calls: {agent_stats['total_calls']}")
                output.append(f"   • Function Calls: {agent_stats['function_calls']}")
                output.append(f"   • Total Content Length: {agent_stats['total_content_length']} chars")
                output.append(f"   • First Call: {agent_stats['first_call']}")
                output.append(f"   • Last Call: {agent_stats['last_call']}")
        
        # Show individual LLM calls if requested
        llm_calls = tracking_result.get("llm_calls", [])
        if llm_calls:
            output.append("\n" + "=" * 60)
            output.append("📞 Individual LLM Calls:")
            output.append("=" * 60)
            
            for call in llm_calls:
                output.append(f"\n#{call['call_number']} - {call['agent_name']}")
                output.append(f"   • Event ID: {call['event_id']}")
                output.append(f"   • Content Length: {call['content_length']} chars")
                output.append(f"   • Has Function Calls: {call['has_function_calls']}")
                if call['function_calls']:
                    output.append(f"   • Functions: {', '.join(call['function_calls'])}")
                output.append(f"   • Is Final Response: {call['is_final']}")
                output.append(f"   • Timestamp: {call['timestamp']}")
        
        output.append("\n" + "=" * 60)
        return "\n".join(output)
    
    async def test_llm_tracking(self, message: str = "Generate 3 creative blog post ideas") -> Dict[str, Any]:
        """
        Test the LLM tracking functionality with a simple message.
        
        Args:
            message: Test message to send (defaults to a simple request)
        
        Returns:
            Dict[str, Any]: Full tracking result
        """
        test_user = "test_user_tracking"
        test_session = await self.create_session(test_user)
        
        try:
            result = await self.run_agent_with_tracking(
                user_id=test_user,
                session_id=test_session,
                user_message=message
            )
            
            print("🧪 LLM Tracking Test Results:")
            print(self.format_llm_call_stats(result))
            
            return result
            
        finally:
            # Clean up test session
            await self.clear_session(test_user, test_session)

    
    async def get_workflow_status(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get the current workflow status based on session state.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        
        Returns:
            Dict[str, Any]: Workflow status information
        """
        state = await self.get_session_state(user_id, session_id)
        
        workflow_status = {
            "ideas_generated": "generated_ideas" in state,
            "outline_created": "content_outline" in state,
            "draft_written": "content_draft" in state,
            "feedback_received": "expert_feedback" in state,
            "seo_optimized": "seo_optimized_content" in state,
            "current_step": self._determine_current_step(state),
            "available_data": list(state.keys())
        }
        
        return workflow_status
    
    def _determine_current_step(self, state: Dict[str, Any]) -> str:
        """Determine the current step in the workflow based on state."""
        if "seo_optimized_content" in state:
            return "completed"
        elif "expert_feedback" in state:
            return "feedback_received"
        elif "content_draft" in state:
            return "draft_completed"
        elif "content_outline" in state:
            return "outline_ready"
        elif "generated_ideas" in state:
            return "ideas_generated"
        else:
            return "starting"
    
    async def clear_session(self, user_id: str, session_id: str):
        """
        Clear/reset a session by deleting it.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        try:
            await self.session_service.delete_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
        except Exception as e:
            print(f"Error clearing session: {e}")


# Global session manager instance
session_manager = SessionManager()

__all__ = ["SessionManager", "session_manager"] 