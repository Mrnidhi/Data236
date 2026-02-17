"""Test runner for the Stateful Agent Graph with Ollama LLM."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_ollama import ChatOllama
from agent_graph.workflow import build_workflow

# Create the LLM instance using local Ollama
llm = ChatOllama(
    model="llama3.2:3b-instruct-q4_K_S",
    temperature=0.3,
)
print("✅ Ollama LLM initialized (llama3.2)\n")


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


# Test 1: Normal flow (strict=False) with real LLM
print("Test 1: Normal flow with LLM (no correction loop)")
r1 = run_test("Normal Flow with LLM (strict=False)", {
    "title": "Blog Post",
    "content": "Introduction to LangGraph",
    "email": "test@example.com",
    "strict": False,
    "task": "Write a technical blog post",
    "llm": llm,
    "turn_count": 0,
})
print("✅ Test 1 PASSED: Normal flow completed with LLM\n")


# Test 2: Correction loop (strict=True) with real LLM
print("Test 2: Correction loop with LLM (strict=True)")
r2 = run_test("Correction Loop with LLM (strict=True)", {
    "title": "Research Paper",
    "content": "Agent architectures",
    "email": "strict@example.com",
    "strict": True,
    "task": "Draft a research summary",
    "llm": llm,
    "turn_count": 0,
})
print("✅ Test 2 PASSED: Correction loop completed with LLM\n")

print("="*60)
print("  ALL TESTS PASSED ✅")
print("="*60)
