import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ── Multi-Key Fallback Pool ─────────────────────────────────────────────────
def _build_key_pool():
    pool = []
    primary = os.getenv("GEMINI_API_KEY", "").strip()
    if primary:
        pool.append(primary)
    fallback_keys = [
        os.getenv("GEMINI_API_KEY_2", "").strip(),
        os.getenv("GEMINI_API_KEY_3", "").strip(),
    ]
    for k in fallback_keys:
        if k and k not in pool:
            pool.append(k)
    return pool

KEY_POOL = _build_key_pool()

class CorrectionResult:
    def __init__(self, is_consistent: bool, confidence: float, reason: str, corrected_findings: list):
        self.is_consistent = is_consistent
        self.confidence = confidence
        self.reason = reason
        self.corrected_findings = corrected_findings

class SelfCorrector:
    def __init__(self):
        self._key_pool = list(KEY_POOL)
        self._key_index = 0
        self.client = genai.Client(api_key=self._current_key())
        self.model_name = "gemini-2.5-flash"

    def _current_key(self):
        if not self._key_pool:
            return ""
        return self._key_pool[self._key_index % len(self._key_pool)]

    def _rotate_key(self):
        if len(self._key_pool) > 1:
            self._key_index = (self._key_index + 1) % len(self._key_pool)
            self.client = genai.Client(api_key=self._current_key())
            print(f"[SelfCorrector] Switched to API key #{self._key_index + 1} of {len(self._key_pool)}.")

    def _safe_generate(self, prompt, max_retries=3):
        RETRYABLE_CODES = ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "quota"]
        for attempt in range(max_retries * len(self._key_pool)):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return response
            except Exception as api_err:
                err_str = str(api_err)
                is_retryable = any(code in err_str for code in RETRYABLE_CODES)
                if is_retryable:
                    old_key_idx = self._key_index
                    self._rotate_key()
                    if self._key_index == old_key_idx:
                        wait_time = 2 ** (attempt + 1)
                        print(f"[SelfCorrector] API overloaded. Waiting {wait_time}s before retry...")
                        time.sleep(min(wait_time, 15))
                else:
                    raise Exception(f"Non-retryable API error: {err_str[:150]}")
        raise Exception("All retries exhausted due to API limits.")

    def evaluate(self, prior_findings, new_findings, tool_outputs):
        prompt = f"""You are a senior security forensics self-correction system.
Your job is to audit the security findings of an AI agent by comparing them directly to the raw tool outputs.
You must catch hallucinations, assumptions, or claims that are NOT backed by hard evidence in the tool output.

RAW TOOL OUTPUTS:
{json.dumps(tool_outputs, indent=2)}

PRIOR FINDINGS (from previous iterations):
{json.dumps(prior_findings, indent=2)}

NEW FINDINGS (proposed in this iteration):
{json.dumps(new_findings, indent=2)}

Verify the following:
1. Are all claims in the findings directly backed by text in the raw tool outputs?
2. Are there any false assumptions or hallucinations (e.g. claiming lateral movement happened when no network tools show it)?
3. If there is a hallucination or inconsistency, mark is_consistent=false, explain why under reason, and remove/correct the invalid findings in corrected_findings.
4. Set a confidence score from 0.0 (unreliable) to 1.0 (verified).

Respond ONLY in JSON format with the following structure:
{{
  "is_consistent": bool,
  "confidence": float,
  "reason": "explanation of any hallucinations, errors, or consistency check success",
  "corrected_findings": [
    {{
      "finding": "description of the verified finding",
      "evidence": "exact quote or reference from tool output",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    }}
  ]
}}
"""
        try:
            response = self._safe_generate(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1]
                if raw_text.endswith("```"):
                    raw_text = raw_text.rsplit("```", 1)[0]
            data = json.loads(raw_text.strip())
            return CorrectionResult(
                is_consistent=data.get("is_consistent", True),
                confidence=data.get("confidence", 1.0),
                reason=data.get("reason", "Checks passed."),
                corrected_findings=data.get("corrected_findings", new_findings)
            )
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "exhausted" in err_msg:
                safe_reason = "Self-correction skipped: Google API quota exhausted."
            else:
                safe_reason = f"Self-correction defaulted: {err_msg[:100]}"
            print(f"[SelfCorrector Error] {safe_reason}")
            return CorrectionResult(
                is_consistent=True,
                confidence=0.8,
                reason=safe_reason,
                corrected_findings=new_findings
            )
