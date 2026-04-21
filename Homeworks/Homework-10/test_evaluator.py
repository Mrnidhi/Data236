import json
import subprocess
import sys
import time
import uuid
from pathlib import Path


def main() -> None:
    import json

    try:
        from kafka import KafkaProducer
    except ImportError as exc:
        raise ImportError(
            "kafka-python is required. Install with: pip install kafka-python"
        ) from exc

    cid = str(uuid.uuid4())[:8]
    print(f"Using correlation_id: {cid}")

    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    topics_data = {
        "inbox": {
            "correlation_id": cid,
            "content": "How do distributed systems handle fault tolerance?",
        },
        "tasks": {
            "correlation_id": cid,
            "content": (
                "1. Define fault tolerance.\n"
                "2. Explain replication and consensus.\n"
                "3. Provide examples."
            ),
        },
        "drafts": {
            "correlation_id": cid,
            "content": "Fault tolerance is when systems do not fail. They use replication.",
        },
        "final": {
            "correlation_id": cid,
            "content": (
                "Fault tolerance ensures a distributed system continues operating even if some "
                "components fail. This is typically achieved through data replication and "
                "distributed consensus protocols like Paxos or Raft."
            ),
        },
    }

    for topic, data in topics_data.items():
        producer.send(topic, data)
        print(f"Sent to {topic}")

    producer.flush()
    time.sleep(2)

    print("\nRunning evaluator...")
    evaluator_script = Path(__file__).resolve().with_name("ge-eval2.py")
    subprocess.run(
        [sys.executable, str(evaluator_script), "--timeout", "120", "--correlation-id", cid],
        check=True,
    )


if __name__ == "__main__":
    main()
