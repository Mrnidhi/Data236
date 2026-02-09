from typing import TypedDict, Dict, Any, Literal
from langgraph.graph import StateGraph, END

# --- Step 1 & 2: Setting up the State (MANDATORY STRUCTURE) ---
class AgentState(TypedDict):
    title: str
    content: str
    email: str
    strict: bool
    task: str
    llm: Any
    planner_proposal: Dict[str, Any]
    reviewer_feedback: Dict[str, Any]
    turn_count: int

# --- Step 3: Creating the Agent Nodes ---

def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Node: Generates a proposal.
    Accepts state, performs task, returns dictionary update.
    """
    print(f"\n--- Planner Node (Turn {state.get('turn_count', 0)}) ---")
    
    current_feedback = state.get("reviewer_feedback")
    
    if current_feedback and current_feedback.get("has_issues"):
        print(f"Planner: Received feedback '{current_feedback.get('feedback')}'. Refining proposal...")
        proposal = {
            "title": state["title"],
            "content": f"{state['task']} - REFINED VERSION (Fixed feedback)",
            "status": "revised"
        }
    else:
        print("Planner: Generating initial proposal...")
        initial_content = f"{state['task']} - DRAFT 1"
        proposal = {
            "title": state["title"],
            "content": initial_content,
            "status": "draft"
        }

    return {
        "planner_proposal": proposal,
        "reviewer_feedback": None 
    }

def reviewer_node(state: AgentState) -> Dict[str, Any]:
    """
    Reviewer Node: Reviews the proposal.
    Returns feedback with 'has_issues' boolean.
    """
    print(f"\n--- Reviewer Node (Turn {state.get('turn_count', 0)}) ---")
    
    proposal = state.get("planner_proposal", {})
    content = proposal.get("content", "")
    
    has_issues = False
    feedback_msg = "Looks good!"
    
    if state.get("strict") and "DRAFT 1" in content:
        has_issues = True
        feedback_msg = "Content is too basic (Draft 1). Please refine."
    
    print(f"Reviewer: Accessing proposal: '{content}'")
    print(f"Reviewer: Verdict -> Issues: {has_issues}, Msg: {feedback_msg}")

    return {
        "reviewer_feedback": {
            "has_issues": has_issues,
            "feedback": feedback_msg
        }
    }

# --- Step 4: Building the Supervisor (The Router) ---

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    State-Updating Node (supervisor_node): 
    This node's only job is to modify the state, like incrementing the turn counter.
    """
    current_count = state.get("turn_count", 0)
    new_count = current_count + 1

    return {"turn_count": new_count}

def router_logic(state: AgentState) -> Literal["planner", "reviewer", "end"]:
    """
    Routing Function (router_logic):
    Reads the state and decides where to go next.
    """
    turn_limit = 5
    if state.get("turn_count", 0) > turn_limit:
        print("Supervisor: Turn limit reached. Terminating.")
        return "end"

    proposal = state.get("planner_proposal")
    feedback = state.get("reviewer_feedback")

    if feedback:
        if feedback.get("has_issues"):
            print("Supervisor: Reviewer found issues. Routing back to -> PLANNER")
            return "planner"
        else:
            print("Supervisor: Reviewer accepted proposal. Routing to -> END")
            return "end"

    if proposal:
        print("Supervisor: Proposal exists, pending review. Routing to -> REVIEWER")
        return "reviewer"

    print("Supervisor: No proposal found. Routing to -> PLANNER")
    return "planner"

# --- Step 5: Assembling the Graph ---

workflow = StateGraph(AgentState)


workflow.add_node("planner", planner_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("supervisor", supervisor_node)


workflow.add_edge("planner", "supervisor")
workflow.add_edge("reviewer", "supervisor")


workflow.set_entry_point("supervisor")


workflow.add_conditional_edges(
    "supervisor",
    router_logic,
    {
        "planner": "planner",
        "reviewer": "reviewer",
        "end": END
    }
)


app = workflow.compile()

# --- Step 6: Running and Testing ---

def run_tests():
    print("\n\n========== TEST 1: Normal Execution (No Issues) ==========")
    initial_state_1 = {
        "title": "My Book",
        "content": "",
        "email": "test@example.com",
        "strict": False,
        "task": "Write a chapter",
        "llm": None,
        "planner_proposal": None,
        "reviewer_feedback": None,
        "turn_count": 0
    }
    
    for s in app.stream(initial_state_1):
        pass 

    print("\n\n========== TEST 2: Correction Loop (Forced Rejection) ==========")
    initial_state_2 = {
        "title": "My Book",
        "content": "",
        "email": "test@example.com",
        "strict": True,
        "task": "Write a chapter",
        "llm": None,
        "planner_proposal": None,
        "reviewer_feedback": None,
        "turn_count": 0
    }

    for s in app.stream(initial_state_2):
        pass

if __name__ == "__main__":
    run_tests()

# --- Intended Output Description ---
"""
Intended Output:

1. Normal Execution Flow (Test 1):
   - Supervisor (Turn 1): Routes to Planner.
   - Planner: Generates "Draft 1".
   - Supervisor (Turn 2): Routes to Reviewer.
   - Reviewer: "Looks good!" (Strict=False).
   - Supervisor (Turn 3): Routes to END.

2. Loop-back Behavior (Test 2):
   - Supervisor (Turn 1): Routes to Planner.
   - Planner: Generates "Draft 1".
   - Supervisor (Turn 2): Routes to Reviewer.
   - Reviewer: "Content too basic". Has Issues = True.
   - Supervisor (Turn 3): Routes back to Planner (Loop).
   - Planner: Sees feedback. Generates "REFINED VERSION".
   - Supervisor (Turn 4): Routes to Reviewer.
   - Reviewer: "Looks good!" (Revised version is accepted).
   - Supervisor (Turn 5): Routes to END.

3. Termination Condition:
   - The graph successfully terminates when `has_issues` is False.
   - If it looped indefinitely, `turn_count > 5` would force termination.
"""
