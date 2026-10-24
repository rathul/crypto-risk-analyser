# Crypto Transaction Risk Analyser

A Streamlit-based tool for screening Ethereum wallet transactions for potential risk signals. It combines rule-based transaction analysis with AI-generated findings to help users explore unusual transaction activity, review risk indicators, and understand patterns that may warrant further investigation.

The tool is intended for educational use, preliminary blockchain analysis, and exploratory screening. It does not establish whether a wallet is involved in criminal activity.

## 1. What It Does

### Wallet transaction retrieval

- Accepts an Ethereum wallet address as input.
- Retrieves normal transaction history from the Ethereum mainnet through the Etherscan API.
- Requests transactions across the available block range, ordered from newest to oldest.

### Rule-based risk scoring

The analyser evaluates four signals:

- **Velocity Risk:** Uses the average time gap between transactions to assess transaction frequency.
- **Volume Anomaly:** Compares the largest non-zero transaction amount with the average non-zero transaction amount.
- **Address Concentration:** Measures how frequently the most common recipient address appears among outgoing transactions.
- **Pattern Risk:** Examines failed transactions and repeated transaction amounts.

Each signal receives a score and a Low, Medium, or High label.

### AI-assisted key findings

The application sends a summary of up to the first 20 retrieved transactions to the Groq API using the `openai/gpt-oss-120b` model.

The prompt asks the model to identify potential risk signals, including unusually large transfers, rapid repeated transactions, transactions involving newly created addresses, and patterns associated with laundering or scam wallets.

The model returns three to five bullet points intended to explain the findings in plain language. These findings are separate from the rule-based numerical risk score.

### Benford's Law analysis

- Extracts leading digits from positive transaction amounts after converting them to ETH.
- Calculates the observed frequency of each leading digit from 1 through 9.
- Compares the observed frequencies with the theoretical Benford's Law distribution.
- Displays the comparison as a bar chart and line chart.

This analysis is exploratory and does not establish that a transaction is fraudulent or manipulated.

### Transaction timeline

- Sorts transactions chronologically.
- Displays transaction dates against transaction amounts in ETH.
- Uses a line chart with markers to show how transaction values vary over time.

### Transaction table

Displays a cleaned transaction table containing:

- Date and time in UTC.
- Sender address.
- Recipient address.
- Transaction amount in ETH.
- Whether the transaction failed.

The dashboard displays up to 20 rows in this table.

### Downloadable report

Generates a downloadable plain-text report containing:

- The wallet address.
- The report generation timestamp in UTC.
- The overall risk score.
- The four risk factors, their labels, and their individual scores.
- AI-generated key findings.
- A disclaimer about the tool's limitations.

## 2. How the Risk Score Works

The overall score is calculated using four rule-based signals. Each signal contributes 5, 15, or 25 points, depending on its classification.

| Risk signal | Low — 5 points | Medium — 15 points | High — 25 points |
|---|---|---|---|
| Velocity Risk | Average gap of 600 seconds or more | Average gap of at least 60 but less than 600 seconds | Average gap below 60 seconds |
| Volume Anomaly | Largest non-zero amount / average non-zero amount is 3 or less | Ratio greater than 3 and up to 10 | Ratio greater than 10 |
| Address Concentration | Most common recipient accounts for 25% or less of recipient entries | More than 25% and up to 50% | More than 50% |
| Pattern Risk | No failed transactions and repeated-amount frequency is at most 15% | At least one failed transaction or repeated-amount frequency above 15%, unless the high-risk condition applies | More than 3 failed transactions or a single amount occurs more than 30% of the time |

**Implementation details:**

- Velocity is based on the average gap between consecutive transaction timestamps. The calculation uses the retrieved transaction set.
- Volume anomaly uses the maximum positive transaction value divided by the average positive transaction value. Zero-value transactions are excluded from this calculation.
- Address concentration counts recipient addresses in the `to` field and measures the share belonging to the most frequent recipient.
- Pattern risk uses the number of failed transactions and the frequency of the most repeated transaction amount. Repeated amounts are compared using their converted ETH values.

The total score is the sum of the four component scores:

`Total Risk Score = Velocity Risk + Volume Anomaly + Address Concentration + Pattern Risk`

Each component has a maximum of 25 points, giving a theoretical total range of **20 to 100** for a non-empty transaction list.

### Risk levels

| Total score | Risk level |
|---|---|
| Below 34 | Low Risk |
| 34–66 | Medium Risk |
| 67–100 | High Risk |

These thresholds are applied by the Streamlit interface after calculating the total score. They are heuristic categories defined by the code, not statistically validated risk probabilities.

The AI-generated findings do not add points to the numerical score.

## 3. Data Source

### Etherscan API

Transaction data is retrieved from the Etherscan API v2 endpoint:

`https://api.etherscan.io/v2/api`

The request uses:

- `chainid=1`, corresponding to Ethereum mainnet.
- `module=account`
- `action=txlist`
- `startblock=0`
- `endblock=99999999`
- `sort=desc`

The application uses the returned normal transaction records, including transaction values, timestamps, sender and recipient addresses, gas prices, and execution status.

An Etherscan API key is expected in the `ETHERSCAN_API_KEY` environment variable.

### AI analysis

The application also requires a Groq API key, supplied through the `GROQ_API_KEY` environment variable. The Groq service is used to generate the natural-language findings.

The application does not use an uploaded transaction file or a bundled sample dataset in the supplied code.

### Data limitations

