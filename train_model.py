import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Load data
df = pd.read_csv("data/sales.csv")

# Convert Date
df['Date'] = pd.to_datetime(df['Date'])
df['Day'] = df['Date'].dt.day
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year

# Convert Product (A=0, B=1)
df['Product'] = df['Product'].map({'A': 0, 'B': 1})

# Features
X = df[['Store', 'Product', 'Customers', 'Promo', 'Holiday', 'Day', 'Month', 'Year']]
y = df['Sales']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
pickle.dump(model, open("model/model.pkl", "wb"))

print("✅ Model trained successfully")