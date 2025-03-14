import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State, dash_table

try:
    import micropip
except ModuleNotFoundError:
    raise ModuleNotFoundError("micropip module not found. Ensure you are running this in a compatible environment or install manually if necessary.")

# Ensure the file exists by checking different possible locations
file_path = "combined_health_nutrition_population_data_with_categories.xlsx"
if not os.path.exists(file_path):
    file_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Data file not found at {file_path}. Please ensure the file is in the correct directory, or provide the correct path."
        )

# Load the data with error handling
try:
    df = pd.read_excel(file_path)
except Exception as e:
    raise RuntimeError(f"Error loading the Excel file: {str(e)}")

# Clean the data
df_cleaned = df.dropna(subset=["Country Name", "Series Name", "Year", "Value", "wealth_quintiles", "Category"])
df_cleaned["Year"] = df_cleaned["Year"].astype(int)
df_cleaned["Value"] = pd.to_numeric(df_cleaned["Value"])

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
def layout():
    return html.Div([
        html.H1("Metrics by Wealth Quintiles", className="custom-title"),
        dcc.Tabs([
            dcc.Tab(label="Visualization", children=[
                html.Div([
                    html.Label("Select a Country:"),
                    dcc.Dropdown(
                        id="country",
                        options=[{"label": c, "value": c} for c in sorted(df_cleaned["Country Name"].unique())],
                        value=sorted(df_cleaned["Country Name"].unique())[0] if not df_cleaned.empty else None,
                        clearable=False
                    ),
                    html.Label("Select Categories:"),
                    dcc.Checklist(
                        id="category",
                        options=[{"label": c, "value": c} for c in sorted(df_cleaned["Category"].unique())],
                        value=[sorted(df_cleaned["Category"].unique())[0]] if not df_cleaned.empty else []
                    ),
                    html.Label("Metrics:"),
                    dcc.RadioItems(id="series"),
                    html.Label("Select Year Range:"),
                    dcc.RangeSlider(
                        id="year_range",
                        min=df_cleaned["Year"].min() if not df_cleaned.empty else 2000,
                        max=df_cleaned["Year"].max() if not df_cleaned.empty else 2025,
                        value=[df_cleaned["Year"].min(), df_cleaned["Year"].max()] if not df_cleaned.empty else [2000, 2025],
                        marks={year: str(year) for year in range(df_cleaned["Year"].min(), df_cleaned["Year"].max()+1, 5)} if not df_cleaned.empty else {}
                    ),
                    html.Label("Select Plot Type:"),
                    dcc.RadioItems(
                        id="plot_type",
                        options=[{"label": p, "value": p} for p in ["Line Plot", "Bar Plot", "Scatter Plot"]],
                        value="Line Plot"
                    ),
                    dcc.Checklist(
                        id="add_avg_line", options=[{"label": "Add Black Dotted Average Line", "value": "avg"}], value=[]
                    ),
                    html.Button("Reset Filters", id="reset_filters", n_clicks=0)
                ], style={"width": "25%", "display": "inline-block"}),
                html.Div([
                    dcc.Graph(id="plot")
                ], style={"width": "70%", "display": "inline-block"})
            ]),
            dcc.Tab(label="Statistics", children=[
                html.Button("Download CSV", id="download_button"),
                dcc.Download(id="download_data"),
                dash_table.DataTable(id="stats_table", page_size=10)
            ])
        ])
    ])

app.layout = layout()

if __name__ == "__main__":
    app.run_server(debug=True)
