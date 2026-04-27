import streamlit as st
import plotly.express as px
from backend.database import init_db, add_expense, get_expenses, delete_expense
from backend.ml_model import detect_anomalies
from backend.utils import calculate_splits

st.set_page_config(page_title="SplitSmart", page_icon="💸", layout="wide")
init_db()

st.title("💸 SplitSmart")
st.caption("AI-powered expense splitter with anomaly detection")

with st.sidebar:
    st.header("Group Setup")
    group_name = st.text_input("Group name", "Hostel Room 4B")
    members_input = st.text_area("Members (one per line)", "Raj\nPriya\nAmit\nSneha")
    members = [m.strip() for m in members_input.split('\n') if m.strip()]
    st.divider()
    st.caption("Built by Anirban | KIIT 2025")

st.subheader("Add Expense")
tab1, tab2, tab3 = st.tabs(["✨ Magic Entry (AI)", "📸 Receipt Scanner", "📝 Manual Entry"])

with tab1:
    st.caption("Tell the AI what happened, and it will fill everything out.")
    col_a, col_b = st.columns([4, 1])
    with col_a:
        nl_text = st.text_input("Expense description", placeholder="E.g. Raj paid 840 for pizza...")
    with col_b:
        st.write("") # spacing for alignment
        st.write("")
        ai_submit = st.button("✨ Auto-fill", type="primary", use_container_width=True)
        
    if ai_submit and nl_text:
        with st.spinner("🤖 Parsing using Gemini..."):
            from backend.services.gemini_service import parse_expense_nl
            parsed = parse_expense_nl(nl_text, members)
            
            if parsed and parsed.get('amount') and parsed.get('paid_by') in members:
                desc = parsed.get('description', '')
                add_expense(parsed['paid_by'], float(parsed['amount']), parsed.get('category', 'Other'), desc, group_name)
                st.success(f"✅ Added Rs {parsed['amount']} paid by {parsed['paid_by']} for {desc}!")
                st.rerun()
            else:
                st.error("😕 Couldn't confidently extract the details. Make sure the name matches the group members, or use Manual Entry.")

with tab2:
    st.caption("Upload a receipt and AI will extract the total and category.")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, width=200)
        receipt_payer = st.selectbox("Who paid this receipt?", members, key="rec_payer")
        if st.button("🔍 Scan & Extract", type="primary", use_container_width=True):
            with st.spinner("🤖 Reading image..."):
                from backend.services.gemini_service import extract_receipt
                parsed = extract_receipt(uploaded_file.getvalue(), members)
                if parsed and parsed.get('amount'):
                    desc = parsed.get('description', 'Receipt Scan')
                    add_expense(receipt_payer, float(parsed['amount']), parsed.get('category', 'Other'), desc, group_name)
                    st.success(f"✅ Extracted & Added: Rs {parsed['amount']} for {desc}!")
                    st.rerun()
                else:
                    st.error("😕 Couldn't read the receipt clearly. Try manual entry.")

with tab3:
    col1, col2, col3 = st.columns(3)
    with col1:
        paid_by = st.selectbox("Paid by", members)
    with col2:
        amount = st.number_input("Amount (Rs)", min_value=0.0, step=10.0)
    with col3:
        category = st.selectbox("Category", ["Food", "Transport", "Rent", "Groceries", "Entertainment", "Other"])

    description = st.text_input("Description (optional)")
    if st.button("Add Expense"):
        if amount > 0:
            add_expense(paid_by, amount, category, description, group_name)
            st.success("Added!")
            st.rerun()
        else:
            st.warning("Enter an amount greater than 0")

df = get_expenses(group_name)

if not df.empty:
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Who Owes Whom")
        settlements, per_person = calculate_splits(df, members)
        st.metric("Fair share per person", f"Rs {per_person}")
        if settlements:
            for s in settlements:
                st.info(f"{s['from']} owes {s['to']}  Rs {s['amount']}")
        else:
            st.success("All settled up!")

    with col2:
        st.subheader("Spending by Category")
        fig = px.pie(df, values='amount', names='category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Anomaly Detection")
    features, flagged = detect_anomalies(df)
    if flagged:
        st.warning(f"Unusual spending detected: {', '.join(flagged)} — pattern is significantly different from the group.")
    elif not features.empty:
        st.success("No unusual spending patterns detected.")
    else:
        st.info("Add at least 4 expenses to enable anomaly detection.")

    if not features.empty:
        fig2 = px.bar(features, x='paid_by', y='total_spent',
                      color='anomaly',
                      color_continuous_scale=['green', 'red'],
                      title="Total spending per person (red = flagged)")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("🔥 AI Spending Roast")
    st.caption("We grouped your spending habits using KMeans. Let AI review your life choices.")
    if st.button("Generate Roast", type="primary"):
        with st.spinner("🤖 Analyzing your terrible financial decisions..."):
            from backend.ml_model import get_spending_personality
            from backend.services.gemini_service import generate_spending_roast
            
            profiles = get_spending_personality(df)
            if "Not enough data" in profiles or "least two" in profiles:
                st.warning(profiles)
            else:
                st.info(f"**Data Profile Context Used (KMeans):**\n{profiles}")
                roast = generate_spending_roast(group_name, profiles)
                st.error(roast, icon="🔥")

    st.divider()
    st.subheader("All Expenses")
    st.dataframe(df[['id','paid_by','amount','category','description','date']], use_container_width=True)
else:
    st.info("No expenses yet. Add one above to get started!")
