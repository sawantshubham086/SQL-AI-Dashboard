from sqlalchemy import create_engine
import pandas as pd

# Create a SQLAlchemy engine
engine = create_engine(
    "mssql+pyodbc://localhost\\SQLEXPRESS/AdventureWorks2022?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

query = "SELECT TOP 5 * FROM Person.Person"
df = pd.read_sql(query, engine)

print(df)
