import os
import pytest
from unittest.mock import MagicMock, patch
from app.agent import run
from tools.google_sheets import SheetsQueryReturn

# Mock data for April expenses
MOCK_APRIL_EXPENSES = [
    {"date": "2024-04-01", "amount": 150.50, "category": "Groceries"},
    {"date": "2024-04-05", "amount": 75.25, "category": "Transportation"},
    {"date": "2024-04-10", "amount": 200.00, "category": "Utilities"}
]

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "fake-api-key")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_INFO", "{}")

@pytest.fixture
def mock_openai_client():
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
def mock_sheets_query(monkeypatch):
    """Mock Google Sheets query function."""
    def mock_query(params):
        if "SELECT SUM(amount) FROM" in params.sql_query:
            return SheetsQueryReturn(
                data=[{"SUM(amount)": 425.75}],
                columns=["SUM(amount)"]
            )
        return SheetsQueryReturn(data=[], columns=[])
    
    monkeypatch.setattr("app.agent.google_sheets_query", mock_query)

def test_total_april_expenses(mock_env_vars, mock_openai_client, mock_sheets_query):
    """Test that the agent can calculate total April expenses."""
    response = run("What were our total expenses in April 2024?")
    
    # Verify the response contains a positive number
    assert any(char.isdigit() for char in response)
    # Extract the number from the response (assuming it's formatted with $ and commas)
    import re
    numbers = re.findall(r'\$[\d,]+\.?\d*', response)
    assert len(numbers) > 0
    # Convert the first found number to float
    amount = float(numbers[0].replace('$', '').replace(',', ''))
    assert amount > 0

def test_out_of_scope(mock_env_vars, mock_openai_client):
    """Test that the agent refuses to answer out-of-scope questions."""
    response = run("What's the weather like today?")
    
    # Verify the response contains an apology and refusal
    assert any(word in response.lower() for word in ["sorry", "apologize", "cannot", "unable"])
    assert any(word in response.lower() for word in ["finance", "financial", "expenses", "budget"])

def test_total_revenue(mock_env_vars, mock_openai_client, mock_sheets_query):
    """Test that the agent can answer total revenue question."""
    response = run("Total revenue?")
    
    # Verify response is a string and not empty
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    
    # Verify the response contains a number
    assert any(char.isdigit() for char in response)
    
    # Extract the number from the response (assuming it's formatted with $ and commas)
    import re
    numbers = re.findall(r'\$[\d,]+\.?\d*', response)
    assert len(numbers) > 0
    # Convert the first found number to float
    amount = float(numbers[0].replace('$', '').replace(',', ''))
    assert amount > 0

def test_total_revenue_with_fake_agent(fake_agent):
    """Test that the agent returns a non-empty response with at least one digit for total revenue query."""
    response = fake_agent("Total revenue?")
    
    # Verify response is a string and not empty
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    
    # Verify the response contains at least one digit
    assert any(char.isdigit() for char in response) 