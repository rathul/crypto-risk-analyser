import streamlit as st
from backend import get_transactions, clean_transactions, calculate_risk_breakdown, analyze_risk

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
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #16161f;
        border: 1px solid #2a2a38 !important;
        border-radius: 16px !important;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="main-title">Crypto Transaction Risk Analyser</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Paste a wallet address to check its transaction risk profile.</div>', unsafe_allow_html=True)

# ---------- INPUT ----------
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
            breakdown = calculate_risk_breakdown(txs)
            score = breakdown["total_score"]

            if score < 34:
                badge_class, badge_text = "badge-low", "LOW RISK"
            elif score < 67:
                badge_class, badge_text = "badge-medium", "MEDIUM RISK"
            else:
                badge_class, badge_text = "badge-high", "HIGH RISK"

            with st.spinner("Analyzing risk..."):
                ai_findings = analyze_risk(txs)

            # ---------- RISK SCORE + BREAKDOWN ----------
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown('<div class="risk-label">Risk Score</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="risk-score">{score}</div>', unsafe_allow_html=True)
                    st.markdown(f'<span class="badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="risk-label">Score Breakdown</div>', unsafe_allow_html=True)
                    for factor in breakdown["factors"]:
                        st.write(f"**{factor['name']}**: {factor['label']} ({factor['score']}/{factor['max']})")
                        st.progress(factor["score"] / factor["max"])

            # ---------- AI FINDINGS ----------
            with st.container(border=True):
                st.markdown('<div class="risk-label">Key Findings</div>', unsafe_allow_html=True)
                st.write(ai_findings)

            # ---------- CLEAN TRANSACTION TABLE ----------
            with st.container(border=True):
                st.markdown(f'<div class="risk-label">Recent Transactions ({len(txs)} found)</div>', unsafe_allow_html=True)
                clean_txs = clean_transactions(txs)
                st.dataframe(clean_txs[:20], use_container_width=True)

st.caption("⚠️ AI-assisted heuristic analysis, not a substitute for professional forensic tools.")