- The configured chain is Ethereum mainnet; other blockchains are not supported by this implementation.
- The analysis depends on the transaction records returned by Etherscan and successful API access.
- The AI findings depend on the Groq service and the configured model.
- The AI prompt receives only a summary of up to 20 transactions, while the rule-based calculations and visualizations use the retrieved transaction list.
- The code does not independently retrieve address creation dates, establish wallet ownership, or verify whether an address is associated with a known illicit entity.
- API errors, rate limits, invalid addresses, and missing credentials may prevent analysis from completing successfully.

## 4. How to Run

### Requirements

- Python 3.10 or newer is recommended for a modern environment. The repository does not explicitly pin a minimum Python version.
- An Etherscan API key.
- A Groq API key.
- Internet access for the API requests.

### Step 1: Clone the repository

```bash
git clone <your-github-repository-url>
cd crypto-risk-analyser-main
```

Replace the repository URL with your actual GitHub repository URL.

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root:

```dotenv
ETHERSCAN_API_KEY=your_etherscan_api_key
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder values with your own API keys. Keep `.env` private and do not commit it to GitHub. The repository's `.gitignore` already excludes `.env`.

### Step 5: Launch the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser, enter an Ethereum wallet address, and click **Analyze Wallet**.

## 5. File Structure

```text
crypto-risk-analyser-main/
├── app.py
├── backend.py
├── requirements.txt
└── .gitignore
```

- `app.py` — Streamlit interface, wallet input, risk score display, charts, transaction table, key findings, and report download.
- `backend.py` — Etherscan transaction retrieval, transaction cleaning, rule-based scoring, Benford's Law calculations, timeline preparation, Groq-based analysis, and report generation.
- `requirements.txt` — Python package dependencies.
- `.gitignore` — Excludes the `.env` file from version control.

## 6. Limitations

- **Screening, not proof:** A high score indicates that the implemented rules detected certain patterns. It does not prove fraud, money laundering, or other criminal activity.
- **Heuristic scoring:** The scoring thresholds are fixed rules in the code. The implementation does not establish that the score predicts actual illicit activity.
- **Benford's Law:** The comparison may be uninformative for small datasets or transaction amounts that do not follow the assumptions of Benford's Law. The implementation does not perform a formal statistical significance test.
- **Transaction velocity:** A short average gap between transactions can be legitimate. The score does not distinguish legitimate automated activity from malicious activity.
- **Volume anomalies:** A large transfer relative to a wallet's other transfers is not necessarily suspicious.
- **Recipient concentration:** Repeated transfers to one recipient can have legitimate explanations.
- **Repeated amounts and failed transactions:** These patterns may occur during ordinary wallet use and can generate false positives.
- **AI-generated findings:** The findings are model-generated and may be incomplete, inaccurate, or speculative. They should be checked against the underlying transaction data.
- **Limited AI context:** Only the first 20 retrieved transactions are passed to the AI prompt. The code does not provide the model with independently verified address reputations or address creation dates.
- **Data availability:** Results depend on Etherscan access, API limits, valid credentials, and the availability of transaction records.
- **Error handling:** The current implementation does not comprehensively handle API error responses, network failures, or AI service failures. Some failures may interrupt analysis rather than produce a complete report.
- **Benford's Law implementation:** Leading digits are extracted from ETH-converted amounts formatted to a fixed number of decimal places. This can affect the extracted digits, particularly for very small amounts, so the chart should be interpreted cautiously.
- **No comprehensive forensic tracing:** The application does not implement a full blockchain investigation workflow, transaction graph analysis, cross-chain tracing, or verified sanctions and wallet-risk database checks.

## 7. Disclaimer

This project is an educational and exploratory blockchain transaction screening tool. It is not a substitute for professional blockchain forensics, compliance review, or a formal investigation.

Risk scores and AI-generated findings are indicative only and may produce false positives or false negatives. Do not use the output as the sole basis for financial, legal, compliance, or law-enforcement decisions.

This tool does not provide financial or legal advice.

## 8. Code Structure

| Component | Responsibility |
|---|---|
| Streamlit interface (`app.py`) | Accepts a wallet address, triggers analysis, displays risk scores and findings, renders charts and tables, and offers a report download. |
| `get_transactions()` | Requests normal Ethereum mainnet transactions from Etherscan API v2. |
| `clean_transactions()` | Converts raw transaction records into readable dates, addresses, ETH amounts, and failure indicators. |
| `calculate_risk_breakdown()` | Computes velocity, volume anomaly, recipient concentration, and transaction-pattern scores, then sums them. |
| `benford_analysis()` | Calculates observed leading-digit frequencies and theoretical Benford frequencies for charting. |
| `timeline_data()` | Sorts transactions by timestamp and prepares dates and ETH values for the timeline chart. |
| `analyze_risk()` | Sends a summary of up to 20 transactions to the configured Groq model and returns natural-language findings. |
| `generate_report()` | Builds the downloadable text report with the score, component breakdown, findings, and disclaimer. |
| `requirements.txt` | Lists the Python packages required by the project. |
| `.gitignore` | Prevents the local `.env` file from being tracked by Git. |

## 9. Technologies Used

- **Python** — Application logic and transaction analysis.
- **Streamlit** — Interactive web application interface.
- **Etherscan API v2** — Ethereum mainnet transaction retrieval.
- **Groq API** — AI-assisted generation of key findings.
- **Plotly** — Benford's Law and transaction timeline charts.
- **Requests** — HTTP requests to the Etherscan API.
- **python-dotenv** — Loading environment variables from `.env`.
- **Collections and datetime** — Frequency counting, transaction pattern calculations, and timestamp formatting.
