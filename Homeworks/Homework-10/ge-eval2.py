import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from deepeval.metrics import GEval
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from openai import OpenAI


TOPIC_INBOX = os.getenv("TOPIC_INBOX", "inbox")
TOPIC_TASKS = os.getenv("TOPIC_TASKS", "tasks")
TOPIC_DRAFTS = os.getenv("TOPIC_DRAFTS", "drafts")
TOPIC_FINAL = os.getenv("TOPIC_FINAL", "final")
TOPIC_EVAL_RESULTS = os.getenv("TOPIC_EVAL_RESULTS", "eval_results")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "geval-evaluator-v1")
KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_JUDGE_MODEL = os.getenv("OLLAMA_JUDGE_MODEL", "llama3.1:8b")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")


class OllamaJudgeModel(DeepEvalBaseLLM):
    """Judge model adapter for Ollama."""

    def __init__(self, model_name: str, base_url: str, api_key: str):
        self.model_name = model_name
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content.strip()

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return self.model_name


@dataclass
class CorrelatedBundle:
    correlation_id: str
    question: Optional[str] = None
    plan: Optional[str] = None
    draft: Optional[str] = None
    final: Optional[str] = None
    updated_at: float = 0.0


def _extract_text(payload: Dict[str, Any]) -> str:
    for key in ("content", "message", "text", "answer", "plan", "draft", "final"):
        value = payload.get(key)
        if isinstance(value, str):
            return value.strip()
    return ""


def _topic_to_stage(topic: str) -> str:
    mapping = {
        TOPIC_INBOX: "question",
        TOPIC_TASKS: "plan",
        TOPIC_DRAFTS: "draft",
        TOPIC_FINAL: "final",
    }
    return mapping.get(topic, "unknown")


