#!/usr/bin/env python
"""Generates and manages profiles."""

class ProfileGenerator:
    def __init__(self, profiles: list = None, questions: list = None):
        self.profiles = list(profiles) if profiles is not None else []
        self.questions = list(questions) if questions is not None else []

    def add_question(self, question: str) -> None:
        """Add a question to the list of questions."""
        self.questions.append(str(question))

    def add_profile(self, profile: dict) -> None:
        """Add a profile to the list of profiles."""
        self.profiles.append(profile)

    def _dict_to_string(self, _dict: dict) -> str:
        """Convert a dictionary to a formatted string."""
        string = ""

        # For each entry in dict, generate string as key: value
        for key in _dict:
            string += str(key) + ": " + str(_dict[key]) + "\n"
        string += "\n"

        return string

    def generate_prompts(self) -> list:
        """Generate prompts by combining profiles and questions."""
        prompts = []

        # For each profile and questions, generate a prompt
        for profile in self.profiles:
            string = self._dict_to_string(profile)
            for question in self.questions:
                prompts.append(string + question)

        return prompts
