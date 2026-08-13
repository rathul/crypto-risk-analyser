import requests
import os
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY")
print("KEY LOADED:", ETHERSCAN_KEY)

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

from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
    1. A risk score from 0-100
    2. 3-5 bullet points explaining why
    3. One-line verdict (Low / Medium / High risk)
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# quick test
import streamlit as st

st.title("Crypto Transaction Risk Analyser")
st.write("Paste an Ethereum wallet address to check its transaction risk.")
st.caption("⚠️ AI-assisted heuristic analysis, not a substitute for professional forensic tools.")

wallet = st.text_input("Wallet address", placeholder="0x...")

if st.button("Analyze"):
    if wallet:
        with st.spinner("Fetching transactions..."):
            txs = get_transactions(wallet)
        if not txs or isinstance(txs, str):
            st.error("No transactions found or invalid address.")
        else:
            st.success(f"Found {len(txs)} transactions")
            st.dataframe(txs[:20])

            with st.spinner("Analyzing risk..."):
                result = analyze_risk(txs)
            st.subheader("Risk Analysis")
            st.write(result)
    else:
        st.warning("Enter a wallet address first.")