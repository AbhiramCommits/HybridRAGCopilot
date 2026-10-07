import os
import json
import random
import time
import argparse
import numpy as np
from hybridrag.config import settings
from hybridrag.retrieval.hybrid import HybridRetriever
from hybridrag.generate.generator import TemplateGenerator
from hybridrag.eval.metrics import create_eval_questions
from hybridrag.eval.scoring import (
    recall_at_k, reciprocal_rank, ndcg_at_k, 
    citation_precision, faithfulness, abstention_accuracy
)

def run_eval(modes: list[str], embedding_backends: list[str], regression_mode: bool = False):
    if not os.path.exists("data/eval/questions.jsonl"):
        create_eval_questions()

    questions = []
    with open("data/eval/questions.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            questions.append(json.loads(line))

    if regression_mode:
        questions = questions[:10]

    results_matrix = {}
    generator = TemplateGenerator()

    for backend in embedding_backends:
        print(f"Evaluating embedding backend: {backend}")
        retriever = HybridRetriever(embedding_mode=backend)

        for mode in modes:
            print(f"  Evaluating mode: {mode}")
            rec5_list, rec10_list, mrr_list, ndcg10_list = [], [], [], []
            cit_prec_list, faith_list, abs_acc_list = [], [], []
            latencies = []

            for q_item in questions:
                query = q_item["question"]
                gold_ids = q_item["gold_doc_ids"]
                answerable = q_item["answerable"]

                t0 = time.time()
                candidates, timings = retriever.retrieve(query, k_out=20, mode=mode)
                latencies.append(timings.timings.get("total", 0.0))

                retrieved_ids = [c.chunk.doc_id for c in candidates if c.chunk]
                retrieved_chunks = [c.chunk for c in candidates if c.chunk]

                rec5_list.append(recall_at_k(retrieved_ids, gold_ids, 5))
                rec10_list.append(recall_at_k(retrieved_ids, gold_ids, 10))
                mrr_list.append(reciprocal_rank(retrieved_ids, gold_ids))
                ndcg10_list.append(ndcg_at_k(retrieved_ids, gold_ids, 10))

                answer = generator.generate(query, candidates)
                cit_prec_list.append(citation_precision(answer.citations, retrieved_chunks))
                faith_list.append(faithfulness(answer.text, answer.citations, retrieved_chunks))
                abs_acc_list.append(abstention_accuracy(answer.abstained, answerable))

            key = f"{backend}_{mode}"
            results_matrix[key] = {
                "recall_at_5": float(np.mean(rec5_list)),
                "recall_at_10": float(np.mean(rec10_list)),
                "mrr": float(np.mean(mrr_list)),
                "ndcg_at_10": float(np.mean(ndcg10_list)),
                "citation_precision": float(np.mean(cit_prec_list)),
                "faithfulness": float(np.mean(faith_list)),
                "abstention_accuracy": float(np.mean(abs_acc_list)),
                "p50_latency": float(np.percentile(latencies, 50)),
                "p95_latency": float(np.percentile(latencies, 95))
            }

    os.makedirs("results", exist_ok=True)
    timestamp = int(time.time())
    result_path = f"results/eval_{timestamp}.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(results_matrix, f, indent=2)

    md_content = "# HybridRAG Evaluation & Ablation Results\n\n"
    md_content += "| Configuration | Recall@5 | Recall@10 | MRR | nDCG@10 | Citation Precision | Faithfulness | Abstention Acc | p50 Latency (s) | p95 Latency (s) |\n"
    md_content += "|---|---|---|---|---|---|---|---|---|---|\n"

    for k, metrics in results_matrix.items():
        md_content += f"| {k} | {metrics['recall_at_5']:.3f} | {metrics['recall_at_10']:.3f} | {metrics['mrr']:.3f} | {metrics['ndcg_at_10']:.3f} | {metrics['citation_precision']:.3f} | {metrics['faithfulness']:.3f} | {metrics['abstention_accuracy']:.3f} | {metrics['p50_latency']:.3f} | {metrics['p95_latency']:.3f} |\n"

    with open("results/ablation.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    with open("results/baseline.json", "w", encoding="utf-8") as f:
        json.dump(results_matrix, f, indent=2)

    print(f"Evaluation complete. Results saved to {result_path} and results/ablation.md")
    return results_matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--regression", action="store_true")
    args = parser.parse_args()

    modes = ["dense", "bm25", "structured", "hybrid", "hybrid_rerank"]
    backends = ["base"]
    if os.path.exists(settings.LORA_MODEL_PATH):
        backends.append("lora")

    if args.regression:
        print("Running regression evaluation check...")
        res = run_eval(["hybrid_rerank"], ["base"], regression_mode=True)
        if os.path.exists("results/baseline.json"):
            with open("results/baseline.json", "r") as f:
                baseline = json.load(f)
            base_mrr = baseline.get("base_hybrid_rerank", {}).get("mrr", 0.0)
            curr_mrr = res["base_hybrid_rerank"]["mrr"]
            print(f"Baseline MRR: {base_mrr:.3f}, Current MRR: {curr_mrr:.3f}")
            if curr_mrr < base_mrr - 0.15:
                print("Regression detected! MRR dropped significantly.")
                exit(1)
        print("Regression check passed successfully.")
    else:
        run_eval(modes, backends)
