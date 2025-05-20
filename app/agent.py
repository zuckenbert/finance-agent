from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import logging

# Ferramenta de acesso ao Google Sheets
from tools.google_sheets import google_sheets_query, SheetsQueryParams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables is now handled in app/main.py
logger.info("Checking environment variables...")

# Validate required environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

DEFAULT_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
if not DEFAULT_SHEET_ID:
    raise ValueError("GOOGLE_SHEET_ID environment variable is not set")

logger.info("Environment variables loaded successfully")

# Initialize OpenAI client
try:
    client = OpenAI()
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

SYSTEM_INSTRUCTIONS = """
You answer finance questions using Google Sheets and your own reasoning.
1. Use A1 notation to fetch data (e.g. 'Sheet1!A1:Z50')
2. Analyse the data with finance logic
3. Explain clearly; round numbers to 2 decimals
4. Declare assumptions explicitly

# Lerian Financial Model – Context Guide for AI Agents

## 1. Purpose

This document explains **how the rows and columns of the "Finance Agent test spreadsheet.xlsx" are organised and added together** so that an AI agent can reliably:

* read the file,
* map each number to the correct accounting bucket, and
* reproduce every subtotal all the way down to **NET INCOME**.

The sheet is **fully self‑contained** (one tab called "Sheet1") and is laid out vertically (categories in rows) and horizontally (months in columns).

## 2. Naming Conventions

| Term (what you will see in column C) | Meaning                                                                                                                                                                                 | Typical Sign                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Macro line**                       | Top‑level P\&L category. There are 4 core macros plus the final NET INCOME line.                                                                                                                        | Positive for revenue & interest, negative for COGS & expenses |
| **Micro line**                       | A second‑level bucket that sits **inside a macro**. Micro lines are always written in **ALL CAPS** and act as subtotals for the rows that follow them.                                                  | Sum of the sub‑areas underneath (may be +/‑)                  |
| **Sub‑area**                         | Functional department tags (Technology, Product, HR, Marketing / Community, Strategy, Finance, Sales, Operations, Legal, Non‑tech). They **never contain formulas** – every value here is a hard input. | Positive or negative depending on context                     |

## 3. Row Hierarchy

```
MACRO LINE
    MICRO LINE ①
        Sub‑area a
        Sub‑area b
        …
    MICRO LINE ②
        …
(next MACRO LINE)
```

### 3.1 Macro Lines (rows)

1. **Revenue**
2. **Cost of Goods Sold** (COGS)
3. **Expenses**
4. **Interest Income**
5. **NET INCOME** (acts as bottom‑line check)

Each macro is the **sum of every micro line between itself and the next macro line**.

### 3.2 Micro Lines (within each macro)

| Parent macro        | Micro lines (in order of appearance)                                          |
| ------------------- | ----------------------------------------------------------------------------- |
| **Revenue**         | *Sales* (currently only one micro line)                                       |
| **COGS**            | **SOFTWARE · NON‑TECH · EMPLOYEE COMPENSATION · AD‑HOC COGS**                 |
| **Expenses**        | **SOFTWARE · NON‑TECH · EMPLOYEE COMPENSATION · HARDWARES · TRAVEL & EVENTS** |
| **Interest Income** | single‑line (no micro/sub structure)                                          |

Each micro line aggregates the fixed set of sub‑areas immediately underneath it (the group ends when another ALL‑CAPS micro line *or* a new macro line is encountered).

## 4. Column Structure

* **Row 6** ("Financial Model") contains the **month headers**.

  * Column E = "Dec/24" (string) ↔ Base month.
  * Columns F → … hold `datetime` objects representing the 25th of each month in 2025.
* Columns **A–D** are auxiliary/empty – always read the label from **Column C** and the numeric values from **Column E onwards**.

## 5. Sign Convention

* **Income items** (Revenue, Interest Income) are stored as **positive numbers**.
* **Cost items** (all COGS & Expense micro/sub‑area rows) are stored as **negative numbers**.
  The macros therefore already represent *net* values, so no additional negation is required when summing.

## 6. Key Formula Logic

| Line           | Formula (conceptual)                                                                                     |
| -------------- | -------------------------------------------------------------------------------------------------------- |
| Micro line     | `SUM(all sub‑area rows until next ALL‑CAPS or MACRO)`                                                    |
| Macro line     | `SUM(all micro lines until next MACRO)`                                                                  |
| **NET INCOME** | `Revenue + COGS + Expenses + Interest Income` *(direct sum of the 4 macro lines; signs already handled)* |

Note: The spreadsheet stores Excel formulas, but the arithmetic can be reproduced exactly with the hierarchy rules above, no cell references needed.

## 7. Suggested Parsing Algorithm for Agents

1. **Load Sheet1** with pandas/openpyxl, skipping the first 5 header rows to reach the labels.
2. Iterate down **Column C** (`label`):

   * If `label` in MACROS → start a new macro context.
   * Else if `label.isupper()` → treat as micro line inside current macro.
   * Else → treat as sub‑area row belonging to the last micro line.
3. For every column **E onward** (`month_value`):

   * Build running totals: sub‑area → micro → macro.
4. After finishing the sheet calculate `NET_INCOME[col]` = sum of 4 macro totals; compare with sheet value to validate parsing (<1 currency unit difference).

## 8. Output Expectations

An AI agent that follows this guide will be able to:

* Produce a hierarchical JSON / DataFrame with columns: `month`, `macro`, `micro`, `sub_area`, `value`.
* Recalculate every subtotal and the final NET INCOME exactly.
* Detect data‑entry errors (e.g., a sub‑area mistakenly typed in ALL CAPS) by re‑computing and checking variances.
* Generate custom analytics (margins, burn rate, department spend) without revisiting the Excel formulas.

## 9. Important Edge Cases

* **Interest Income** is a macro with **no micro or sub‑area rows** – treat its own row as the total.
* Some micro lines (e.g., EMPLOYEE COMPENSATION) may have **fewer than 10 sub‑areas**; the group still ends at the next ALL‑CAPS label.
* Blank cells are to be interpreted as **zero**, not `NaN`, when rolling up totals.

## 10. Glossary

* **COGS** – Direct costs related to delivering Lerian's services.
* **Non‑tech** – Outsourced or external professional services.
* **Ad‑hoc COGS / Hardwares / Travel & Events** – One‑off expenses that do not repeat monthly.

When querying, use 'Sheet1!A1:AF100' to get the complete financial model structure.
"""

