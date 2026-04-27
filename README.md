# 💸 SplitSmart AI

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_API-8E75B2?style=for-the-badge&logo=googlebard&logoColor=white)

**SplitSmart** is a highly capable AI-powered expense splitting orchestrator built for roommates and groups. Moving far beyond native arithmetic tools like Splitwise, SplitSmart integrates multi-modal generative AI and statistical machine learning (K-Means) to turn painful group logistics into a frictionless, entertaining experience.

---

## 🚀 Key Features

* **🧠 Natural Language "Magic Entry":** 
  Instead of digging through 5 form fields, just type what happened (e.g., *"Raj paid 840 for pizza"*). SplitSmart's internal Gemini NLP service dynamically parses it securely into structured database records.

* **📸 Receipt OCR Scanner:**
  Hate manual entry entirely? Upload a picture of a receipt. Using Google's **Gemini 1.5 Flash Vision** engine, SplitSmart physically reads the receipt, extracts the total, categorizes the purchase (e.g., *Groceries*), and writes it to the ledger automatically.

* **📉 Settlement Engine & Analytics:**
  Calculates mathematically optimal "Who Owes Whom" settlements combined with interactive Plotly dashboards mapping out spending distributions per category.

* **🔥 AI Spending Profile Roast:**
  An embedded **K-Means Clustering** engine runs continuous background analysis on all users, grouping them into financial spending profiles based on metrics like frequency and averages. Instead of rigid graphs, to make it fun, an edgy AI consumes the resulting cluster output to generate a merciless "Financial Roast" of your group's latest habits.

---

## 🛠️ Architecture

* **Frontend:** Streamlit 
* **Backend:** Python + Pandas + SQLite
* **Machine Learning:** `scikit-learn` (Unsupervised Clustering)
* **Generative AI Parsing Engine:** Google Gemini SDK (`gemini-1.5-flash`)
* **Visualizations:** Plotly Express

---

## 💻 Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/george817/Split-Smart-.git
   cd Split-Smart-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   Create a `.env` file at the root with your API key:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

4. **Launch Application:**
   ```bash
   streamlit run app.py
   ```
