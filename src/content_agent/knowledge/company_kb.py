"""Company knowledge base and brand facts loader."""

import os
from typing import Any
import yaml


class CompanyKnowledgeBase:
    """Loads approved brand facts, guidelines, and terminology from configuration files."""

    def __init__(self, brand_config_path: str = "configs/brands/sirius_tech.yaml"):
        self.brand_config_path = brand_config_path
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if os.path.exists(self.brand_config_path):
            try:
                with open(self.brand_config_path, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                    return content if isinstance(content, dict) else {}
            except Exception:
                pass
        return {
            "company_name": "Sirius Tech",
            "tagline": "Evidence-Backed Enterprise AI & Autonomous Systems",
            "voice": "Authoritative, technical, empirical, and transparent",
        }

    def get_brand_voice(self) -> str:
        return self._data.get("voice", "Authoritative, objective, and empirical")
