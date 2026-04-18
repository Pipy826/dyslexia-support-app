# games/__init__.py
from .visual_game import VISUAL_QUESTIONS
from .spelling_game import SPELLING_QUESTIONS
from .comprehension_game import COMPREHENSION_QUESTIONS
from .working_memory_game import WORKING_MEMORY_QUESTIONS
from .rapid_naming_game import RAPID_NAMING_QUESTIONS
from .motor_coordination_game import MOTOR_COORDINATION_QUESTIONS

__all__ = [
    "VISUAL_QUESTIONS",
    "SPELLING_QUESTIONS",
    "COMPREHENSION_QUESTIONS",
    "WORKING_MEMORY_QUESTIONS",
    "RAPID_NAMING_QUESTIONS",
    "MOTOR_COORDINATION_QUESTIONS",
]
