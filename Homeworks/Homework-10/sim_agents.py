import json
import time
import uuid


def _safe_loads(message: bytes):
    try:
        return json.loads(message.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def main() -> None:
    try:
        from kafka import KafkaConsumer, KafkaProducer
    except ImportError as exc:
        raise ImportError(
            "kafka-python is required. Install with: pip install kafka-python"
        ) from exc

    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    consumer = KafkaConsumer(
        "inbox",
        bootstrap_servers="localhost:9092",
        value_deserializer=_safe_loads,
        auto_offset_reset="latest",
    )

    print("Starting agent simulation. Waiting for messages on 'inbox'...")

    for msg in consumer:
        try:
            data = msg.value
            cid = data.get("correlation_id", str(uuid.uuid4()))
            question = data.get("content", "Unknown question")

            print(f"\n[Planner] Received question: {question}")
            plan = (
                "1. Define fault tolerance.\n"
                "2. Explain replication and consensus.\n"
                "3. Provide examples."
            )
            producer.send("tasks", {"correlation_id": cid, "content": plan})
            producer.flush()
            time.sleep(1)

            print("[Writer] Drafted answer based on plan.")
            draft = "Fault tolerance is when systems do not fail. They use replication."
            producer.send("drafts", {"correlation_id": cid, "content": draft})
            producer.flush()
            time.sleep(1)

            print("[Reviewer] Refined answer.")
            final = (
                "Fault tolerance ensures a distributed system continues operating even if some "
                "components fail. This is typically achieved through data replication and "
                "distributed consensus protocols like Paxos or Raft."
            )
            producer.send("final", {"correlation_id": cid, "content": final})
            producer.flush()
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
