import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure file exists
file_path = "combined_health_nutrition_population_data_with_categories.xlsx"
if not os.path.exists(file_path):
    st.error(f"Data file not found at {file_path}. Please upload the correct file.")
    st.stop()

# Load data
df = pd.read_excel(file_path).dropna(subset=["Country Name", "Series Name", "Year", "Value", "wealth_quintiles", "Category"])
df["Year"] = df["Year"].astype(int)
df["Value"] = pd.to_numeric(df["Value"])

# Streamlit UI
st.title("Metrics by Wealth Quintiles")

# Sidebar Filters
country = st.selectbox("Select a Country", sorted(df["Country Name"].unique()))
categories = st.multiselect("Select Categories", sorted(df["Category"].unique()), default=[df["Category"].unique()[0]])
series = st.selectbox("Select Metric", sorted(df["Series Name"].unique()))
year_range = st.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max())))
plot_type = st.radio("Select Plot Type", ["Line Plot", "Bar Plot", "Scatter Plot"])
add_avg = st.checkbox("Add Black Dotted Average Line")

# Filter Data
filtered_df = df[(df["Country Name"] == country) & (df["Category"].isin(categories)) & (df["Series Name"] == series) & (df["Year"].between(*year_range))]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # Plot Data
    if plot_type == "Line Plot":
        fig = px.line(filtered_df, x="Year", y="Value", color="wealth_quintiles", title=f"{country} - {series}")
    elif plot_type == "Bar Plot":
        fig = px.bar(filtered_df, x="Year", y="Value", color="wealth_quintiles", title=f"{country} - {series}")
    else:
        fig = px.scatter(filtered_df, x="Year", y="Value", color="wealth_quintiles", title=f"{country} - {series}")

    if add_avg:
        avg_df = filtered_df.groupby("Year")["Value"].mean().reset_index()
        fig.add_scatter(x=avg_df["Year"], y=avg_df["Value"], mode="lines", name="Average", line=dict(dash="dot", color="black"))

    st.plotly_chart(fig)

# Show Data Table
st.subheader("Statistics Table")
st.dataframe(filtered_df)

# CSV Download Button
st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")
