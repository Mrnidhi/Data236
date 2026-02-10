"""Test runner for the Stateful Agent Graph (realtygraph)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_graph.workflow import build_workflow

def run_test(test_name, initial_state):
    print(f"\n{'='*60}")
    print(f"  {test_name}")
    print(f"{'='*60}")

    graph = build_workflow()
    result = graph.invoke(initial_state)

    print(f"\n--- Final State ---")
    print(f"  Turn count: {result.get('turn_count')}")
    print(f"  Planner proposal: {result.get('planner_proposal')}")
    print(f"  Reviewer feedback: {result.get('reviewer_feedback')}")
    print()
    return result


# Test 1: Normal flow (strict=False) — should go Supervisor→Planner→Supervisor→Reviewer→Supervisor→END
print("Test 1: Normal flow (no correction loop)")
r1 = run_test("Normal Flow (strict=False)", {
    "title": "Blog Post",
    "content": "Introduction to LangGraph",
    "email": "test@example.com",
    "strict": False,
    "task": "Write a technical blog post",
    "llm": None,
    "turn_count": 0,
})
assert r1["reviewer_feedback"]["approved"] == True, "Test 1 FAILED: should be approved"
assert r1["reviewer_feedback"]["has_issues"] == False, "Test 1 FAILED: should have no issues"
print("✅ Test 1 PASSED: Normal flow completed successfully\n")


# Test 2: Correction loop (strict=True) — should loop back to Planner once
print("Test 2: Correction loop (strict=True)")
r2 = run_test("Correction Loop (strict=True)", {
    "title": "Research Paper",
    "content": "Agent architectures",
    "email": "strict@example.com",
    "strict": True,
    "task": "Draft a research summary",
    "llm": None,
    "turn_count": 0,
})
assert r2["reviewer_feedback"]["approved"] == True, "Test 2 FAILED: should be approved after revision"
assert r2["planner_proposal"]["revised"] == True, "Test 2 FAILED: proposal should be revised"
print("✅ Test 2 PASSED: Correction loop worked correctly\n")

print("="*60)
print("  ALL TESTS PASSED ✅")
print("="*60)
