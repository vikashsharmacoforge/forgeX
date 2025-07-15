# forgex Project

---

## Overview

**forgex** is a modular, agent-based conversational AI system designed to gather project requirements, generate user stories, and iteratively refine them with human feedback. It leverages FastAPI for HTTP endpoints, LangChain for LLM orchestration, and a custom memory system for persistent conversation storage. The architecture is built around multiple agents, each responsible for a specific stage in the requirements-to-user-stories pipeline, and uses MCP (Multi-agent Communication Protocol) for inter-agent communication.

---

## Architecture

### Main Components

- **Agents** (`src/agents/`)
  - `getpr.py`: Gathers project requirements from the user.
  - `cus_agent.py`: Converts finalized requirements into user stories.
  - `hitl.py`: Human-in-the-loop agent for refining user stories based on feedback.
- **Memory** (`src/memory/stm.py`): Implements persistent storage for conversations using async file I/O.
- **LLM Wrapper** (`src/llm/customllm.py`): Custom wrapper for language models via REST API.
- **Communication Server** (`src/communication/server.py`): FastAPI server that routes requests to the appropriate agent.
- **MCP Clients** (`src/mcp-clients/`): Clients for connecting to MCP servers using HTTP or SSE.
- **Utils** (`src/utils/`): Helper modules for agent orchestration and STM context management.
- **Frontend** (`final chat/app.py`): Shiny-based chat UI for user interaction.

---

## Workflow

1. **User Initiates Conversation**  
   The user interacts with the system via the Shiny chat UI (`final chat/app.py`). Each message is stored in the STM (Short-Term Memory) server for persistence.

2. **Project Requirements Gathering**  
   The `getpr.py` agent prompts the user for project requirements, classifies when requirements are finalized, and transitions the state to user story creation.

3. **User Story Generation**  
   The `cus_agent.py` agent takes finalized requirements and generates user stories using an LLM.

4. **Human-in-the-Loop Refinement**  
   The `hitl.py` agent allows the user to provide feedback or request changes to the generated user stories. It uses a classifier to determine if the stories are finalized or need further updates.

5. **Memory and State Management**  
   All conversation states and messages are stored and retrieved using the STM server (`src/memory/stm.py`), ensuring continuity and traceability.

6. **Communication**  
   The FastAPI server (`src/communication/server.py`) exposes endpoints for each agent, routing incoming requests to the correct tool based on the conversation state.

---

## Key Modules

### Agents

- **getpr.py**
  - Collects project requirements.
  - Uses a classifier LLM to detect when requirements are finalized.
  - Stores conversation state and transitions to user story creation.

- **cus_agent.py**
  - Generates user stories from finalized requirements.
  - Stores the generated stories and transitions to HITL (Human-in-the-Loop) state.

- **hitl.py**
  - Accepts user feedback on user stories.
  - Classifies feedback as requiring further changes or finalization.
  - Beautifies and finalizes user stories when approved.

### Memory

- **stm.py**
  - Provides async tools for storing and retrieving conversation data.
  - Stores each conversation as a JSON file keyed by conversation ID.
  - Exposes MCP tools for use by agents.

### LLM Wrapper

- **customllm.py**
  - Wraps a REST API for LLM inference.
  - Supports system prompts, history, and configurable parameters.

### Communication

- **server.py**
  - FastAPI server with endpoints for each agent state (`/data/START`, `/data/CUS`, `/data/HITL`).
  - Forwards requests to the appropriate agent tool via MCP.

### MCP Clients

- **stmhttp_client.py**
  - Async client for connecting to MCP servers over HTTP.
  - Used by agents and utils for memory operations.

### Utils

- **agents_wrapper.py**
  - Provides a unified interface for connecting to MCP agents and invoking tools.
- **stm_context_manager.py**
  - Async helpers for storing and retrieving messages from STM.

### Frontend

- **app.py** (Shiny)
  - Provides a chat interface for user interaction.
  - Handles message submission, state management, and displays assistant responses.

---

## How to Run

1. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Start the STM Server**
   ```
   python src/memory/stm.py
   ```

3. **Start Agent Servers**
   ```
   python src/agents/getpr.py
   python src/agents/cus_agent.py
   python src/agents/hitl.py
   ```

4. **Start the Communication Server**
   ```
   python src/communication/server.py
   ```

5. **Run the Frontend**
   ```
   python final chat/app.py
   ```

---

## Configuration

- **Environment Variables**: Set in `.env` for LLM API keys, endpoints, and model names.
- **Persistent Storage**: Conversations are stored as JSON files in the `storage/` directory.

---

## Extensibility

- **Add New Agents**: Implement a new agent in `src/agents/` and register it with the communication server.
- **Change LLM Provider**: Update `customllm.py` to point to a different REST API.
- **Customize Prompts**: Edit the prompt strings in each agent for different behaviors.

---

## File Structure

```
forgeX-1/
│
├── final chat/
│   └── app.py
├── src/
│   ├── agents/
│   │   ├── getpr.py
│   │   ├── cus_agent.py
│   │   └── hitl.py
│   ├── communication/
│   │   └── server.py
│   ├── llm/
│   │   └── customllm.py
│   ├── memory/
│   │   └── stm.py
│   ├── mcp-clients/
│   │   ├── stmhttp_client.py
│   │   └── sse_client.py
│   └── utils/
│       ├── agents_wrapper.py
│       └── stm_context_manager.py
├── requirements.txt
├── README.md
└── config.ini
```

---

## Technologies Used

- **Python 3.11+**
- **FastAPI** (API server)
- **LangChain** (LLM orchestration)
- **Shiny** (Frontend chat UI)
- **aiofiles** (Async file I/O)
- **dotenv** (Environment variable management)
- **MCP** (Multi-agent Communication Protocol)

---

## Summary

forgex is a flexible, modular system that streamlines the process of gathering project requirements and generating user stories through conversational AI. Its agent-based architecture and use of modern technologies like FastAPI, LangChain, and MCP make it a powerful tool for enhancing productivity and collaboration in software development projects.