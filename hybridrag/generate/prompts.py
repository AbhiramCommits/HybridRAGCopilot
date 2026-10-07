from dataclasses import dataclass
from typing import Dict

@dataclass
class PromptVersion:
    name: str
    template: str
    changelog: str

PROMPTS: Dict[str, PromptVersion] = {
    "v1_basic": PromptVersion(
        name="v1_basic",
        template="Answer the user's question using the provided context passages.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:",
        changelog="Basic baseline prompt without strict citation or abstention constraints."
    ),
    "v2_strict_citation": PromptVersion(
        name="v2_strict_citation",
        template="You are an enterprise document copilot. Answer the question using ONLY the provided context passages. Every claim must include a citation [DocID]. If the context is insufficient, state so clearly.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:",
        changelog="Added strict citation requirement and instruction to use only provided context."
    ),
    "v3_abstain_guard": PromptVersion(
        name="v3_abstain_guard",
        template="You are an enterprise document copilot. Answer the question accurately using ONLY the provided context passages with exact citations. If the context does not contain the answer or confidence is low, you must ABSTAIN by stating 'I cannot answer this question based on the available internal documentation.' and suggest the closest relevant document category.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:",
        changelog="Added explicit abstention guardrails, confidence thresholding, and category suggestion requirement."
    )
}
