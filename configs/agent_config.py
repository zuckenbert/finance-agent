"""Configuration constants for the finance agent.

This module contains configuration settings used throughout the finance agent application.

Constants:
    DEFAULT_MODEL (str): The default OpenAI model to use for agent operations.
        Currently set to "gpt-4-turbo-preview" which is OpenAI's latest GPT-4 model
        optimized for real-time performance.

    MAX_ROWS (int): The maximum number of rows to process in a single operation.
        This limit helps prevent memory issues and ensures reasonable processing times
        when working with large datasets.
"""

DEFAULT_MODEL = "gpt-4-turbo-preview"
MAX_ROWS = 500 