# 📊 Financial Engine

> **Originally Developed by** : [Raj Adhikari](https://github.com/r-adhikari97)

A **time-machine for market data** — replay and analyze historical financial data for one or more companies across single or multiple dates.

Built to **backtest strategies**, **calculate financial ratios**, and **accelerate data analysis** using a smart caching mechanism.

---

## 📦 Changelog

See full [CHANGELOG.md](https://github.com/r-adhikari97/financial-engine/blob/main/CHANGELOG.md)

---

## ✨ Features

- 📈 Calculate financial ratios on-demand
- 🔁 Perform rolling computations for line items
- ⚡ Caching mechanism for fast range-date processing

---

## 🚀 Installation

```bash
pip install financial-engine
```

### Step-by-step

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
2. Create a `.env` file in the root of your project:

   ```dotenv
   MONGO_URI=
   MONGO_DATABASE=
   MONGO_COLLECTION=
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   BUCKET_NAME=
   ```
3. Install the package:

   ```bash
   pip install financial-engine
   ```

---

## 🐍 Requirements

- Python ≥ 3.10
- Compatible with major OS environments (Linux, Windows, Mac)

---

## 🛠 Implemented Methods

| Method                          | Description                                                       |
| ------------------------------- | ----------------------------------------------------------------- |
| `get_ratios()`                | Get financial ratios for a single company on a specific date      |
| `get_ratios_range()`          | Fetch financial ratios for a company across a date range          |
| `get_ratios_range_multiple()` | Fetch financial ratios for multiple comapnies across a date range |

---

## 📦 Usage Example

```python
from financial_engine.core.engine import FinancialEngine

fe = FinancialEngine()

ratios_df = await fe.get_ratios_range(
    alpha_code="RELIANCE",
    start_date="2023-01-01",
    end_date="2023-01-15"
)
print(ratios_df)
```

---
