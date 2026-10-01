# 🤖 AI Leave Approval Workflow Agent

An agentic workflow automation system for intelligent leave approval using **LangGraph**. The workflow combines AI reasoning, tool calling, structured outputs, and human-in-the-loop decision making to simulate a real-world enterprise leave approval process.

---

## 🚀 Features

- 🧠 AI-powered leave request assessment
- 🛠 Tool calling for employee information and leave balance
- 📋 Structured outputs using Pydantic
- 👤 Human-in-the-loop approval for complex requests
- 🔄 Multi-step workflow with conditional routing
- 💾 Stateful execution using LangGraph checkpointing
- 📈 Workflow visualization support

---

## 🏗 Workflow

```
Employee Request
        │
        ▼
 AI Assessment
        │
        ▼
 Fetch Employee Data
        │
        ▼
Decision Making
   │      │
   │      ├────────────► Human Review
   │                     │
   │                     ▼
   │             Employee Clarification
   │                     │
   └─────────────────────┘
        │
        ▼
 Final Approval
```

---

## ⚙️ Tech Stack

- Python
- LangGraph
- LangChain Core
- python-dotenv

---

## 📂 Project Structure

```
AI-Leave-Approval-Workflow-Agent/
│
├── main.py                 # Main workflow implementation
├── utils.py                # LLM setup & graph visualization
├── requirements.txt
├── .env
├── leave_workflow.png      # Generated workflow graph
└── README.md
```

---

## 🧩 Workflow Components

### Employee Tools
- Fetch employee details
- Check leave balance

### AI Assessment
- Evaluates urgency
- Assesses employee risk
- Recommends approval, escalation, or clarification

### Human Review
- Escalates complex requests
- Allows manager approval or rejection

### Employee Clarification
- Collects additional information when required
- Re-evaluates the request automatically

### Final Decision
- Approves automatically when eligible
- Approves after manager intervention when required

---

## ▶️ Getting Started

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Leave-Approval-Workflow-Agent.git
cd AI-Leave-Approval-Workflow-Agent
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
```

(or your preferred LLM provider)

### Run

```bash
python main.py
```

---

## 📌 Example Flow

1. Employee submits leave request.
2. AI fetches employee details and leave balance.
3. AI evaluates urgency and risk.
4. Request is:
   - Automatically approved,
   - Sent for manager review, or
   - Returned for employee clarification.
5. Final approval is generated.

---

## 🎯 Key Concepts Demonstrated

- Agentic AI workflows
- State-based workflow orchestration
- Conditional routing
- Tool integration
- Human-in-the-loop systems
- Structured LLM outputs
- Enterprise workflow automation

---

## 🔮 Future Improvements

- Web UI with Streamlit or Gradio
- Database integration
- HRMS API integration
- Email notifications
- Leave calendar management
- Audit logging
- Multi-level approval workflows

---

## 👨‍💻 Author
 
**Gollaally Veda Spoorthi**

---

⭐ If you found this project interesting, consider giving it a star!
