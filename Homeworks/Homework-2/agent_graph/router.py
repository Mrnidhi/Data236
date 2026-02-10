from __future__ import annotations

from typing import Any, Dict, Literal

from .state import AgentState

MAX_TURNS = 5


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Supervisor node: increments the turn counter."""
    turn_count = state.get("turn_count", 0) + 1
    print(f"---NODE: Supervisor --- (turn {turn_count})")
    return {"turn_count": turn_count}


def supervisor_router(state: AgentState) -> Literal["planner", "reviewer", "END"]:
    """
    Router logic for the Supervisor:
    - If turn_count exceeds MAX_TURNS → END (prevent infinite loops)
    - If no planner_proposal yet → route to Planner
    - If proposal exists but no reviewer_feedback → route to Reviewer  
    - If reviewer found issues → route back to Planner (correction loop)
    - If no issues → END
    """
    turn_count = state.get("turn_count", 0)

    if turn_count > MAX_TURNS:
        print("  Router: MAX TURNS reached → END")
        return "END"

    proposal = state.get("planner_proposal")
    feedback = state.get("reviewer_feedback")

    if not proposal:
        print("  Router: No proposal → Planner")
        return "planner"

    if not feedback:
        print("  Router: Has proposal, no feedback → Reviewer")
        return "reviewer"

    if feedback.get("has_issues"):
        print("  Router: Has issues → Planner (correction loop)")
        return "planner"

    print("  Router: No issues → END")
    return "END"
