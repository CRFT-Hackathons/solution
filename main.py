import pandas as pd

# Load the data
connections = pd.read_csv("resources/connections.csv", engine="pyarrow")
customers = pd.read_csv("resources/customers.csv", engine="pyarrow")
demands = pd.read_csv("resources/demands.csv", engine="pyarrow")
refineries = pd.read_csv("resources/refineries.csv", engine="pyarrow")
tanks = pd.read_csv("resources/tanks.csv", engine="pyarrow")
