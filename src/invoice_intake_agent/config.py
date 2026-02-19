"""Configuration for the invoice intake agent."""

import os
from dotenv import load_dotenv
from enum import Enum


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")


class Model(str, Enum):
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"

    def __str__(self) -> str:
        return self.value


MODEL = Model.GPT_5_MINI
