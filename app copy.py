import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from backend.database import init_db, add_expense, get_expenses, delete_expense
from backend.ml_model import detect_anomalies
from backend.utils import calculate_splits

st.set_page_config(
    page_title="SplitSmart",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0b0f1a;
    color: #e8eaf0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1525 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #c9cde0 !important; }
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 10%, rgba(99,102,241,0.12) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(236,72,153,0.10) 0%, transparent 50%),
                #0b0f1a;
}
#MainMenu, footer, header { visibility: hidden; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(236,72,153,0.10));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(10px);
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #6366f1, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] { color: #9ca3c0 !important; font-size: 0.8rem !important; }

.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 28px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.5) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    overflow: hidden;
}
hr { border-color: rgba(255,255,255,0.07) !important; }
.stAlert { border-radius: 12px !important; border: none !important; }
[data-testid="stPlotlyChart"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(99,102,241,0.15);
}
[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero Banner ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(236,72,153,0.15) 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 24px;
    padding: 40px 48px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
">
  <div style="position:absolute;top:-60px;right:-60px;width:220px;height:220px;border-radius:50%;
              background:radial-gradient(circle,rgba(236,72,153,0.25),transparent 70%);"></div>
  <div style="position:absolute;bottom:-40px;left:30%;width:160px;height:160px;border-radius:50%;
              background:radial-gradient(circle,rgba(99,102,241,0.2),transparent 70%);"></div>
  <div style="font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;margin-bottom:8px;
              background:linear-gradient(90deg,#6366f1,#ec4899,#f59e0b);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    SplitSmart
  </div>
  <div style="color:#9ca3c0;font-size:1rem;max-width:520px;line-height:1.6;">
    AI-powered expense splitting with real-time anomaly detection.
    Know exactly who owes what — and flag unusual spending instantly.
  </div>
  <div style="margin-top:16px;display:flex;gap:12px;flex-wrap:wrap;">
    <span style="background:rgba(99,102,241,0.2);border:1px solid rgba(99,102,241,0.4);
                 color:#a5b4fc;padding:4px 14px;border-radius:20px;font-size:0.78rem;">
      Isolation Forest ML
    </span>
    <span style="background:rgba(236,72,153,0.15);border:1px solid rgba(236,72,153,0.35);
                 color:#f9a8d4;padding:4px 14px;border-radius:20px;font-size:0.78rem;">
      SQLite Backend
    </span>
    <span style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.35);
                 color:#fcd34d;padding:4px 14px;border-radius:20px;font-size:0.78rem;">
      Real-time Splits
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
                margin-bottom:4px;color:#a5b4fc;">Group Setup</div>
    """, unsafe_allow_html=True)

    group_name = st.text_input("Group name", "Hostel Room 4B")
    members_input = st.text_area("Members (one per line)", "Raj\nPriya\nAmit\nSneha")
    members = [m.strip() for m in members_input.split('\n') if m.strip()]

    st.divider()
    st.markdown(f"""
    <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);
                border-radius:12px;padding:14px 16px;">
      <div style="font-size:0.75rem;color:#9ca3c0;margin-bottom:6px;">ACTIVE GROUP</div>
      <div style="font-family:'Syne',sans-serif;font-weight:700;color:#a5b4fc;">{group_name}</div>
      <div style="font-size:0.8rem;color:#6b7280;margin-top:4px;">{len(members)} members</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="font-size:0.75rem;color:#4b5563;text-align:center;line-height:1.6;">
        Built by Anirban Kumar<br>KIIT University · 2025<br>
        <span style="color:#6366f1;">ML/AI Engineer</span>
    </div>
    """, unsafe_allow_html=True)

# ── Add Expense ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700;
            margin-bottom:16px;color:#e8eaf0;">Add Expense</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    paid_by = st.selectbox("Paid by", members)
with col2:
    amount = st.number_input("Amount (Rs)", min_value=0.0, step=10.0)
with col3:
    category = st.selectbox("Category", ["Food","Transport","Rent","Groceries","Entertainment","Other"])

description = st.text_input("Description (optional)", placeholder="e.g. Pizza night, Uber to airport...")
col_btn, col_space = st.columns([1, 4])
with col_btn:
    add_clicked = st.button("Add Expense", type="primary", use_container_width=True)

if add_clicked:
    if amount > 0:
        add_expense(paid_by, amount, category, description, group_name)
        st.success(f"Added Rs {amount:.0f} paid by {paid_by}!")
        st.rerun()
    else:
        st.warning("Please enter an amount greater than 0.")

# ── Load Data ─────────────────────────────────────────────────────────────────
init_db()
df = get_expenses(group_name)

if not df.empty:
    st.divider()

    total = df['amount'].sum()
    _, per_person = calculate_splits(df, members)
    top_spender = df.groupby('paid_by')['amount'].sum().idxmax()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Spent", f"Rs {total:,.0f}")
    with m2:
        st.metric("Fair Share / Person", f"Rs {per_person:,.0f}")
    with m3:
        st.metric("Transactions", len(df))
    with m4:
        st.metric("Top Spender", top_spender)

    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                    margin-bottom:14px;">Who Owes Whom</div>
        """, unsafe_allow_html=True)
        settlements, _ = calculate_splits(df, members)
        if settlements:
            for s in settlements:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(236,72,153,0.07));
                            border:1px solid rgba(99,102,241,0.2);border-radius:12px;
                            padding:14px 18px;margin-bottom:10px;display:flex;
                            align-items:center;justify-content:space-between;">
                  <div>
                    <span style="color:#f9a8d4;font-weight:600;">{s['from']}</span>
                    <span style="color:#6b7280;margin:0 8px;">owes</span>
                    <span style="color:#a5b4fc;font-weight:600;">{s['to']}</span>
                  </div>
                  <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;
                              background:linear-gradient(90deg,#6366f1,#ec4899);
                              -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    Rs {s['amount']:,.2f}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Everyone is settled up!")

    with col2:
        st.markdown("""
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                    margin-bottom:14px;">Spending by Category</div>
        """, unsafe_allow_html=True)
        fig_pie = px.pie(
            df, values='amount', names='category', hole=0.5,
            color_discrete_sequence=['#6366f1','#ec4899','#f59e0b','#10b981','#3b82f6','#8b5cf6']
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3c0', family='DM Sans'),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        fig_pie.update_traces(textfont_color='white')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                margin-bottom:14px;">Spending per Person</div>
    """, unsafe_allow_html=True)
    person_totals = df.groupby('paid_by')['amount'].sum().reset_index()
    fig_bar = px.bar(
        person_totals, x='paid_by', y='amount', color='amount',
        color_continuous_scale=['#6366f1','#ec4899','#f59e0b'],
        labels={'paid_by':'Member','amount':'Total Spent (Rs)'}
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9ca3c0', family='DM Sans'),
        coloraxis_showscale=False, margin=dict(t=10, b=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
    )
    fig_bar.update_traces(marker_line_width=0)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                margin-bottom:14px;">Anomaly Detection</div>
    """, unsafe_allow_html=True)

    features, flagged = detect_anomalies(df)
    if flagged:
        for f in flagged:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(239,68,68,0.15),rgba(236,72,153,0.1));
                        border:1px solid rgba(239,68,68,0.4);border-radius:14px;
                        padding:18px 22px;margin-bottom:10px;">
              <div style="font-size:1.1rem;font-weight:700;color:#fca5a5;margin-bottom:4px;">
                Unusual Spending Detected
              </div>
              <div style="color:#d1d5db;">
                <strong style="color:#f87171;">{f}</strong> has a spending pattern
                significantly different from the rest of the group.
                Flagged by the Isolation Forest ML model.
              </div>
            </div>
            """, unsafe_allow_html=True)
        if not features.empty:
            fig_a = px.bar(
                features, x='paid_by', y='total_spent', color='anomaly',
                color_continuous_scale=['#10b981','#ef4444'],
                labels={'paid_by':'Member','total_spent':'Total Spent (Rs)','anomaly':'Anomaly Score'}
            )
            fig_a.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9ca3c0'), margin=dict(t=10,b=10),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_a, use_container_width=True)
    elif not features.empty:
        st.markdown("""
        <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
                    border-radius:12px;padding:16px 20px;color:#6ee7b7;">
            No unusual spending patterns detected. Everyone is spending normally.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);
                    border-radius:12px;padding:16px 20px;color:#a5b4fc;">
            Add at least 4 expenses to enable anomaly detection.
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                margin-bottom:14px;">All Expenses</div>
    """, unsafe_allow_html=True)
    st.dataframe(
        df[['id','paid_by','amount','category','description','date']].rename(columns={
            'id':'#','paid_by':'Paid By','amount':'Amount (Rs)',
            'category':'Category','description':'Description','date':'Date'
        }),
        use_container_width=True, hide_index=True
    )

else:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px;">
      <div style="font-size:4rem;margin-bottom:16px;">💸</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;
                  color:#e8eaf0;margin-bottom:8px;">No expenses yet</div>
      <div style="color:#6b7280;">Add your first expense above to get started.</div>
    </div>
    """, unsafe_allow_html=True)
