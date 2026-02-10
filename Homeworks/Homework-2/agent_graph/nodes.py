from __future__ import annotations

import json
from typing import Any, Dict

from .state import AgentState


def planner_node(state: AgentState) -> Dict[str, Any]:
    print("---NODE: Planner ---")

    llm = state.get("llm")
    title = state.get("title", "")
    content = state.get("content", "")
    email = state.get("email", "")
    task_desc = state.get("task", "")
    feedback = state.get("reviewer_feedback")

    prompt = (
        f"You are a Planner agent. Your job is to create a proposal.\n\n"
        f"Task: {task_desc}\n"
        f"Title: {title}\n"
        f"Content: {content}\n"
        f"Email: {email}\n"
    )

    if feedback and feedback.get("has_issues"):
        prompt += (
            f"\nThe Reviewer found issues with your previous proposal:\n"
            f"Issues: {json.dumps(feedback.get('issues', []))}\n"
            f"Please revise your proposal to address these issues.\n"
        )

    prompt += "\nReturn a JSON object with keys: summary, action_items (list), revised (bool)."

    if llm:
        response = llm.invoke(prompt)
        raw = getattr(response, "content", str(response))
    else:
        has_issues = feedback and feedback.get("has_issues")
        raw = json.dumps({
            "summary": f"Proposal for: {title}" + (" (REVISED)" if has_issues else ""),
            "action_items": [
                f"Process: {task_desc}",
                f"Handle content for: {email}",
            ],
            "revised": bool(has_issues),
        })

    try:
        proposal = json.loads(raw)
    except Exception:
        proposal = {"raw": raw}

    print(f"  Planner output: {json.dumps(proposal, indent=2)}")
    return {"planner_proposal": proposal, "reviewer_feedback": {}}


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    print("---NODE: Reviewer ---")

    llm = state.get("llm")
    proposal = state.get("planner_proposal", {})
    strict = state.get("strict", False)
    title = state.get("title", "")

    prompt = (
        f"You are a Reviewer agent. Review the following proposal:\n\n"
        f"Proposal: {json.dumps(proposal)}\n"
        f"Strict mode: {strict}\n"
        f"Title: {title}\n\n"
        f"Check for completeness, correctness, and quality.\n"
        f"Return JSON with keys: approved (bool), has_issues (bool), issues (list of strings)."
    )

    if llm:
        response = llm.invoke(prompt)
        raw = getattr(response, "content", str(response))
    else:
        is_revised = proposal.get("revised", False)
        if strict and not is_revised:
            raw = json.dumps({
                "approved": False,
                "has_issues": True,
                "issues": ["Proposal needs more detail for strict mode"],
            })
        else:
            raw = json.dumps({
                "approved": True,
                "has_issues": False,
                "issues": [],
            })

    try:
        feedback = json.loads(raw)
    except Exception:
        feedback = {"approved": True, "has_issues": False, "issues": [], "raw": raw}

    print(f"  Reviewer output: {json.dumps(feedback, indent=2)}")
    return {"reviewer_feedback": feedback}
