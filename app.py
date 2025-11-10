import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from sqlalchemy import create_engine
from openai import OpenAI

# ---- SETTINGS ----
SERVER = "localhost\\SQLEXPRESS"
DATABASE = "AdventureWorks2022"
ENGINE = create_engine(
    f"mssql+pyodbc://{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Load OpenAI API key from environment variable
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# ---- STREAMLIT UI ----
st.set_page_config(page_title="SQL + AI Dashboard", layout="wide")
st.title("🧠 SQL + AI Data Explorer")
st.write("✅ App loaded successfully! Enter a SQL query below ⬇️")

# --- Query input section ---
query = st.text_area(
    "✍️ Enter your SQL query:",
    """SELECT 
        PC.Name AS ProductCategory,
        SUM(SOD.LineTotal) AS TotalSales,
        COUNT(SOD.SalesOrderID) AS TotalOrders,
        AVG(SOD.UnitPrice) AS AveragePrice
       FROM Sales.SalesOrderDetail SOD
       JOIN Production.Product P 
           ON SOD.ProductID = P.ProductID
       JOIN Production.ProductSubcategory PS 
           ON P.ProductSubcategoryID = PS.ProductSubcategoryID
       JOIN Production.ProductCategory PC 
           ON PS.ProductCategoryID = PC.ProductCategoryID
       GROUP BY PC.Name
       ORDER BY TotalSales DESC;""",
    height=200
)


# --- Run Query Button ---
if st.button("Run Query"):
    try:
        with st.spinner("Running query..."):
            df = pd.read_sql(query, ENGINE)

        st.success(f"✅ Query executed successfully! Returned {len(df)} rows.")
        st.dataframe(df, width='stretch')

        # ---- NUMERIC CHARTS ----
        numeric_cols = df.select_dtypes("number").columns
        if len(numeric_cols) > 0:
            st.subheader("📊 Numeric Data Visualization")
            st.bar_chart(df[numeric_cols])

        # ---- AI INSIGHTS ----
        if OPENAI_KEY:
            try:
                st.subheader("🤖 AI Summary Generator")
                client = OpenAI(api_key=OPENAI_KEY)
                with st.spinner("🧠 Generating AI insights..."):
                    sample = df.head(10).to_string()
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert data analyst."},
                            {"role": "user", "content": f"Analyze this SQL data and summarize key insights:\n{sample}"}
                        ]
                    )
                    ai_output = response.choices[0].message.content
                    st.markdown(f"### 🧠 AI Insights\n{ai_output}")
            except Exception as e:
                st.warning(f"⚠️ AI insights unavailable: {e}")
        else:
            st.info("💡 Your OpenAI API key is not detected. Run this in PowerShell:\n\n"
                    "`setx OPENAI_API_KEY \"your_key_here\"`\n\nThen restart VS Code and rerun Streamlit.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- Check AI Key Status ---
if OPENAI_KEY:
    st.sidebar.success("✅ OpenAI API Key Loaded Successfully!")
else:
    st.sidebar.warning("⚠️ OpenAI API Key Missing. Insights Disabled.")
