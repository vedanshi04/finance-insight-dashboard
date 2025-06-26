
# 💼 Finance Insight Dashboard

> **Tagline:** Upload. Clean. Visualize. — Make sense of financial data in minutes, not hours.

A powerful and interactive **Streamlit app** built to help you **analyze, clean, and visualize financial data**—all in just a few clicks.

Whether you're a data analyst, finance professional, or business stakeholder, this tool simplifies complex financial datasets and transforms them into actionable insights.

---

## 🚀 Features That Make a Difference

✅ Upload CSV or Excel files  
✅ Automatic detection of numeric, categorical, boolean, datetime, and text columns  
✅ Data cleaning (null handling, type conversion, duplicates, outliers)  
✅ Outlier removal via IQR (optional toggle)  
✅ Insightful visualizations: line plots, bar charts, area plots, treemaps, heatmaps  
✅ AI-powered summarization using the OpenAI API
✅ Built with modular and production-ready Python code

---

## 📂 Project Structure

```
finance-insight-dashboard/
├── Home.py                  # Main entry point
├── pages/                   # Streamlit multi-page files
│   ├── 1_Overview.py
│   ├── 2_Data_Analysis.py
│   ├── 3_Data_Visualization.py
│   └── 4_OpenAI_Summary.py
├── src/                     # Core logic and utilities
│   ├── auth.py
│   └── preprocess.py
├── .streamlit
│   ├── secrets.toml
│   └── config.toml          # Streamlit config (e.g., theme, secrets)
├── requirements.txt         # Python dependencies
├── .gitignore               # Files to ignore in Git
└── README.md                # You're reading it
```

---

## 🛠️ Built With

- **Python 3.11+**
- **Streamlit** – web app interface
- **Pandas** – data manipulation
- **Matplotlib & Plotly** – plotting
- **OpenAI API** – for natural-language data summaries
- **Custom Preprocessing** – robust cleaning, type inference, and outlier removal

---

## 📥 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/vedanshi04/finance-insight-dashboard.git
cd finance-insight-dashboard
```

### 2. Set Up a Virtual Environment (with `uv`)

If you’re using [**uv**](https://github.com/astral-sh/uv) for faster dependency management:

```bash
uv venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

If you're using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Add OpenAI API Key

```bash
[openai]
api_key = "sk-..."
```

### 4. Launch the App

```bash
streamlit run Home.py
```

---

## 🌐 Live Deployment

You can view the hosted version here:

👉 [https://finance-insight-dashboard.streamlit.app/](https://finance-insight-dashboard.streamlit.app)
[username - admin, password - 1234 [only for sampling]]
*(Note: Deployment powered by [Streamlit Cloud](https://streamlit.io/cloud))*

---

## 📊 Sample Use Cases

- Financial report generation
- Exploratory analysis of transactional datasets
- Investment, revenue, or sales trend visualization
- Real-time summaries of financial files using GPT
- Teaching EDA and AI summarization in finance

---

## 🧠 What Makes This App Unique?

Unlike most dashboards, this one:
- **understands your data** without hardcoded assumptions
- **cleans messy data** with smart type and outlier handling
- **adapts visualizations** to different data types dynamically
- **summarizes insights using AI,** not static code
- lets you **explore and learn** from data, not just view it

---

## 🤝 Contributing

Want to improve this app? Feel free to fork and PR!

---

## 📄 License

This project is open-source and licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

This license includes a **grant of patent rights**, providing legal protection for both contributors and users.

---

> Built with ❤️ by Vedanshi Ponkia for making finance data exploration effortless and elegant.