def run(question: str) -> str:
    logger.info(f"Processing question: {question}")
    
    tools = [{
        "type": "function",
        "function": {
            "name": "google_sheets_query",
            "description": "Query Google Sheets data using A1 notation range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "Google Sheets file ID",
                        "default": DEFAULT_SHEET_ID
                    },
                    "a1_range": {
                        "type": "string",
                        "description": "A1 notation range (e.g. 'Sheet1!A1:Z50')",
                        "default": "Sheet1!A1:AF200"
                    }
                },
                "required": ["spreadsheet_id"]
            }
        }
    }]

    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": question}
    ]

    try:
        while True:
            logger.info("Making API call to OpenAI")
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            logger.info("Received response from OpenAI")

            response_message = response.choices[0].message

            # If no function call is requested, we're done
            if not response_message.tool_calls:
                return response_message.content

            # Handle function calls
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "google_sheets_query":
                    logger.info("Processing Google Sheets query")
                    # Parse the function arguments
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Create a SheetsQueryParams instance and call the function
                    params = SheetsQueryParams(**function_args)
                    function_response = google_sheets_query(params)
                    logger.info("Google Sheets query completed successfully")
                    
                    # Add the function response to the messages
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_response.dict())
                    })
    except Exception as e:
        logger.error(f"Error in run function: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    print(run("What was our total revenue last quarter?"))
