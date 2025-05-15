# 🚀 Agentic RAG with MCP Server [![Agentic-RAG-MCPServer - AgenticRag](https://img.shields.io/badge/Agentic--RAG--MCPServer-AgenticRag-blueviolet)](https://github.com/ashishpatel26/Agentic-RAG-with-MCP-Server)

---

## ✨ Overview

![](Image/AgenticRAGMCPServer.gif)

**Agentic RAG with MCP Server** is a powerful project that brings together an MCP (Model Context Protocol) server and client for building **Agentic RAG** (Retrieval-Augmented Generation) applications.

This setup empowers your RAG system with advanced tools such as:

* 🕵️‍♂️ **Entity Extraction**
* 🔍 **Query Refinement**
* ✅ **Relevance Checking**

The server hosts these intelligent tools, while the client shows how to seamlessly connect and utilize them.

---

## 🖥️ Server — `server.py`

Powered by the `FastMCP` class from the `mcp` library, the server exposes these handy tools:

| Tool Name               | Description                                                                               | Icon |
| ----------------------- | ----------------------------------------------------------------------------------------- | ---- |
| `get_time_with_prefix`  | Returns the **current date & time**                                                       | ⏰    |
| `extract_entities_tool` | Uses **OpenAI** to extract entities from a query — enhancing document retrieval relevance | 🧠   |
| `refine_query_tool`     | Improves the quality of user queries with **OpenAI-powered refinement**                   | ✨    |
| `check_relevance`       | Filters out irrelevant content by checking chunk relevance with an LLM                    | ✅    |

---

## 🤝 Client — `mcp-client.py`

The client demonstrates how to connect and interact with the MCP server:

* Establish a connection with `ClientSession` from the `mcp` library
* List all available server tools
* Call any tool with custom arguments
* Process queries leveraging **OpenAI or Gemini** and MCP tools in tandem

---

## ⚙️ Requirements

* Python 3.9 or higher
* `openai` Python package
* `mcp` library
* `python-dotenv` for environment variable management

---

## 🛠️ Installation Guide

```bash
# Step 1: Clone the repository
git clone https://github.com/ashishpatel26/Agentic-RAG-with-MCP-Server.git

# Step 2: Navigate into the project directory
cd Agentic-RAG-with-MCP-Serve

# Step 3: Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Configuration

1. Create a `.env` file (use `.env.sample` as a template)
2. Set your OpenAI model in `.env`:

```env
OPENAI_MODEL_NAME="your-model-name-here"
GEMINI_API_KEY="your-model-name-here"
```

---

## 🚀 How to Use

1. **Start the MCP server:**

```bash
python server.py
```

2. **Run the MCP client:**

```bash
python mcp-client.py
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

***Thanks for Reading 🙏***



