"""Pydantic models for the finance agent."""

from typing import List
from pydantic import BaseModel, Field


class FinancialRecord(BaseModel):
    """Model representing a financial transaction record."""
    date: str = Field(..., description="Date of the transaction")
    category: str = Field(..., description="Category of the transaction")
    amount: float = Field(..., description="Amount of the transaction")


class AgentResponse(BaseModel):
    """Model representing an agent's response."""
    text: str = Field(..., description="Text response from the agent")
    data: List = Field(default_factory=list, description="Additional data from the agent") 