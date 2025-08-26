# 🤖 Multi-Agent Content Creation POC

A proof of concept demonstrating the power of **Google ADK (Agent Development Kit)** for building sophisticated multi-agent systems. This project creates a collaborative content creation pipeline using specialized AI agents that work together seamlessly.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Google ADK](https://img.shields.io/badge/Google%20ADK-1.12.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)

## 🏗️ Architecture

This system implements a **multi-agent orchestration pattern** where a main orchestrator coordinates specialized agents:

```
┌─────────────────────┐
│  Orchestrator       │ ──── Routes user requests to appropriate agents
│  Agent              │      Based on intent analysis and workflow state
└─────────────────────┘
           │
           ├─── 💡 Ideate Agent        (Generates creative ideas)
           ├─── 📋 Outline Agent       (Creates structured outlines)
           ├─── 📝 Draft Agent         (Writes complete content)
           ├─── 👨‍💼 Persona Feedback   (Provides expert feedback & chat)
           └─── 🔍 SEO Agent          (Optimizes for search engines)
```

### Key Components

- **🧠 Orchestrator Agent**: Master coordinator using Google ADK's `LlmAgent`
- **🔧 Specialized Agents**: Each with specific roles and expertise
- **💾 Session Storage**: `InMemorySessionService` for conversation state
- **🌐 Streamlit Interface**: Interactive chat UI with workflow tracking
- **🔄 Agent Tools**: `AgentTool` for inter-agent communication

## 🚀 Features

- **🤝 Multi-Agent Coordination**: Agents work together seamlessly
- **📊 Workflow Tracking**: Visual progress through content creation stages
- **💬 Interactive Chat**: Natural language interface for all interactions
- **🧠 Intelligent Routing**: Auto-detects which agent to use based on context
- **📈 State Management**: Persistent conversation memory across interactions

## 📋 Prerequisites

- **Python 3.8+**
- **Google API Key** (for Gemini models)
- **Git** (for cloning the repository)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd google_adk_poc
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # The app will create a template for you
   python main.py --check-env
   
   # Copy the template and add your API key
   cp .env.template .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

## 🔑 Configuration

Create a `.env` file in the project root with your API keys:

```env
# Required: Google API Key for Gemini models
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Additional providers
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Application settings
DEBUG_MODE=True
STREAMLIT_PORT=8501
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### Getting a Google API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" and create a new key
4. Copy the key to your `.env` file

## 🎯 Usage

### Quick Start

**Launch the web interface** (recommended):
```bash
python main.py --web
```

This opens a Streamlit app at `http://localhost:8501` with:
- 💬 Interactive chat interface
- 📊 Real-time workflow progress
- ⚡ Quick action buttons
- 🔧 Session management tools

### Command Line Options

```bash
python main.py --web          # Launch Streamlit interface (default)
python main.py --test         # Test the agent system directly  
python main.py --check-env    # Verify environment setup
python main.py --info         # Show detailed project information
```

### Example Workflow

1. **💡 Generate Ideas**:
   ```
   "Give me ideas for a blog post about artificial intelligence"
   ```

2. **📋 Create Outline**:
   ```
   "Create an outline for the AI blog post idea"
   ```

3. **📝 Write Draft**:
   ```
   "Write a complete draft based on the outline"
   ```

4. **👨‍💼 Get Feedback**:
   ```
   "I'd like expert feedback on my draft"
   ```

5. **🔍 SEO Optimize**:
   ```
   "Optimize this content for SEO"
   ```

## 🏭 Project Structure

```
google_adk_poc/
├── 📁 agents/              # AI agent implementations
│   ├── specialized_agents.py   # Five specialized agents
│   ├── orchestrator.py        # Main coordinator agent
│   └── __init__.py
├── 📁 config/              # Configuration management
│   └── settings.py            # Pydantic settings with env vars
├── 📁 frontend/            # User interfaces
│   └── streamlit_app.py       # Main Streamlit chat interface
├── 📁 utils/               # Utility functions
│   ├── session_manager.py     # ADK session management
│   └── __init__.py
├── 📁 models/              # (Empty - for future model definitions)
├── 📄 main.py              # Main application entry point
├── 📄 requirements.txt     # Python dependencies
└── 📄 README.md           # This file
```

## 🤖 Agent Details

### 🧠 Orchestrator Agent
- **Role**: Master coordinator and request router
- **Capabilities**: Intent analysis, workflow management, agent selection
- **Tools**: All specialized agents as `AgentTool` instances

### 💡 Ideate Agent
- **Role**: Creative idea generation
- **Input**: Topics, themes, general concepts
- **Output**: 3-5 structured, actionable ideas with explanations

### 📋 Outline Agent
- **Role**: Content structuring and organization  
- **Input**: Ideas (user-provided or from Ideate Agent)
- **Output**: Hierarchical outline with main points and sub-points

### 📝 Draft Agent
- **Role**: Complete content creation
- **Input**: Structured outline from session state
- **Output**: Full, engaging content draft ready for review

### 👨‍💼 Persona Feedback Agent
- **Role**: Expert review and conversational interaction
- **Modes**: 
  - Content Review: Detailed feedback on drafts
  - Chat Interaction: Subject matter expert dialogue

### 🔍 SEO Agent
- **Role**: Search engine optimization specialist
- **Input**: Content draft from session state
- **Output**: SEO analysis, recommendations, and optimized version

## 💾 Session Management

The system uses **Google ADK's InMemorySessionService** for:

- **🔄 State Persistence**: Conversation history and workflow data
- **📊 Progress Tracking**: Current step and completed stages
- **🔗 Agent Communication**: Shared context between specialized agents
- **🧠 Memory**: Maintains context across multi-turn conversations

### Session State Keys
- `generated_ideas`: Output from Ideate Agent
- `content_outline`: Output from Outline Agent  
- `content_draft`: Output from Draft Agent
- `expert_feedback`: Output from Persona Feedback Agent
- `seo_optimized_content`: Output from SEO Agent

## 🧪 Testing

**Test the agent system directly**:
```bash
python main.py --test
```

This runs a simple test that:
1. Creates a test session
2. Sends a sample message
3. Displays the agent response
4. Shows workflow status

## 🔧 Development

### Adding New Agents

1. **Create the agent** in `agents/specialized_agents.py`:
   ```python
   new_agent = LlmAgent(
       name="NewAgent",
       model="gemini-2.0-flash",
       instruction="Your specialized instructions...",
       description="What this agent does",
       output_key="new_agent_output"
   )
   ```

2. **Wrap as a tool** in `agents/orchestrator.py`:
   ```python
   new_tool = AgentTool(agent=new_agent)
   ```

3. **Add to orchestrator tools** and update instructions

4. **Update session manager** workflow tracking if needed

### Customizing the UI

The Streamlit interface is in `frontend/streamlit_app.py`. Key areas:
- `display_workflow_progress()`: Workflow visualization
- `display_chat_interface()`: Main chat functionality

## 📚 Resources

- **[Google ADK Documentation](https://github.com/google/adk-python)**: Official ADK guide
- **[Gemini API](https://ai.google.dev/gemini-api)**: Google's generative AI models
- **[Streamlit Docs](https://streamlit.io/)**: Building interactive web apps
- **[Google AI Studio](https://aistudio.google.com/)**: Get your API key here

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Enhancements

- **🏗️ Custom Agent Types**: Extend beyond LlmAgent
- **🌐 API Interface**: REST API for programmatic access
- **📊 Advanced Analytics**: Detailed workflow metrics
- **🔗 External Integrations**: Connect to CMSs, social media
- **💾 Persistent Storage**: Database-backed session storage
- **🎨 Advanced UI**: Rich text editing, file uploads
- **🔄 Workflow Templates**: Predefined content creation flows

---

**Built with ❤️ using Google ADK and Streamlit**

*This is a proof of concept demonstrating multi-agent orchestration patterns. Customize and extend as needed for your specific use cases!* 