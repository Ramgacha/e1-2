import json
import sys 
import os

class Quiz:
    def __init__(self, question: str, choices: list, answer: int):
        self.question = question
        self.choices = choices
        self.answer = answer

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"]
        )
    