"""Test configuration and fixtures."""

import pytest
from unittest.mock import MagicMock, patch
from tools.google_sheets import SheetsQueryReturn, SheetsQueryParams

@pytest.fixture
def mock_openai(monkeypatch):
    """Mock OpenAI client and its responses."""
    with patch("app.agent.client") as mock_client:
        # Mock agent creation
        mock_agent = MagicMock()
        mock_agent.id = "fake-agent-id"
        mock_client.beta.agents.create.return_value = mock_agent

        # Mock thread creation
        mock_thread = MagicMock()
        mock_thread.id = "fake-thread-id"
        mock_client.beta.threads.create.return_value = mock_thread

        # Mock run creation and status
        mock_run = MagicMock()
        mock_run.id = "fake-run-id"
        mock_client.beta.threads.runs.create.return_value = mock_run
        
        # Mock run status
        mock_run_status = MagicMock()
        mock_run_status.status = "completed"
        mock_client.beta.threads.runs.retrieve.return_value = mock_run_status

        # Mock message response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=MagicMock(value="Test response"))]
        mock_client.beta.threads.messages.list.return_value = MagicMock(data=[mock_message])

        yield mock_client

@pytest.fixture
def fake_sheets_query(monkeypatch):
    """Mock Google Sheets query function with dummy data."""
    def mock_query(params: SheetsQueryParams) -> SheetsQueryReturn:
        # Mock data for different query types
        if "SELECT SUM(amount) FROM" in params.sql_query:
            return SheetsQueryReturn(
                data=[{"SUM(amount)": 425.75}],
                columns=["SUM(amount)"]
            )
        elif "SELECT * FROM" in params.sql_query:
            return SheetsQueryReturn(
                data=[
                    {"date": "2024-04-01", "amount": 150.50, "category": "Groceries"},
                    {"date": "2024-04-05", "amount": 75.25, "category": "Transportation"},
                    {"date": "2024-04-10", "amount": 200.00, "category": "Utilities"}
                ],
                columns=["date", "amount", "category"]
            )
        return SheetsQueryReturn(data=[], columns=[])
    
    monkeypatch.setattr("tools.google_sheets.google_sheets_query", mock_query)
    return mock_query

@pytest.fixture
def fake_agent(monkeypatch, fake_sheets_query):
    """Create a fake agent that uses the mocked sheets query."""
    def mock_run(question: str) -> str:
        # Use the mocked sheets query to simulate agent behavior
        if "total" in question.lower() and "expenses" in question.lower():
            result = fake_sheets_query(SheetsQueryParams(
                spreadsheet_id="test-sheet",
                sql_query="SELECT SUM(amount) FROM transactions"
            ))
            return f"Total expenses: ${result.data[0]['SUM(amount)']:,.2f}"
        return "I don't have enough information to answer that question."
    
    monkeypatch.setattr("app.agent.run", mock_run)
    return mock_run

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "fake-api-key")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}") 