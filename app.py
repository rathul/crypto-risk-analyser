import re
import streamlit as st

import os
import requests
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

    Give me:
    1. A risk score in the exact format: "Score: XX/100" (replace XX with a number)
    2. 3-5 bullet points explaining why
    3. One-line verdict (Low / Medium / High risk)
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

st.set_page_config(page_title="Crypto Risk Analyser", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    .stApp {
        background-color: #0d0d12;
        color: #e6e6f0;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .subtitle {
        color: #9a9ab0;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }
    .card {
        background-color: #16161f;
        border: 1px solid #2a2a38;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .risk-score {
        font-size: 3.2rem;
        font-weight: 800;
        color: #ffffff;
    }
    .risk-label {
        color: #9a9ab0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-low { background-color: #1f3d2b; color: #4ade80; }
    .badge-medium { background-color: #3d3a1f; color: #facc15; }
    .badge-high { background-color: #3d1f1f; color: #f87171; }

    div.stButton > button {
        background: linear-gradient(90deg, #4f6ef7, #8b7cf6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #3f5ce0, #7a68e8);
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #16161f;
        color: white;
        border: 1px solid #2a2a38;
        border-radius: 10px;
        div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #16161f;
    border: 1px solid #2a2a38 !important;
    border-radius: 16px !important;
    padding: 10px;
}
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
with st.container(border=True):
    col1, col2 = st.columns([1, 3])
    ..., unsafe_allow_html=True)

# ---------- INPUT CARD ----------
with st.container(border=True):
    wallet = st.text_input("Wallet address", placeholder="0x...")
    analyze = st.button("Analyze Wallet")
    

if analyze:
    if not wallet:
        st.warning("Enter a wallet address first.")
    else:
        with st.spinner("Fetching transactions..."):
            txs = get_transactions(wallet)

        if not txs or isinstance(txs, str):
            st.error("No transactions found or invalid address.")
        else:
            with st.spinner("Analyzing risk..."):
                result = analyze_risk(txs)

            # try to pull a numeric score out of the AI's response
            score_match = re.search(r"(\d{1,3})\s*/\s*100", result)
            score = int(score_match.group(1)) if score_match else None

            if score is not None:
                if score < 34:
                    badge_class, badge_text = "badge-low", "LOW RISK"
                elif score < 67:
                    badge_class, badge_text = "badge-medium", "MEDIUM RISK"
                else:
                    badge_class, badge_text = "badge-high", "HIGH RISK"
            else:
                badge_class, badge_text = "badge-medium", "UNKNOWN"

            # ---------- RISK SCORE CARD ----------
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown('<div class="risk-label">Risk Score</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="risk-score">{score if score is not None else "--"}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="risk-label">AI Analysis</div>', unsafe_allow_html=True)
                st.write(result)
            st.markdown('</div>', unsafe_allow_html=True)

            # ---------- TRANSACTIONS CARD ----------
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="risk-label">Recent Transactions ({len(txs)} found)</div>', unsafe_allow_html=True)
            st.dataframe(txs[:20], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            

st.caption("⚠️ AI-assisted heuristic analysis, not a substitute for professional forensic tools.")