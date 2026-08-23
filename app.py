import os
import requests
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_transactions(wallet_address):
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": 1,
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["result"]


def clean_transactions(txs):
    """Convert raw Etherscan fields into clean, forensic-report-friendly rows."""
    cleaned = []
    for tx in txs:
        cleaned.append({
            "Date/Time": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d %H:%M:%S"),
            "From": tx["from"],
            "To": tx["to"],
            "Amount (ETH)": round(int(tx["value"]) / 10**18, 6),
            "Failed": tx["isError"] == "1",
        })
    return cleaned


def calculate_risk_breakdown(txs):
    """Rule-based scoring — transparent, not a black box."""
    if not txs:
        return {}

    values = [int(tx["value"]) / 10**18 for tx in txs]
    timestamps = sorted([int(tx["timeStamp"]) for tx in txs])
    addresses = [tx["to"] for tx in txs if tx["to"]]

    gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 999999
    if avg_gap < 60:
        velocity_score, velocity_label = 25, "High"
    elif avg_gap < 600:
        velocity_score, velocity_label = 15, "Medium"
    else:
        velocity_score, velocity_label = 5, "Low"

    nonzero_values = [v for v in values if v > 0]
    if nonzero_values:
        max_val = max(nonzero_values)
        avg_val = sum(nonzero_values) / len(nonzero_values)
        volume_ratio = max_val / avg_val if avg_val > 0 else 0
    else:
        volume_ratio = 0
    if volume_ratio > 10:
        volume_score, volume_label = 25, "High"
    elif volume_ratio > 3:
        volume_score, volume_label = 15, "Medium"
    else:
        volume_score, volume_label = 5, "Low"

    address_counts = Counter(addresses)
    if address_counts:
        top_freq = address_counts.most_common(1)[0][1]
        concentration_ratio = top_freq / len(addresses)
    else:
        concentration_ratio = 0
    if concentration_ratio > 0.5:
        concentration_score, concentration_label = 25, "High"
    elif concentration_ratio > 0.25:
        concentration_score, concentration_label = 15, "Medium"
    else:
        concentration_score, concentration_label = 5, "Low"

    failed_count = sum(1 for tx in txs if tx["isError"] == "1")
    value_counts = Counter(values)
    most_repeated = value_counts.most_common(1)[0][1] if value_counts else 0
    if failed_count > 3 or most_repeated > len(txs) * 0.3:
        pattern_score, pattern_label = 25, "High"
    elif failed_count > 0 or most_repeated > len(txs) * 0.15:
        pattern_score, pattern_label = 15, "Medium"
    else:
        pattern_score, pattern_label = 5, "Low"

    total = velocity_score + volume_score + concentration_score + pattern_score

    return {
        "total_score": total,
        "factors": [
            {"name": "Velocity Risk", "label": velocity_label, "score": velocity_score, "max": 25},
            {"name": "Volume Anomaly", "label": volume_label, "score": volume_score, "max": 25},
            {"name": "Address Concentration", "label": concentration_label, "score": concentration_score, "max": 25},
            {"name": "Pattern Risk", "label": pattern_label, "score": pattern_score, "max": 25},
        ]
    }


def benford_analysis(txs):
    """Returns observed leading-digit distribution vs Benford's Law expected distribution."""
    values = [int(tx["value"]) / 10**18 for tx in txs if int(tx["value"]) > 0]
    leading_digits = []
    for v in values:
        s = f"{v:.10f}".lstrip("0.").lstrip("0")
        if s and s[0].isdigit() and s[0] != "0":
            leading_digits.append(int(s[0]))

    observed_counts = Counter(leading_digits)
    total = len(leading_digits)

    observed = []
    expected = []
    digits = list(range(1, 10))
    for d in digits:
        observed_pct = (observed_counts.get(d, 0) / total * 100) if total > 0 else 0
        expected_pct = __import__("math").log10(1 + 1/d) * 100
        observed.append(observed_pct)
        expected.append(expected_pct)

    return digits, observed, expected


def timeline_data(txs):
    """Returns dates and transaction values for a timeline chart, oldest to newest."""
    sorted_txs = sorted(txs, key=lambda tx: int(tx["timeStamp"]))
    dates = [datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d") for tx in sorted_txs]
    values = [int(tx["value"]) / 10**18 for tx in sorted_txs]
    return dates, values


def analyze_risk(transactions):
    summary = []
    for tx in transactions[:20]:
        summary.append({
            "from": tx["from"],
            "to": tx["to"],
            "value_eth": int(tx["value"]) / 10**18,
            "timestamp": tx["timeStamp"],
            "gas_price": tx["gasPrice"]
        })

    prompt = f"""
    You are a crypto fraud analyst. Analyze these transactions for risk signals:
    {summary}

    Look for: unusually large transfers, rapid repeated transactions (possible bot/mixing behavior),
    transactions to newly-created addresses, and any patterns typical of laundering or scam wallets.

    Give me 3-5 bullet points explaining the key risk signals, in plain language for a report.
    Do not include a numeric score - just the findings.
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_report(wallet, breakdown, ai_findings):
    lines = []
    lines.append("CRYPTO TRANSACTION RISK REPORT")
    lines.append("=" * 40)
    lines.append(f"Wallet Address: {wallet}")
    lines.append(f"Analysis Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"Overall Risk Score: {breakdown['total_score']}/100")
    lines.append("")
    lines.append("RISK BREAKDOWN")
    lines.append("-" * 40)
    for factor in breakdown["factors"]:
        lines.append(f"{factor['name']}: {factor['label']} ({factor['score']}/{factor['max']})")
    lines.append("")
    lines.append("KEY FINDINGS")
    lines.append("-" * 40)
    lines.append(ai_findings)
    lines.append("")
    lines.append("DISCLAIMER: AI-assisted heuristic analysis, not a substitute for professional forensic tools.")
    return "\n".join(lines)