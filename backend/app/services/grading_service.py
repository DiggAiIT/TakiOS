import asyncio
import json
import re

import anthropic

from app.config import settings

_MAX_GRADE_RETRIES = 3


class GradingService:
    def __init__(self):
        self.client = (
            anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            if settings.anthropic_api_key
            else None
        )

    def _fallback_grade(
        self,
        fact: str,
        student_response: str,
        rubric: str,
        project_context: str | None = None,
    ) -> dict[str, str | float | list[str]]:
        fact_terms = {
            term for term in re.findall(r"[a-zA-Z0-9_]+", fact.lower()) if len(term) >= 4
        }
        response_terms = {
            term
            for term in re.findall(r"[a-zA-Z0-9_]+", student_response.lower())
            if len(term) >= 4
        }
        overlap = fact_terms & response_terms
        coverage = len(overlap) / max(len(fact_terms), 1)
        length_bonus = min(len(student_response.strip()) / 400, 0.2)
        score = round(min(10.0, max(0.0, (coverage + length_bonus) * 10)), 1)

        reasoning = (
            "Local fallback grading was used because no AI provider was available. "
            f"The response matched {len(overlap)} key concept(s) from the reference fact and used rubric '{rubric}'."
        )
        if project_context:
            reasoning += " Project context was preserved in the grading context review."

        feedback = (
            "Expand the answer with the exact technical terms from the source fact and align it more directly with the rubric criteria."
        )
        matched = sorted(overlap)
        missing = sorted(fact_terms - response_terms)
        hints = []
        if missing:
            hints.append(f"Address these missing concepts: {', '.join(list(missing)[:5])}")
        if len(student_response.strip()) < 100:
            hints.append("Provide a more detailed response with specific examples.")

        return {
            "score": score,
            "reasoning": reasoning,
            "feedback": feedback,
            "confidence_score": 0.0,
            "matched_concepts": matched,
            "improvement_hints": hints,
            "model_used": "local-fallback",
        }
        
    async def grade_submission(self, fact: str, student_response: str, rubric: str, project_context: str | None = None):
        if self.client is None:
            return self._fallback_grade(fact, student_response, rubric, project_context)

        prompt = f"""You are an expert educational grader specializing in medical device engineering. 
Evaluate the student's response based on the original fact.
Fact: {fact}
Student Response: {student_response}
Rubric: {rubric}
"""
        if project_context:
            prompt += f"Student's Active Project: '{project_context}'\nIMPORTANT: Evaluate whether the student's response logically applies to and makes sense within the context of their specific medical device project!\n"

        prompt += """
Return the evaluation in strict JSON format with the following keys:
- "score": A float from 0 to 10
- "reasoning": A text explaining the grade, specifically referencing their project context if applicable
- "feedback": A constructive suggestion for the student
- "confidence_score": A float from 0.0 to 1.0 indicating how confident you are in this grade
- "matched_concepts": An array of strings listing the key concepts from the fact that the student correctly addressed
- "improvement_hints": An array of strings with specific, actionable suggestions for improvement
"""
        last_exc: Exception | None = None
        model = "claude-3-5-sonnet-20241022"
        for attempt in range(_MAX_GRADE_RETRIES):
            try:
                response = await self.client.messages.create(
                    model=model,
                    max_tokens=1024,
                    system="Always output raw, valid JSON. No markdown blocks.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                try:
                    result = json.loads(response.content[0].text)
                    result.setdefault("confidence_score", 0.8)
                    result.setdefault("matched_concepts", [])
                    result.setdefault("improvement_hints", [])
                    result["model_used"] = model
                    return result
                except (ValueError, KeyError):
                    # Malformed JSON — not retryable, fall back immediately
                    return self._fallback_grade(fact, student_response, rubric, project_context)
            except Exception as exc:
                last_exc = exc
                if attempt < _MAX_GRADE_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)  # 1 s, 2 s before attempts 2, 3

        # All retries exhausted
        return self._fallback_grade(fact, student_response, rubric, project_context)
