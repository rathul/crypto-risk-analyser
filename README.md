# Crypto Transaction Risk Analyser

A Streamlit web application for screening Ethereum wallet transactions for potential risk indicators. It combines rule-based scoring, Benford's Law analysis, transaction visualisations, and AI-generated findings to support exploratory blockchain analysis.

> **Disclaimer:** This is an educational screening tool only. It does not prove criminal activity and is not a substitute for professional blockchain forensics.

## What it does

The app retrieves Ethereum mainnet transaction history using the Etherscan API and:

- Calculates an overall risk score (20-100) from four signals: transaction velocity, volume anomalies, recipient address concentration, and transaction patterns.
- Displays a risk level (Low / Medium / High).
- Performs Benford's Law analysis, comparing the leading digits of transaction amounts with the expected distribution.
- Visualises a transaction timeline showing amounts over time.
- Generates AI-assisted key findings using the Groq API.
- Displays a clean transaction table with timestamps, addresses, ETH amounts, and transaction status.
- Offers a downloadable text report containing the score breakdown and findings.

## How scoring works

The overall score combines four equally weighted signals. Each signal is classified as Low (5 points), Medium (15 points), or High (25 points).

| Signal | What it checks | Medium (15 pts) | High (25 pts) |
|---|---|---|---|
| Velocity Risk | Average time gap between transactions | Under 600 seconds | Under 60 seconds |
| Volume Anomaly | Largest non-zero amount divided by the average non-zero amount | Ratio above 3 | Ratio above 10 |
| Address Concentration | Share of transactions sent to the most frequent recipient | Above 25% | Above 50% |
| Pattern Risk | Failed transactions and repeated identical amounts | Any failed transaction, or one amount repeated in over 15% of transactions | More than 3 failed transactions, or one amount repeated in over 30% of transactions |

Anything below the Medium threshold scores Low (5 points).

**Overall score = sum of the four component scores.**

| Score | Risk level |
|---|---|
| Below 34 | Low |
| 34-66 | Medium |
| 67-100 | High |

The thresholds are defined in `backend.py`. They were chosen by judgment, not fitted to labelled data (see Limitations). The AI-generated findings are separate from the numerical score and do not contribute to it. The scores are rule-based indicators, not probabilities of fraud.

## Why Benford's Law?

Benford's Law is a standard forensic accounting test. In naturally occurring financial data, the leading digit 1 appears about 30% of the time and 9 only about 5%. Fabricated or manipulated amounts often break this pattern, so large deviations from the expected distribution can flag unnatural transaction amounts.

## Data sources

- **Etherscan API v2** retrieves Ethereum mainnet transaction history.
- **Groq API** generates natural-language findings from a summary of the 20 most recent transactions.

Both services require API keys, set through the environment variables `ETHERSCAN_API_KEY` and `GROQ_API_KEY`.

## How to run

### Prerequisites

- Python 3.10 or later recommended
- pip
- Etherscan and Groq API keys

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/rathul/crypto-risk-analyser.git
cd crypto-risk-analyser

# 2. Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
ETHERSCAN_API_KEY=your_etherscan_api_key
GROQ_API_KEY=your_groq_api_key
```

Launch the app:

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal, enter an Ethereum wallet address, and select **Analyze Wallet**.

## File structure

```
.
├── app.py             # Streamlit interface and visualisations
├── backend.py         # Data retrieval, analysis, scoring and reports
├── requirements.txt   # Python dependencies
├── .gitignore         # Excludes environment secrets
└── README.md          # Project documentation
```

## Code walkthrough

| Component | What it does |
|---|---|
| `app.py` | Handles wallet input, analysis execution, risk display, charts, transaction table, and report download. |
| `get_transactions()` | Retrieves Ethereum transactions from Etherscan API v2. |
| `clean_transactions()` | Converts raw transaction records into a consistent, readable format. |
| `calculate_risk_breakdown()` | Calculates the four risk signals and the overall score. |
| `benford_analysis()` | Compares observed leading-digit frequencies with Benford's Law. |
| `timeline_data()` | Prepares chronologically ordered transactions for the timeline chart. |
| `analyze_risk()` | Uses the Groq API to generate AI-assisted findings. |
| `generate_report()` | Creates the downloadable text report. |

## Limitations

- **Heuristic thresholds.** The scoring cut-offs were chosen by judgment and have not been validated against labelled fraud data, so scores can produce false positives and false negatives.
- **ETH transfers only.** The Etherscan query covers normal transactions, not ERC-20 token transfers. A wallet that mostly moves tokens can look quiet or show many 0 ETH transactions.
- **Zero-value transactions affect Pattern Risk.** Repeated 0 ETH contract calls (such as token approvals) count as repeated identical amounts and can raise the pattern score for active DeFi wallets.
- **Velocity is averaged over the full history.** For long-lived wallets, the average gap can hide short bursts of rapid activity.
- **AI findings cover recent activity only.** The AI summary sees only the 20 most recent transactions, not the full history, and its output may be inaccurate. Verify it independently.
- **Benford's Law needs enough data.** Results can be misleading for small datasets or amounts that do not naturally span several orders of magnitude.
- **Data dependence.** Results depend on API availability, the data returned, and valid credentials.
- **Scope.** The app analyses Ethereum mainnet only and does not verify wallet ownership or criminal activity.
