"""Skills loader and manager"""

import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Skill:
    """Represents a single skill"""

    name: str
    description: str
    prompt: str
    category: str = "general"
    tools: Optional[List[str]] = None
    examples: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
            "category": self.category,
            "tools": self.tools,
            "examples": self.examples,
        }


class SkillLoader:
    """Loads and manages skills from YAML files"""

    def __init__(self, skills_dir: str = None):
        """Initialize skill loader

        Args:
            skills_dir: Directory containing skill files (default: built-in skills)
        """
        if skills_dir is None:
            skills_dir = os.path.join(os.path.dirname(__file__), "builtin")

        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}

        # Load skills on initialization
        self._load_all_skills()

    def _load_all_skills(self):
        """Load all skills from the skills directory"""
        if not os.path.exists(self.skills_dir):
            return

        for filename in os.listdir(self.skills_dir):
            if filename.endswith((".yml", ".yaml")):
                filepath = os.path.join(self.skills_dir, filename)
                self._load_skill_file(filepath)

    def _load_skill_file(self, filepath: str):
        """Load skills from a YAML file

        Args:
            filepath: Path to the YAML file
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "skills" not in data:
                return

            for skill_data in data["skills"]:
                skill = Skill(
                    name=skill_data.get("name", ""),
                    description=skill_data.get("description", ""),
                    prompt=skill_data.get("prompt", ""),
                    category=skill_data.get("category", "general"),
                    tools=skill_data.get("tools"),
                    examples=skill_data.get("examples"),
                )

                if skill.name:
                    self.skills[skill.name] = skill

        except Exception as e:
            print(f"Warning: Failed to load skills from {filepath}: {e}")

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name

        Args:
            name: Skill name

        Returns:
            Skill instance or None
        """
        return self.skills.get(name)

    def list_skills(self, category: str = None) -> List[Skill]:
        """List all available skills

        Args:
            category: Filter by category (optional)

        Returns:
            List of skills
        """
        if category:
            return [s for s in self.skills.values() if s.category == category]
        return list(self.skills.values())

    def get_categories(self) -> List[str]:
        """Get all available categories

        Returns:
            List of category names
        """
        return list(set(s.category for s in self.skills.values()))

    def search_skills(self, query: str) -> List[Skill]:
        """Search skills by name or description

        Args:
            query: Search query

        Returns:
            List of matching skills
        """
        query_lower = query.lower()
        return [
            s for s in self.skills.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]
