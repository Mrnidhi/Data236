from __future__ import annotations

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import planner_node, reviewer_node
from .router import supervisor_node, supervisor_router


def build_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("reviewer", reviewer_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "planner": "planner",
            "reviewer": "reviewer",
            "END": END,
        },
    )

    workflow.add_edge("planner", "supervisor")
    workflow.add_edge("reviewer", "supervisor")

    return workflow.compile()
