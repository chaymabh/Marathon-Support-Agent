# 🏃‍♀️ Marathon-Support-Agent

## 📄 Overview

**Marathon-Support-Agent** is a smart, modular support assistant tailored for endurance event management platforms such as marathons, ultraruns, and trail races. It provides a complete pipeline from chat-based user input to automated ticket creation when necessary, combining conversational AI with structured data retrieval and fallback mechanisms.

This project uses **LangGraph**, **LangChain**, **FastAPI**, and integrates with a **PostgreSQL** backend. When needed, it escalates unresolved issues through a summarization and ticket generation process using an external helpdesk API.

## 🖼️ System Diagram

The system is structured around a conversational pipeline that routes requests through multiple intelligent components:

![System Architecture](img/pipeline.png)

## 🌟 Key Features

- **Interactive Chat UI**: Web-based interface for direct user interaction with the system.
- **FastAPI Backend**: Manages request routing and connects the chat interface to backend agents.
- **LLM-Supervisor Agent**: Analyzes each request to determine if it can be resolved using existing knowledge or if escalation is needed.
- **Knowledge Base (RAG)**: Factual responses are retrieved from a structured PostgreSQL database through retrieval-augmented generation.
- **Summarization Agent**: For questions that cannot be directly answered, the system generates a structured summary for support ticket creation.
- **Ticket Creation (eDesk API)**: Automatically creates support tickets using the summarized content.
- **Database Logging**: _(In progress)_ — future support for logging conversations and tickets for audit and analysis.

## 🧠 How It Works

1. The user sends a message through the chat interface.
2. The FastAPI gateway receives the message and forwards it to the LLM-Supervisor Agent.
3. The agent checks whether the Knowledge Base contains a relevant answer:
   - If **yes**, a direct response is generated and returned to the user.
   - If **no**, the query is passed to the Summarization Agent, which structures it for ticketing.
4. The structured summary is sent to the helpdesk API to open a support ticket.
5. _(Coming soon)_: All interactions will be logged into PostgreSQL for traceability and analysis.

## 🧬 Component Overview

| Component                | Description                                                        |
| ------------------------ | ------------------------------------------------------------------ |
| 💬 Chat UI               | Frontend interface for end users                                   |
| 🚦 FastAPI Gateway       | Handles HTTP routing, API key authentication, and middleware       |
| 🧠 LLM-Supervisor Agent  | Decision logic for routing between agents or escalation paths      |
| 📘 Knowledge Base (RAG)  | Structured PostgreSQL-backed retrieval augmented generation        |
| ✍️ Summarization Agent   | Converts unclear queries into structured ticket-friendly summaries |
| 📝 Ticketing API (eDesk) | Sends tickets to external helpdesk system using JSON payloads      |
| 🛠️ PostgreSQL Logging    | _(In progress)_ Planned feature for request-response storage       |

## 💻 Chat Interface

A minimal web-based chat page is included to test and visualize the system in real-time. It connects directly to the FastAPI backend and reflects agent responses or ticket creation updates.