def _safe_deserialize_kafka_value(raw_value: bytes) -> Optional[Dict[str, Any]]:
    try:
        payload = json.loads(raw_value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def build_metrics(judge_model: DeepEvalBaseLLM) -> Dict[str, GEval]:
    plan_quality = GEval(
        name="Plan Quality",
        criteria=(
            "Assess whether ACTUAL_OUTPUT is a structured, actionable plan for INPUT. "
            "Reward clear steps, logical order, and task relevance. Penalize vague or missing steps."
        ),
        evaluation_steps=[
            "Read the INPUT question.",
            "Verify the ACTUAL_OUTPUT contains clear ordered steps.",
            "Evaluate if the plan directly addresses the INPUT.",
            "Output a score from 1-10 based on these criteria.",
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge_model,
    )

    helpfulness = GEval(
        name="Helpfulness",
        criteria=(
            "Assess whether ACTUAL_OUTPUT is helpful, relevant, and complete for INPUT. "
            "Reward clarity and correctness; penalize irrelevance or major omissions."
        ),
        evaluation_steps=[
            "Read the INPUT question.",
            "Analyze the ACTUAL_OUTPUT for correctness and relevance.",
            "Check for completeness.",
            "Output a score from 1-10 based on helpfulness.",
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge_model,
    )

    improvement = GEval(
        name="Final-vs-Draft Improvement",
        criteria=(
            "EXPECTED_OUTPUT is the Writer draft. ACTUAL_OUTPUT is the Reviewer final answer. "
            "Score higher when ACTUAL_OUTPUT is better in accuracy, clarity, structure, and actionability."
        ),
        evaluation_steps=[
            "Compare EXPECTED_OUTPUT (draft) with ACTUAL_OUTPUT (final).",
            "Determine if ACTUAL_OUTPUT is clearer, more structured, or more accurate.",
            "Check that ACTUAL_OUTPUT did not remove important information.",
            "Output a score from 1-10 indicating the degree of improvement.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        model=judge_model,
    )

    return {
        "plan_quality": plan_quality,
        "helpfulness": helpfulness,
        "improvement": improvement,
    }


def evaluate_bundle(bundle: CorrelatedBundle, metrics: Dict[str, GEval]) -> Dict[str, Any]:
    input_text = bundle.question or ""

    plan_case = LLMTestCase(
        input=input_text,
        actual_output=bundle.plan or "",
        expected_output="",
    )
    metrics["plan_quality"].measure(plan_case)

    draft_case = LLMTestCase(
        input=input_text,
        actual_output=bundle.draft or "",
        expected_output="",
    )
    metrics["helpfulness"].measure(draft_case)
    helpfulness_draft = float(metrics["helpfulness"].score)

    final_case = LLMTestCase(
        input=input_text,
        actual_output=bundle.final or "",
        expected_output="",
    )
    metrics["helpfulness"].measure(final_case)
    helpfulness_final = float(metrics["helpfulness"].score)

    improvement_case = LLMTestCase(
        input=input_text,
        expected_output=bundle.draft or "",
        actual_output=bundle.final or "",
    )
    metrics["improvement"].measure(improvement_case)

    return {
        "correlation_id": bundle.correlation_id,
        "scores": {
            "plan_quality": float(metrics["plan_quality"].score),
            "helpfulness_draft": helpfulness_draft,
            "helpfulness_final": helpfulness_final,
            "final_vs_draft_improvement": float(metrics["improvement"].score),
        },
        "reasoning": {
            "plan_quality": metrics["plan_quality"].reason,
            "helpfulness_draft": "Measured with Helpfulness metric.",
            "helpfulness_final": "Measured with Helpfulness metric.",
            "final_vs_draft_improvement": metrics["improvement"].reason,
        },
        "evaluated_at": int(time.time()),
    }


def _is_ready(bundle: CorrelatedBundle) -> bool:
    return bool(bundle.question and bundle.plan and bundle.draft and bundle.final)


def _create_consumer(group_id: str, auto_offset_reset: str):
    try:
        from kafka import KafkaConsumer
    except ImportError as exc:
        raise ImportError(
            "kafka-python is required. Install with: pip install kafka-python"
        ) from exc

    return KafkaConsumer(
        TOPIC_INBOX,
        TOPIC_TASKS,
        TOPIC_DRAFTS,
        TOPIC_FINAL,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True,
        value_deserializer=_safe_deserialize_kafka_value,
    )


def _create_producer():
    try:
        from kafka import KafkaProducer
    except ImportError as exc:
        raise ImportError(
            "kafka-python is required. Install with: pip install kafka-python"
        ) from exc

    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda data: json.dumps(data).encode("utf-8"),
    )


def run_kafka_evaluator(
    target_correlation_id: Optional[str], timeout_seconds: int
) -> Optional[Dict[str, Any]]:
    judge_model = OllamaJudgeModel(
        model_name=OLLAMA_JUDGE_MODEL,
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
    )
    metrics = build_metrics(judge_model)

    if target_correlation_id:
        effective_group_id = f"{KAFKA_GROUP_ID}-{target_correlation_id}-{int(time.time())}"
    else:
        effective_group_id = f"{KAFKA_GROUP_ID}-{int(time.time())}"

    auto_offset_reset = "earliest" if target_correlation_id else KAFKA_AUTO_OFFSET_RESET

    consumer = _create_consumer(
        group_id=effective_group_id,
        auto_offset_reset=auto_offset_reset,
    )
    producer = _create_producer()

    state: Dict[str, CorrelatedBundle] = {}
    start = time.time()

    print("Listening for Kafka messages on topics: inbox, tasks, drafts, final")

    try:
        while time.time() - start < timeout_seconds:
            records = consumer.poll(timeout_ms=1000)
            if not records:
                continue

            for _, messages in records.items():
                for message in messages:
                    topic = message.topic
                    payload = message.value
                    if not isinstance(payload, dict):
                        continue

                    correlation_id = payload.get("correlation_id")
                    if not correlation_id:
                        continue
                    if target_correlation_id and correlation_id != target_correlation_id:
                        continue

                    stage = _topic_to_stage(topic)
                    text = _extract_text(payload)
                    if not text:
                        continue

                    if correlation_id not in state:
                        state[correlation_id] = CorrelatedBundle(correlation_id=correlation_id)

                    bundle = state[correlation_id]
                    bundle.updated_at = time.time()

                    if stage == "question":
                        bundle.question = text
                    elif stage == "plan":
                        bundle.plan = text
                    elif stage == "draft":
                        bundle.draft = text
                    elif stage == "final":
                        bundle.final = text

                    if _is_ready(bundle):
                        result = evaluate_bundle(bundle, metrics)
                        producer.send(TOPIC_EVAL_RESULTS, result)
                        producer.flush()

                        print("\nGEval Scores")
                        print("-" * 40)
                        print(f"correlation_id: {result['correlation_id']}")
                        print(f"Plan Quality: {result['scores']['plan_quality']:.3f}")
                        print(f"Helpfulness (Draft): {result['scores']['helpfulness_draft']:.3f}")
                        print(f"Helpfulness (Final): {result['scores']['helpfulness_final']:.3f}")
                        print(
                            "Final-vs-Draft Improvement: "
                            f"{result['scores']['final_vs_draft_improvement']:.3f}"
                        )
                        print(f"Published evaluation to topic: {TOPIC_EVAL_RESULTS}")

                        return result
    finally:
        consumer.close()
        producer.close()

    print("No complete correlation group found before timeout.")
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Consume planner, writer, and reviewer Kafka messages and evaluate them with GEval."
        )
    )
    parser.add_argument(
        "--correlation-id",
        default=None,
        help="Only evaluate one specific correlation_id.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="How many seconds to wait for a complete plan, draft, and final set.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_kafka_evaluator(args.correlation_id, args.timeout)


if __name__ == "__main__":
    main()
