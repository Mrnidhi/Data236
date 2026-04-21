import json
from pathlib import Path
from typing import Any, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.figure import Figure


MODEL_FILE = "customer_model.json"
METADATA_FILE = "customer_metadata.json"


@st.cache_resource
def load_resources(
    model_path: Path, metadata_path: Path
) -> Tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    try:
        with model_path.open("r", encoding="utf-8") as model_file:
            model = json.load(model_file)

        with metadata_path.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)

        return model, metadata
    except FileNotFoundError:
        st.error(
            "Model files not found. Run train_customer_model.py first to create the JSON files."
        )
        return None, None
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        st.error("Unable to load model resources. Re-run train_customer_model.py.")
        return None, None


def predict_cluster(user_point: np.ndarray, cluster_centers: np.ndarray) -> int:
    distances = np.linalg.norm(cluster_centers - user_point, axis=1)
    return int(np.argmin(distances))


def build_plot(
    training_data: np.ndarray, predicted_labels: np.ndarray, user_point: np.ndarray
) -> Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(
        training_data[:, 0],
        training_data[:, 1],
        c=predicted_labels,
        cmap="tab10",
        alpha=0.6,
        edgecolor="none",
    )

    ax.scatter(
        user_point[0],
        user_point[1],
        c="red",
        s=180,
        marker="X",
        label="Current Customer",
        edgecolor="black",
        linewidth=1,
    )

    ax.set_xlabel("Annual Income (k$)")
    ax.set_ylabel("Spending Score (1-100)")
    ax.set_title("Customer Segments (K-Means, k=5)")
    legend = ax.legend(*scatter.legend_elements(), title="Cluster")
    ax.add_artist(legend)
    ax.legend(loc="lower right")

    return fig


base_dir = Path(__file__).resolve().parent


def main() -> None:
    model, metadata = load_resources(base_dir / MODEL_FILE, base_dir / METADATA_FILE)

    st.title("Customer Segmentation with K-Means")
    st.markdown("Predict the cluster for a customer using Annual Income and Spending Score.")

    if model is not None and metadata is not None:
        feature_names = metadata["feature_names"]
        training_data = np.asarray(metadata["training_data"])
        cluster_centers = np.asarray(model["cluster_centers"])

        st.sidebar.header("Customer Profile")
        annual_income = st.sidebar.slider(feature_names[0], min_value=15, max_value=150, value=60)
        spending_score = st.sidebar.slider(feature_names[1], min_value=1, max_value=100, value=50)

        user_input = np.array([[annual_income, spending_score]], dtype=float)
        predicted_cluster = predict_cluster(user_input[0], cluster_centers)

        st.metric(label="Predicted Cluster ID", value=predicted_cluster)

        predicted_labels = np.array(
            [predict_cluster(point, cluster_centers) for point in training_data], dtype=int
        )
        plot = build_plot(training_data, predicted_labels, user_input[0])
        st.pyplot(plot)


if __name__ == "__main__":
    main()
