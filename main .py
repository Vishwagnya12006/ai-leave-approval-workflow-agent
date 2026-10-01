import uuid
from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from utils import get_llm, visualize_graph
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig

load_dotenv()

# Constants
EMPLOYEES = {
    "EMP001": {"name": "Alice Smith", "stress_score": 8, "days_since_last_leave": 180},
    "EMP002": {"name": "Bob Jones", "stress_score": 3, "days_since_last_leave": 10},
    "EMP003": {"name": "Charlie Brown", "stress_score": 9, "days_since_last_leave": 250},
}
BALANCES = {"EMP001": 15, "EMP002": 5, "EMP003": 2}

class LeaveState(TypedDict):
    employee_id: str
    leave_reason: str
    messages: Annotated[list, add_messages]
    urgency: str
    risk_explanation: str
    decision: str
    decision_explanation: str
    manager_decision: str | None
    employee_response: str | None
    final_status: str

class AssessmentResult(BaseModel):
    urgency: Literal["Emergency", "High", "Normal"]
    risk_explanation: str
    decision: Literal["Approve", "Escalate", "Need Info"]
    decision_explanation: str

class ClarificationRequest(BaseModel):
    question: str

@tool
def get_employee_details(employee_id: str) -> dict:
    """Fetches employee details: name, stress score, and days since last leave."""
    e = EMPLOYEES.get(employee_id, {"name": "Unknown", "stress_score": 5, "days_since_last_leave": 30})
    return {"employee_name": e["name"], "stress_score": e["stress_score"], "days_since_last_leave": e["days_since_last_leave"]}

@tool
def check_leave_balance(employee_id: str) -> dict:
    """Checks the remaining leave balance for the employee."""
    return {"leave_balance_days": BALANCES.get(employee_id, 10)}

# Global LLM clients reuse
llm = get_llm(temperature=0.0)
llm_with_tools = llm.bind_tools([get_employee_details, check_leave_balance])
structured_llm = llm.with_structured_output(AssessmentResult, method="function_calling")
clarification_llm = llm.with_structured_output(ClarificationRequest, method="function_calling")
tool_executor = ToolNode([get_employee_details, check_leave_balance])

def tool_node(state: LeaveState, config: RunnableConfig):
    if getattr(state["messages"][-1], "tool_calls", None):
        print("[Execution Trace] Tool Node")
        return tool_executor.invoke(state, config)
    return {}

def llm_assessment_node(state: LeaveState):
    print("[Execution Trace] LLM Assessment")
    has_details = any(msg.type == "tool" for msg in state["messages"])
    
    instruction = (
        "Analyze employee details and balance from history, then call AssessmentResult tool."
        if has_details
        else "You must call tools to fetch employee details and balance first."
    )
    prompt = (
        f"Leave Request\n"
        f"Employee ID: {state['employee_id']}\n"
        f"Reason: {state['leave_reason']}\n\n"
        f"{instruction}"
    )

    if not has_details:
        return {"messages": [llm_with_tools.invoke([SystemMessage(content=prompt)] + state["messages"])]}

    res = structured_llm.invoke([SystemMessage(content=prompt)] + state["messages"])
    return {
        "urgency": res.urgency, "risk_explanation": res.risk_explanation,
        "decision": res.decision, "decision_explanation": res.decision_explanation
    }

def routing_decision(state: LeaveState):
    print("[Execution Trace] Decision")
    if getattr(state["messages"][-1], "tool_calls", None):
        return "tool"
    return {"Approve": "finalize", "Need Info": "employee_clarification"}.get(state["decision"], "human_review")

def human_review_node(state: LeaveState):
    print("[Execution Trace] Human Review")
    return {}

def human_review_router(state: LeaveState):
    return "finalize" if (state["manager_decision"] or "").lower() in ["approve", "approved", "y", "yes"] else "employee_clarification"

def employee_clarification_node(state: LeaveState):
    print("[Execution Trace] Employee Clarification")
    mgr = state["manager_decision"]
    prompt = (
        f"Manager rejection: '{mgr}'\n" if mgr else "AI needs clarification.\n"
        f"Leave Reason: '{state['leave_reason']}'\nExplanation: {state['decision_explanation']}\n"
        "Ask employee for clarification or date modification."
    )
    res = clarification_llm.invoke([HumanMessage(content=prompt)] + state["messages"])
    print(f"\nAI request to employee: {getattr(res, 'question', 'Please clarify your request.')}")
    ans = input("Employee Response: ").strip()
    
    return {
        "employee_response": ans,
        "leave_reason": f"{state['leave_reason']} (Clarification: {ans})",
        "manager_decision": None,
        "messages": [HumanMessage(content=ans)]
    }

def finalize_node(state: LeaveState):
    print("[Execution Trace] Finalize\nFinal Decision:", status := "Approved (Auto)" if state["decision"] == "Approve" else "Approved (Manager)")
    return {"final_status": status}

# Graph Construction
builder = StateGraph(LeaveState)
builder.add_node("tool", tool_node)
builder.add_node("llm_assessment", llm_assessment_node)
builder.add_node("human_review", human_review_node)
builder.add_node("employee_clarification", employee_clarification_node)
builder.add_node("finalize", finalize_node)

builder.add_edge(START, "tool")
builder.add_edge("tool", "llm_assessment")
builder.add_conditional_edges("llm_assessment", routing_decision)
builder.add_conditional_edges("human_review", human_review_router)
builder.add_edge("employee_clarification", "llm_assessment")
builder.add_edge("finalize", END)

if __name__ == "__main__":
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory, interrupt_before=["human_review"])
    visualize_graph(graph, "leave_workflow.png")
    
    print("\n=== AI Leave Approval Workflow Agent ===")
    print("Available Employee IDs: EMP001, EMP002, EMP003")
    
    while True:
        emp_id = input("\nEnter Employee ID (or 'exit'): ").strip().upper()
        if emp_id == "EXIT":
            break
        if emp_id not in EMPLOYEES:
            print("Invalid ID.")
            continue
            
        reason = input("Enter Leave Reason: ").strip()
        if not reason:
            continue
            
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        graph.invoke({
            "employee_id": emp_id,
            "leave_reason": reason,
            "messages": [HumanMessage(content=f"Employee {emp_id} requests leave for: {reason}")]
        }, config)
        
        state = graph.get_state(config)
        if not state.next:
            print("\nProcess Completed Automatically.")
        while state.next:
            print(f"\nEscalated for Human Review.\nUrgency: {state.values.get('urgency')} | Risk: {state.values.get('risk_explanation')}\nExplanation: {state.values.get('decision_explanation')}")
            graph.update_state(config, {"manager_decision": "reject" if input("Decision (approve/reject): ").strip().lower() == "reject" else "approve"}, as_node="human_review")
            graph.invoke(None, config)
            state = graph.get_state(config)
