# Marathon-Support-Agent

### **📄 Description:**

> A modular, agent-based Retrieval-Augmented Generation (RAG) system for customer support in **endurance event management** (e.g., marathons, ultramarathons, long-distance walking events). Built using **LangGraph**, **LangChain**, and **FastAPI**, this assistant interfaces with a **PostgreSQL** event database and leverages **LLM-driven multi-agent orchestration** to respond to both **structured transactional queries** (tickets, registrations, event info) and **general knowledge questions** (about race types, distances, training, etc.).

---

## 📚 Technical Overview

The project implements a **Structured RAG architecture** with intelligent **agent routing**, backed by **relational data**, and enriched through **LLM-based reasoning**. It allows customers to:

- Inquire about upcoming events, locations, and distances
- Check ticket availability, bookings, and transaction history
- Get help with registration, account access, and refunds
- Ask general questions about marathons or race logistics

---

### 🧠 Architecture Highlights

| Component                  | Description                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| 🧭 **LangGraph**           | Manages multi-agent flows via `StateGraph`, using conditional transitions                               |
| 🤖 **LLMs**                | Operate as PlannerAgent, ReporterAgent, and optional SummarizationAgent                                 |
| 🛠️ **Planner Agent**       | Uses structured prompts + guided JSON to route input to the right agent/tool                            |
| 🔧 **SQL Tools**           | `get_events`, `get_tickets`, `get_orders`, `get_customers`, `get_faq` — each maps to a PostgreSQL table |
| 🗂️ **Structured RAG**      | Factual queries are grounded using real-time SQL retrieval before LLM generation                        |
| 💬 **Fallback Agent**      | Reporter handles unclear queries, escalation, or user clarification                                     |
| 🧾 **Summarization Agent** | (Optional) Generates structured JSON tickets from multi-turn conversations                              |
| 🗃️ **PostgreSQL Backend**  | Stores all transactional data (event metadata, tickets, users, orders)                                  |
| 🔐 **API Key Security**    | Protects data endpoints and routes via authorization middleware                                         |
| 🌐 **HTML UI**             | Lightweight interface served through FastAPI for direct user interaction                                |

---

### 🧬 RAG Flow Diagram

```mermaid
graph TD
    A[User Message] --> P[PlannerAgent]
    P -->|Tool Needed| KBT[knowledge_base_tool]
    KBT -->|Executes SQL Tool| T[Tool (e.g. get_events)]
    T --> R[ReporterAgent]
    P -->|Fallback or Unclear| R
    R --> E[EndNodeAgent]
```

---

### 🧠 RAG Modes Supported

- ✅ **Structured RAG** (SQL → LLM)
- ✅ **Tool-Augmented Generation** via LangGraph conditional routing
- ✅ **Fallback generation** for fuzzy, conversational, or unsupported queries
- 🔌 _Ready for future integration with_ **vector stores** for unstructured RAG

---

### 🗂️ Repo Name Suggestions

| Name                     | Purpose                              |
| ------------------------ | ------------------------------------ |
| `marathon-support-agent` | Most direct and descriptive          |
| `racewise-rag-bot`       | Technical and catchy                 |
| `eventflow-agent`        | Neutral and scalable                 |
| `endurassist`            | Branded-style, for endurance support |
| `ragtrack-agent`         | Combines “RAG” and “track”           |
| `ticketbot-langgraph`    | Transaction-focused                  |

---

### ✅ Summary

This project implements a **production-grade RAG system** with:

- Semantic agent-based routing (LangGraph)
- Structured grounding via PostgreSQL tools
- Prompt-defined, memory-aware agent behavior
- LLM-generated responses based on real data
- Clear separation between factual queries and fallback reasoning

It's suitable for any business managing **large-scale public events**, particularly in sports and fitness sectors.
