"""
Zero-API Bullet Generator for NextUpCV
Generates dynamic ATS-optimized resume bullet points using domain action templates.
"""

from typing import List
import random


class RuleBasedBulletGenerator:
    """Generates deterministic, high-impact resume bullets without external APIs."""

    # Categorized action verbs and high-impact templates
    TEMPLATES = [
        "Architected and deployed {keyword}-driven modules, improving workflow throughput and operational reliability.",
        "Integrated {keyword} into core data pipelines, reducing processing latency and manual intervention.",
        "Engineered scalable solutions leveraging {keyword} to enhance system performance and maintainability.",
        "Implemented industry best practices for {keyword}, accelerating release velocity across target environments.",
        "Spearheaded technical migration and adoption of {keyword}, resulting in improved service uptime and test coverage.",
        "Optimized backend processes and data handling using {keyword}, boosting overall system efficiency by 25%.",
        "Collaborated with cross-functional teams to integrate {keyword}, streamlining development and debugging cycles.",
    ]

    def generate_tailored_bullets(
        self, missing_keywords: List[str], job_description: str = ""
    ) -> List[str]:
        """Generates dynamic resume bullet points targeting missing ATS keywords."""
        if not missing_keywords:
            return []

        generated_bullets = []
        # Target up to top 4 missing keywords
        target_keywords = missing_keywords[:4]

        for i, kw in enumerate(target_keywords):
            # Select a template deterministically based on index/hash
            template_idx = (hash(kw) + i) % len(self.TEMPLATES)
            bullet = self.TEMPLATES[template_idx].format(keyword=kw)
            generated_bullets.append(bullet)

        return generated_bullets


# Alias so both class names work interchangeably across your code
LLMBulletGenerator = RuleBasedBulletGenerator
