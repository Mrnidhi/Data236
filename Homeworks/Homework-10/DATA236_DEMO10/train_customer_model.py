import json
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans


RANDOM_SEED = 42
N_SAMPLES = 200
N_CLUSTERS = 5
MODEL_FILENAME = "customer_model.json"
METADATA_FILENAME = "customer_metadata.json"


def simulate_customer_data(
    n_samples: int = N_SAMPLES, seed: int = RANDOM_SEED
) -> np.ndarray:
    rng = np.random.default_rng(seed)

    annual_income = rng.uniform(15, 150, size=n_samples)
    spending_score = rng.uniform(1, 100, size=n_samples)

    return np.column_stack((annual_income, spending_score))


def train_model(data: np.ndarray) -> KMeans:
    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED, n_init=10)
    model.fit(data)
    return model


def save_artifacts(model: KMeans, data: np.ndarray, output_dir: Path) -> None:
    model_path = output_dir / MODEL_FILENAME
    metadata_path = output_dir / METADATA_FILENAME

    model_payload = {
        "cluster_centers": model.cluster_centers_.tolist(),
        "n_clusters": N_CLUSTERS,
    }

    metadata = {
        "feature_names": ["Annual Income (k$)", "Spending Score (1-100)"],
        "training_data": data.tolist(),
        "random_seed": RANDOM_SEED,
        "n_samples": int(data.shape[0]),
        "n_clusters": N_CLUSTERS,
    }

    with model_path.open("w", encoding="utf-8") as model_file:
        json.dump(model_payload, model_file, indent=2)

    with metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)

    print(f"Saved model to: {model_path}")
    print(f"Saved metadata to: {metadata_path}")


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    data = simulate_customer_data()
    model = train_model(data)
    save_artifacts(model, data, output_dir)


if __name__ == "__main__":
    main()
