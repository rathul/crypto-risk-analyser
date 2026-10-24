# Crypto Transaction Risk Analyser

A Streamlit web application for screening Ethereum wallet transactions for potential risk indicators. Combines rule-based analysis, Benford's Law, transaction visualisations, and AI-generated findings to support exploratory blockchain analysis.

---

## What it does

The app retrieves Ethereum mainnet transaction history using the Etherscan API and:

- Calculates an **overall risk score (20–100)** based on four signals: transaction velocity, volume anomalies, recipient address concentration, and transaction patterns.
- Displays a **risk level** (Low / Medium / High).
- Performs **Benford's Law analysis**, comparing observed transaction amount leading digits with the expected distribution.
- Visualises a **transaction timeline** showing transaction amounts over time.
- Generates **AI-assisted key findings** using the Groq API.
- Displays a transaction table with timestamps, addresses, ETH amounts, and transaction status.
- Offers a **downloadable text report** containing the score breakdown and findings.

> **Disclaimer:** This is an educational screening tool only. It does not prove criminal activity and is not a substitute for professional blockchain forensics.

---

## How scoring works

The overall score combines four equally weighted components, each contributing 5, 15, or 25 points.

| **Signal** | **What it checks** |
|---|---|
| Velocity Risk | Average time gap between transactions |
| Volume Anomaly | Largest transaction amount relative to the average |
| Address Concentration | Proportion of transactions sent to the most frequent recipient |
| Pattern Risk | Failed transactions and repeated transaction amounts |

Each signal is classified as Low (5 points), Medium (15 points), or High (25 points), based on thresholds defined in `backend.py`.

**Overall score** = sum of the four component scores.

| **Score** | **Risk level** |
|---|---|
| Below 34 | Low |
| 34–66 | Medium |
| 67–100 | High |

The AI-generated findings are separate from the numerical score and do not contribute to it. These scores are rule-based indicators, not probabilities of fraud.

---

## Data sources

- **Etherscan API v2** – Retrieves Ethereum mainnet transaction history.
- **Groq API** – Generates natural-language findings from a summary of up to 20 transactions.

Both services require API keys configured through environment variables: `ETHERSCAN_API_KEY` and `GROQ_API_KEY`.

---

## How to run

### Prerequisites

- Python 3.10 or later recommended
- pip
- Etherscan and Groq API keys

### Steps

```bash
# 1. Clone the repository
git clone <your-github-repository-url>
cd crypto-risk-analyser-main

# 2. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```dotenv
ETHERSCAN_API_KEY=your_etherscan_api_key
GROQ_API_KEY=your_groq_api_key
```

Launch the app:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, enter an Ethereum wallet address, and select **Analyze Wallet**.

---

## File structure

```text
.
├── app.py             # Streamlit interface and visualisations
├── backend.py         # Data retrieval, analysis, scoring and reports
├── requirements.txt   # Python dependencies
├── .gitignore         # Excludes environment secrets
└── README.md          # Project documentation
```

---

## Code walkthrough

| **Component** | **What it does** |
|---|---|
| `app.py` | Handles wallet input, analysis execution, risk display, charts, transaction table, and report download. |
| `get_transactions()` | Retrieves Ethereum transactions from Etherscan API v2. |
| `clean_transactions()` | Converts raw transaction records into a consistent format for analysis. |
| `calculate_risk_breakdown()` | Calculates the four risk signals and overall score. |
| `benford_analysis()` | Compares observed leading-digit frequencies with Benford's Law. |
| `timeline_data()` | Prepares chronologically ordered transactions for the timeline chart. |
| `analyze_risk()` | Uses the Groq API to generate AI-assisted findings. |
| `generate_report()` | Creates the downloadable text report. |

### Limitations

- Risk scores are heuristic and may produce false positives or false negatives.
- Benford's Law results can be misleading for small datasets or unsuitable transaction distributions.
- AI-generated findings may be inaccurate and should be independently verified.
- Results depend on API availability, returned transaction data, and valid credentials.
- The application analyses Ethereum mainnet transactions and does not independently verify wallet ownership or criminal activity.

