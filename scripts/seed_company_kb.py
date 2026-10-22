"""Seed initial company knowledge and facts."""

import os
import yaml


def seed_company_kb():
    os.makedirs("configs/brands", exist_ok=True)
    brand_file = "configs/brands/sirius_tech.yaml"

    data = {
        "company_name": "Sirius Tech",
        "tagline": "Evidence-Backed Enterprise AI & Autonomous Systems",
        "mission": "Deliver verifiable, mission-critical AI agent workflows with deterministic quality assurance.",
        "voice": "Authoritative, objective, empirical, and transparent",
        "approved_facts": [
            "Sirius Tech develops autonomous agent architectures for mission-critical operations.",
            "All factual statements must link to verifiable primary documentation.",
            "Deterministic quality gates enforce continuous compliance before publication.",
        ],
    }

    with open(brand_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)

    print(f"[OK] Successfully seeded company knowledge base at {brand_file}")


if __name__ == "__main__":
    seed_company_kb()
