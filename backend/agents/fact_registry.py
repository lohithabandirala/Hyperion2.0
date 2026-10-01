import json
from typing import List, Dict, Any
from providers.llm_provider import LLMProvider

class FactRegistryAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        
    def extract_facts(self, content: str) -> List[Dict[str, Any]]:
        schema = {
            "type": "object",
            "properties": {
                "facts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "fact_id": {"type": "string"},
                            "claim": {"type": "string"},
                            "fact_type": {
                                "type": "string",
                                "enum": ["DATE", "NUMBER", "PERCENTAGE", "ENTITY", "LOCATION", "EVENT", "STATISTIC", "CLAIM"]
                            },
                            "confidence": {"type": "number"},
                            "source_reference": {"type": "string"},
                            "entities": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["fact_id", "claim", "fact_type", "confidence"]
                    }
                }
            },
            "required": ["facts"]
        }
        prompt = f"""
        You are the Canonical Fact Registry Engine for the NTRO Gen AI Platform.
        Extract every atomic factual claim from the source text into a structured fact registry.
        
        Guidelines:
        1. Categorize each fact (DATE, NUMBER, PERCENTAGE, ENTITY, LOCATION, EVENT, STATISTIC, CLAIM).
        2. Assign a deterministic ID (F001, F002, etc.).
        3. Identify exact source references (e.g. "Section 1, Paragraph 2").
        4. List all specific entity names associated with the claim.
        5. Provide a confidence score (0.0 to 1.0).
        
        Source Text:
        \"\"\"{content}\"\"\"
        """
        result = self.provider.structured_generate(prompt, schema)
        facts = result.get("facts", [])
        
        # Ensure sequential IDs if missing
        for idx, f in enumerate(facts):
            if not f.get("fact_id"):
                f["fact_id"] = f"F{idx+1:03d}"
        return facts
