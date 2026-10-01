import json
from typing import Dict, Any, List
from providers.llm_provider import LLMProvider

class OutputGenerator:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        
    def generate(self, output_type: str, semantic_model: Dict[str, Any], facts: List[Dict[str, Any]], config: Dict[str, Any], custom_instruction: str = "") -> str:
        base_prompt = f"""
        You are an expert AI communication architect for the National Technical Research Organisation (NTRO).
        Transform the verified Canonical Facts and Semantic Model into an official '{output_type}' communication artefact.
        
        Operator Configuration:
        - Target Audience: {config.get('audience', 'Executive')}
        - Tone: {config.get('tone', 'Professional')}
        - Target Language: {config.get('language', 'English')}
        - Detail Level: {config.get('detail_level', 'Medium')}
        - Communication Objective: {config.get('objective', 'Inform')}
        {f"- Special Instruction: {custom_instruction}" if custom_instruction else ""}
        
        Semantic Model:
        {json.dumps(semantic_model, indent=2)}
        
        Canonical Facts (SINGLE SOURCE OF TRUTH):
        {json.dumps(facts, indent=2)}
        
        CRITICAL RULES:
        1. STRICT FACTUAL GROUNDING: Use ONLY the provided Canonical Facts.
        2. Never hallucinate numbers, dates, locations, organizations, or casualty figures.
        3. Maintain high analytical rigor, clarity, and authority.
        """
        
        if output_type == "infographic":
            schema = {
                "type": "object",
                "properties": {
                    "headline": {"type": "string"},
                    "subheadline": {"type": "string"},
                    "key_statistic": {"type": "string"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "value": {"type": "string"},
                                "explanation": {"type": "string"}
                            },
                            "required": ["title", "value", "explanation"]
                        }
                    },
                    "key_takeaway": {"type": "string"},
                    "aspect_ratio": {"type": "string"}
                },
                "required": ["headline", "sections", "key_takeaway"]
            }
            res = self.provider.structured_generate(base_prompt + "\nGenerate structured JSON for an Infographic.", schema)
            return json.dumps(res, indent=2)
            
        elif output_type == "presentation":
            schema = {
                "type": "object",
                "properties": {
                    "slides": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "slide_number": {"type": "integer"},
                                "title": {"type": "string"},
                                "subtitle": {"type": "string"},
                                "content": {"type": "array", "items": {"type": "string"}},
                                "visual_recommendation": {"type": "string"},
                                "speaker_notes": {"type": "string"}
                            },
                            "required": ["slide_number", "title", "content"]
                        }
                    }
                },
                "required": ["slides"]
            }
            res = self.provider.structured_generate(base_prompt + "\nGenerate a complete presentation slide deck as structured JSON.", schema)
            return json.dumps(res, indent=2)
            
        elif output_type == "video":
            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "duration_seconds": {"type": "integer"},
                    "scenes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "scene_number": {"type": "integer"},
                                "duration": {"type": "string"},
                                "visual_description": {"type": "string"},
                                "camera_direction": {"type": "string"},
                                "narration": {"type": "string"},
                                "on_screen_text": {"type": "string"},
                                "transition": {"type": "string"}
                            },
                            "required": ["scene_number", "duration", "visual_description", "narration"]
                        }
                    },
                    "subtitles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                                "text": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["title", "scenes"]
            }
            res = self.provider.structured_generate(base_prompt + "\nGenerate a comprehensive Video Package & Storyboard as structured JSON.", schema)
            return json.dumps(res, indent=2)
            
        elif output_type == "linkedin":
            prompt = base_prompt + "\nFormat as a LinkedIn post with a strong hook, clear paragraphs, key takeaways, and strategic hashtags."
            return self.provider.generate(prompt)
            
        elif output_type == "x":
            prompt = base_prompt + "\nFormat as an official X/Twitter thread (e.g. 1/n, 2/n, 3/n). Keep each tweet under 280 characters with relevant tags."
            return self.provider.generate(prompt)
            
        elif output_type == "advisory":
            prompt = base_prompt + "\nFormat as a formal Strategic Incident Advisory in Markdown with Executive Summary, Situation, Key Facts, Threat Assessment, and Recommended Actions."
            return self.provider.generate(prompt)
            
        elif output_type == "summary":
            prompt = base_prompt + "\nFormat as a concise Executive Briefing with Title, Context, Findings, Key Metrics, and Strategic Implications."
            return self.provider.generate(prompt)
            
        return self.provider.generate(base_prompt + f"\nGenerate content for {output_type}.")
