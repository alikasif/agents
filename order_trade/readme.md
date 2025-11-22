# Autonomous Trading Platform — Agentic Architecture

## 🚀 Overview

This project implements a **sandboxed autonomous trading platform** built from modular, collaborative AI agents. Each agent has a specialized role in the end-to-end investment lifecycle — from market research to trade execution — with internal checks, multi-agent consensus, and supervisory oversight.

The design focuses on **research transparency**, **risk control**, and **agent accountability**, ensuring every trade is explainable, simulated, and auditable before live execution.

---

## 🧩 System Architecture

The platform is composed of **4 primary agent layers** and **1 supervisory layer**:

### 1. Research Agents (Trio)

* **Goal:** Identify high-potential sectors for investment.
* **Agents:** `research-1`, `research-2`, `research-3`.
* **Process:**

  * Each agent independently analyzes global/local news, macro trends, policies, and institutional flows.
  * They discuss and challenge each other’s findings through structured debate messages.
  * The trio produces a **consensus sector list** (2–3 sectors) with confidence scores and source provenance.

### 2. Financial Analyst Agents (Trio)

* **Goal:** Identify investable companies within approved sectors.
* **Agents:** `financial-1`, `financial-2`, `financial-3`.
* **Process:**

  * Each agent independently ranks companies based on fundamentals (P&L, debt/equity, ROE) and technical indicators.
  * Agents hold a consensus round to reconcile differences and agree on 4–6 top picks.
  * Produces a **consensus stock list** with aggregated scores, allocation suggestions, and minority opinions.

### 3. Trader Agent

* **Goal:** Create executable **trade plans** from consensus stock lists.
* **Responsibilities:**

  * Define buy/sell side, entry and exit bands, stop-loss, take-profit, and order types.
  * Enforce risk policies (max 1% per trade, 10% per sector exposure).
  * Output structured trade plans, not actual executions.

### 4. Broker Agent

* **Goal:** Simulate **execution of trades** in a sandbox environment.
* **Responsibilities:**

  * Validate trade plans against available cash and risk limits.
  * Apply slippage, fees, and partial fill logic.
  * Update the local **ledger** with immutable transaction records.
  * Produce detailed execution receipts for each order.

### 5. Supervisor Agent

* **Goal:** Enforce governance, safety, and coordination across the pipeline.
* **Responsibilities:**

  * Validate research and analyst consensus outputs.
  * Approve or reject sectors, stocks, and trade plans.
  * Apply tie-breaker logic and flag human review for low-confidence or conflicting cases.
  * Maintain system integrity and compliance boundaries.

---

## 💰 Sandbox Trading Model

The platform operates in a **sandbox environment** with simulated capital and deterministic market data.

* **Starting capital:** ₹10,000,000
* **Per-trade limit:** 1% of portfolio
* **Sector cap:** 10% of portfolio
* **Transaction fee:** 0.05% + ₹10 per trade
* **Slippage model:** `fill_price = quoted_price ± (impact_coeff * order_size / avg_daily_volume)`

Ledger records are **append-only** and include all transactions, positions, and cash snapshots.

---

## 📁 Repository Structure

```
├── prompts.py           # All system/user prompts for every agent
├── README.md            # Project overview and documentation
├── /agents              # Future directory for agent definitions and orchestration scripts
├── /data                # Market, news, and fundamental data feeds
├── /sandbox             # Local ledger and trade execution simulation
└── /tests               # Unit and integration tests
```

---

## 🧠 Prompts Design Philosophy

All prompts are:

* **Declarative** — every agent knows exactly what data structure to return.
* **Auditable** — all claims require sources and timestamps.
* **Collaborative** — agents reach consensus through structured discussions.
* **Composable** — Supervisor orchestrates transitions between stages.

You can find all prompt templates in [`prompts.py`](./prompts.py), including helper factories for the multi-agent setups:

```python
get_research_prompts(agent_id)
get_financial_prompts(agent_id, sector)
```

---

## 🧮 Data Model — Ledger Structure

The broker agent maintains a local ledger containing three main entities:

* **transactions** — append-only list of all order and fill events.
* **positions** — real-time holdings by symbol.
* **cash_snapshots** — cash and net liquidation values over time.

Example:

```json
{
  "tx_id": "uuid",
  "symbol": "RELIANCE.NS",
  "side": "BUY",
  "qty": 100,
  "price": 2500.0,
  "fee": 125.0,
  "status": "FILLED"
}
```

---

## ⚖️ Risk Management Highlights

* Hard limits: per-trade 1%, sector 10%.
* Stop-loss and take-profit required per trade.
* Automatic circuit breakers on daily drawdown.
* Supervisor agent enforces compliance and halts unsafe flows.

---

## 🧩 Multi-Agent Discussion Protocol

Agents communicate via structured JSON messages:

```json
{"from": "research-1", "msg_type": "CHALLENGE", "content": "Policy data lacks update", "sources": ["Reuters"]}
```

The consensus process is deterministic and transparent — all votes, confidence scores, and minority objections are recorded.

---

## 🧰 Future Extensions

* Integration with real broker APIs (e.g., Zerodha, Alpaca) after sandbox validation.
* Vector memory for long-term trend awareness.
* Reinforcement layer for trader policy optimization.
* Automated backtesting pipeline with slippage simulation.

---

## 🧾 Legal Disclaimer

This project is for **research and educational purposes only**. It does not constitute financial advice or guarantee profitability. Always comply with local market regulations and consult a licensed financial professional before live deployment.

---

## 📜 License

MIT License — © 2025 Autonomous Trading Research Team
