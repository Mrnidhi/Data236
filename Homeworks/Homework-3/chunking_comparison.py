"""
Comparison of LlamaIndex Chunking Techniques on Tiny Shakespeare
"""


import time
import requests
import numpy as np
import pandas as pd

from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import (
    TokenTextSplitter,
    SentenceWindowNodeParser,
)
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# Configuration

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DATASET_URL = (
    "https://raw.githubusercontent.com/karpathy/char-rnn/master/"
    "data/tinyshakespeare/input.txt"
)
TOP_K = 5
PRIMARY_QUERY = "Who are the two feuding houses?"
OPTIONAL_QUERIES = [
    "Who is Romeo in love with?",
    "Which play contains the line 'To be, or not to be'?",
]

print("Loading HuggingFace embedding model …")
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
Settings.embed_model = embed_model

print("Downloading Tiny Shakespeare dataset …")
shakespeare_text = requests.get(DATASET_URL, timeout=30).text
print(f"  ✓ Downloaded {len(shakespeare_text):,} characters.\n")

document = Document(text=shakespeare_text)




def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))




def retrieve_and_report(technique_name: str, index: VectorStoreIndex,
                        query: str, k: int = TOP_K):
    """
    For a given index and query:
    - Compute the query embedding and print dimension + first 8 values
    - Retrieve top-k nodes
    - Compute explicit cosine similarity for each result
    - Print a formatted table
    Returns a dict of summary metrics.
    """
    print(f"\n{'='*80}")
    print(f"  Technique: {technique_name}")
    print(f"  Query    : \"{query}\"")
    print(f"{'='*80}")

    # Query embedding
    q_emb = np.array(embed_model.get_query_embedding(query))
    print(f"  Query embedding dimension : {q_emb.shape[0]}")
    print(f"  First 8 values            : {q_emb[:8].tolist()}")

    # Retrieve
    retriever = index.as_retriever(similarity_top_k=k)
    t0 = time.perf_counter()
    results = retriever.retrieve(query)
    latency_ms = (time.perf_counter() - t0) * 1000

    rows = []
    doc_embeddings = []
    for rank, node_with_score in enumerate(results, start=1):
        node = node_with_score.node
        store_score = node_with_score.score
        text = node.get_content()
        chunk_len = len(text)
        preview = text[:160].replace("\n", " ")

        # Get document embedding from the node
        if node.embedding is not None:
            d_emb = np.array(node.embedding)
        else:
            d_emb = np.array(embed_model.get_text_embedding(text))
        doc_embeddings.append(d_emb)
        cos_sim = cosine_similarity(q_emb, d_emb)

        rows.append({
            "rank": rank,
            "store_score": round(store_score, 4),
            "cosine_sim": round(cos_sim, 4),
            "chunk_len": chunk_len,
            "preview": preview
        })

    df = pd.DataFrame(rows)

    # Shapes
    doc_matrix = np.vstack(doc_embeddings)
    print(f"\n  Query vector shape       : {q_emb.shape}")
    print(f"  Document vectors shape   : {doc_matrix.shape}")
    print(f"  Retrieval latency        : {latency_ms:.1f} ms\n")

    # Table
    print(df.to_string(index=False))

    # Summary metrics
    top1_cos = rows[0]["cosine_sim"] if rows else 0.0
    mean_cos = float(np.mean([r["cosine_sim"] for r in rows])) if rows else 0.0

    return {
        "technique": technique_name,
        "top1_cosine": top1_cos,
        "mean_at_k_cosine": round(mean_cos, 4),
        "latency_ms": round(latency_ms, 1),
    }




# Token-based chunking
def build_token_index(doc: Document):
    splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=64)
    nodes = splitter.get_nodes_from_documents([doc])
    print(f"Token-based chunking  → {len(nodes)} chunks, "
          f"avg length {int(np.mean([len(n.get_content()) for n in nodes]))} chars")
    index = VectorStoreIndex(nodes, embed_model=embed_model)
    return index, nodes




# Semantic chunking
def build_semantic_index(doc: Document):
    splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=embed_model,
    )
    nodes = splitter.get_nodes_from_documents([doc])
    print(f"Semantic chunking     → {len(nodes)} chunks, "
          f"avg length {int(np.mean([len(n.get_content()) for n in nodes]))} chars")
    index = VectorStoreIndex(nodes, embed_model=embed_model)
    return index, nodes




# Sentence-window chunking
def build_sentence_window_index(doc: Document):
    splitter = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    nodes = splitter.get_nodes_from_documents([doc])
    print(f"Sentence-window       → {len(nodes)} chunks, "
          f"avg length {int(np.mean([len(n.get_content()) for n in nodes]))} chars")
    index = VectorStoreIndex(nodes, embed_model=embed_model)
    return index, nodes


# ──────────────────────────────────────────────
# 5.  Build all three indexes
# ──────────────────────────────────────────────



token_index, token_nodes = build_token_index(document)
semantic_index, semantic_nodes = build_semantic_index(document)
sw_index, sw_nodes = build_sentence_window_index(document)





# Run retrieval for primary query
summaries = []

s1 = retrieve_and_report("Token-Based", token_index, PRIMARY_QUERY)
s1["total_chunks"] = len(token_nodes)
s1["avg_chunk_len"] = int(np.mean([len(n.get_content()) for n in token_nodes]))
summaries.append(s1)

s2 = retrieve_and_report("Semantic", semantic_index, PRIMARY_QUERY)
s2["total_chunks"] = len(semantic_nodes)
s2["avg_chunk_len"] = int(np.mean([len(n.get_content()) for n in semantic_nodes]))
summaries.append(s2)

s3 = retrieve_and_report("Sentence-Window", sw_index, PRIMARY_QUERY)
s3["total_chunks"] = len(sw_nodes)
s3["avg_chunk_len"] = int(np.mean([len(n.get_content()) for n in sw_nodes]))
summaries.append(s3)



# Run retrieval for optional queries

for oq in OPTIONAL_QUERIES:
    retrieve_and_report("Token-Based", token_index, oq)
    retrieve_and_report("Semantic", semantic_index, oq)
    retrieve_and_report("Sentence-Window", sw_index, oq)



# Comparison report
print("\n\n" + "="*80)
print("COMPARISON REPORT")
print("="*80)

report_df = pd.DataFrame(summaries)[[
    "technique", "top1_cosine", "mean_at_k_cosine",
    "total_chunks", "avg_chunk_len", "latency_ms"
]]
report_df.columns = [
    "Technique", "Top-1 Cosine", "Mean@k Cosine",
    "Total Chunks", "Avg Chunk Len", "Latency (ms)"
]
print("\n### Retrieval Quality Table\n")
print(report_df.to_string(index=False))

print("\nDone ✓")

