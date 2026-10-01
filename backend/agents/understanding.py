import json
from typing import Dict, Any
from providers.llm_provider import LLMProvider

class UnderstandingAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        
    def analyze(self, content: str) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "core_message": {"type": "string"},
                "entities": {"type": "array", "items": {"type": "string"}},
                "events": {"type": "array", "items": {"type": "string"}},
                "timeline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "time": {"type": "string"},
                            "event": {"type": "string"}
                        }
                    }
                },
                "risks": {"type": "array", "items": {"type": "string"}},
                "recommended_actions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["topic", "core_message", "entities", "events"]
        }
        prompt = f"""
        Perform a comprehensive intelligence and operational analysis of the following source text.
        Extract the central topic, core message, key named entities (organizations, locations, systems), 
        event chronology / timeline, operational risks, and recommended actions.
        
        Source Text:
        \"\"\"{content}\"\"\"
        """
        return self.provider.structured_generate(prompt, schema)
