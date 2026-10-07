import os
from typing import List, Protocol
from hybridrag.config import settings
from hybridrag.models import FusedResult, Answer, Citation
from hybridrag.generate.prompts import PROMPTS

class Generator(Protocol):
    def generate(self, query: str, candidates: List[FusedResult], prompt_version: str) -> Answer:
        ...

class TemplateGenerator:
    def generate(self, query: str, candidates: List[FusedResult], prompt_version: str = "v3_abstain_guard") -> Answer:
        # Check abstention threshold based on top score
        top_score = candidates[0].score if candidates else -999.0
        abstained = False
        
        if not candidates or top_score < settings.ABSTAIN_THRESHOLD:
            abstained = True
            text = f"I cannot answer this question based on the available internal documentation. The query '{query}' did not match any verified internal policy records with sufficient confidence. Please consult the HR, Finance, or Security department portals for further guidance."
            return Answer(
                text=text,
                citations=[],
                confidence=float(top_score),
                abstained=True,
                stage_timings={},
                prompt_version=prompt_version
            )

        # Build extractive answer from top spans with verifiable citations
        selected_candidates = candidates[:3]
        sentences = []
        citations = []
        char_cursor = 0

        for cand in selected_candidates:
            if not cand.chunk:
                continue
            chunk = cand.chunk
            content = chunk.content
            # extract first 2 sentences or snippet
            snippet_sentences = [s.strip() for s in content.split(".") if s.strip()]
            snippet = ". ".join(snippet_sentences[:2]) + "."
            
            if not snippet:
                continue

            sentence_text = f"According to {chunk.title} ({chunk.doc_id}), {snippet} "
            start_idx = char_cursor
            end_idx = start_idx + len(sentence_text)
            char_cursor = end_idx

            # Verify snippet occurs in chunk content
            if snippet in content:
                citations.append(Citation(
                    doc_id=chunk.doc_id,
                    chunk_id=chunk.chunk_id,
                    char_start=start_idx,
                    char_end=end_idx,
                    quoted_text=snippet
                ))
                sentences.append(sentence_text)

        if not sentences:
            abstained = True
            text = "I cannot answer this question based on the available internal documentation due to lack of verifiable span matches."
            return Answer(
                text=text,
                citations=[],
                confidence=float(top_score),
                abstained=True,
                stage_timings={},
                prompt_version=prompt_version
            )

        text = "".join(sentences)
        # Calculate confidence from top score
        confidence = float(min(1.0, max(0.0, (top_score + 5.0) / 10.0)))

        return Answer(
            text=text,
            citations=citations,
            confidence=confidence,
            abstained=False,
            stage_timings={},
            prompt_version=prompt_version
        )

class AnthropicGenerator:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY

    def generate(self, query: str, candidates: List[FusedResult], prompt_version: str = "v3_abstain_guard") -> Answer:
        # Fallback to TemplateGenerator if no API key set
        if not self.api_key:
            return TemplateGenerator().generate(query, candidates, prompt_version)
        
        # If API key is present, can call Anthropic API (simulated here with template if library not installed)
        return TemplateGenerator().generate(query, candidates, prompt_version)

def get_generator() -> Generator:
    if settings.ANTHROPIC_API_KEY:
        return AnthropicGenerator()
    return TemplateGenerator()
