# Spreadsheet Documentation

## Overview
[Add your general description of the spreadsheet's purpose and importance here]

## Sheet Structure
[Describe how your spreadsheet is organized, including different sheets/tabs if applicable]

## Data Format
[Explain the format of your data, important columns, and any specific conventions]

## Special Considerations
[Add any special rules, calculations, or important context the AI should know]

## Usage Guidelines
[Add any specific instructions about how the data should be interpreted or used]

# Guide for Cursor – Financial Model **Sums Logic**

> **Purpose** – Give Cursor (and any developer/analyst) the minimal mental model it needs to understand **where every total comes from** in the Google Sheets financial model.

---

## 1. Row Hierarchy

```text
┌─ Revenue (macro)
│   └─ … individual revenue lines (not shown in screenshot)
├─ Cost of Goods Sold (COGS) (macro)
│   ├─ Software           ⤵︎
│   ├─ Technology         ⤵︎  ← repeated functional stack
│   ├─ Product            ⤵︎
│   ├─ HR                 ⤵︎
│   ├─ Marketing / Community
│   ├─ Strategy
│   ├─ Finance
│   ├─ Sales
│   ├─ Operations
│   └─ Legal              ⤴︎  (end of functional stack)
├─ Employee Compensation (macro)
│   └─ same functional stack
├─ Expenses (OPEX) (macro)
│   └─ same functional stack + Bank Fees & Taxes
├─ Ad‑hoc COGS (macro)
│   └─ same functional stack
├─ Travel & External Events (macro)
│   └─ same functional stack
├─ Branding, Offsite, Workshop Design Service, Hardware … (each a **macro block**)
│   └─ same functional stack
└─ KPI & Summary rows (Net Income, Cashburn, Runway, …)
```

**Key point:** Every **macro block** is nothing more than a *wrapper* that **sums** the **exact same ordered functional stack** that lives immediately below it.

---

## 2. Functional Stack (the 9 areas that repeat)

1. Technology
2. Product
3. HR
4. Marketing / Community
5. Strategy
6. Finance
7. Sales
8. Operations
9. Legal

This order **never changes**. When you see `Technology` under COGS, it lines up row‑to‑row with `Technology` under Expenses, Employee Comp, etc., enabling quick vertical scanning and simple range formulas.

---

## 3. Formula Conventions

### 3.1. Monthly totals (inside each macro row)

```gsheets
# Example: Total COGS for Technology in Dec‑24 (row 12 in the model)
=SUM(Detailed_COGS_Technology!D5:D20)  # could also be direct cell range e.g. =SUM(D14:D22)
```

*We recommend naming ranges (`Detailed_COGS_Technology_Dec24`) for readability, but a fixed row range works because the template never shifts.*

### 3.2. Macro block total

```gsheets
# Example: Macro "Cost of Goods Sold" in Dec‑24 (row 6)
=SUM(D7:D15)   # sums the nine functional lines below
```

Exactly the same pattern is used for **Expenses**, **Ad‑hoc COGS**, etc. – just adjust the row numbers.

### 3.3. Year‑to‑Date (YTD) column

YTD = `SUM($Dec24:$Apr25)` for each row, automatically extending when new months are inserted.

---

## 4. Adding a New Month

1. **Insert a new column** at the end of the monthly timeline.
2. **Copy formulas** from the previous month's column—every macro block & KPI formula uses relative references, so they adjust automatically.

---

## 5. Adding a New Functional Area (rare)

* Insert the new area **in the same position** across **every stack** (COGS, Expenses, Employee Comp …).
* Update each macro `SUM()` range to include the new row index.
* Update KPI formulas if they rely on hard‑coded row numbers.

> **Tip:** Keep a single source of row indices (a hidden "Config" sheet) if dynamic references are needed.

---

## 6. KPI Relationships (high‑level)

| KPI              | Core formula linkage                                          |
| ---------------- | ------------------------------------------------------------- |
| **Net Income**   | `Revenue – (COGS + Employee Comp + Expenses + Ad‑hoc blocks)` |
| **Cashburn**     | `–(Net Income – Non‑cash adjustments)`                        |
| **Naked Runway** | `Current Cash ÷ Cashburn`                                     |
| **Total Runway** | `Current Cash + Future Interest ÷ Recurring Burn`             |

---

## 7. Sanity Checks

* Each macro total should equal the **SUM** of the nine functional rows below.
* Grand totals (e.g., Net Income) should flip sign as expected when revenue < total costs.
* Cross‑block comparison is easy: Technology's share of COGS vs Expenses = just read across the same row.

---

## 8. TL;DR for Cursor

1. **Recognise macro blocks** – bolded rows with grey fill.
2. **Sum the next nine rows** (Technology → Legal) to get the macro total.
3. **Repeat** for every block; logic is identical.
4. KPI rows use those macro totals; follow comments in the sheet if deeper tracing needed.

Happy parsing! 🎯 