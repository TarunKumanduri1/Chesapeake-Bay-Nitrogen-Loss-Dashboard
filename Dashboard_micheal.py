import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_table
import os

# Get the absolute path to the directory where the script is located
base_dir = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Define data paths relative to the script's directory
data_paths = {
    '2017': os.path.join(base_dir, 'data', '2017'),
    '2030': os.path.join(base_dir, 'data', '2030'),
    '2050': os.path.join(base_dir, 'data', '2050'),
}


# Nitrogen loss categories with descriptions
nitrogen_loss_labels = {
    'nitrogen_loss1': 'N input not taken by crop',
    'nitrogen_loss2': 'Crop processing N loss',
    'nitrogen_loss3': 'Feed waste & manure loss',
    'nitrogen_loss4': 'Slaughtering/milking/laying N loss',
    'nitrogen_loss5': 'Food processing N loss',
    'nitrogen_loss6': 'Food N waste',
    'nitrogen_loss7': 'Human N waste'
}


# Function to load data based on selected year
def load_data(year):
    path = data_paths[year]
    # Reading CSV files with os.path.join
    nitrogen_df = pd.read_csv(os.path.join(path, 'nitrogen_losses_summary.csv'))
    area_df = pd.read_csv(os.path.join(path, 'harvested_area_by_commodity.csv'))
    inventory_df = pd.read_csv(os.path.join(path, 'inventory_by_commodity.csv'))
    crop_processing_nitrogen_df = pd.read_csv(os.path.join(path, 'crop_processing_nitrogen.csv'))
    animal_stage_nitrogen_df = pd.read_csv(os.path.join(path, 'animal_stage_nitrogen.csv'))
    # Rename columns in crop_processing_nitrogen_df
    crop_processing_nitrogen_df.columns = [
        col.replace("selfloop", "within_county") if col.startswith("selfloop") else col
        for col in crop_processing_nitrogen_df.columns
    ]

    # Rename columns in animal_stage_nitrogen_df
    animal_stage_nitrogen_df.columns = [
        col.replace("selfloop", "within_county") if col.startswith("selfloop") else col
        for col in animal_stage_nitrogen_df.columns
    ]
    # Calculate total nitrogen loss for each DataFrame by summing specified columns
    crop_processing_nitrogen_df['total_nitrogen_loss'] = crop_processing_nitrogen_df[
        ['nitrogen_loss1', 'nitrogen_loss2']
    ].sum(axis=1)

    animal_stage_nitrogen_df['total_nitrogen_loss'] = animal_stage_nitrogen_df[
        ['nitrogen_loss3', 'nitrogen_loss4', 'nitrogen_loss5', 'nitrogen_loss6', 'nitrogen_loss7']
    ].sum(axis=1)

    # Combine the total nitrogen loss from both dataframes if necessary
    total_nitrogen_df = pd.concat([
        crop_processing_nitrogen_df[['FIPS', 'county', 'total_nitrogen_loss']],
        animal_stage_nitrogen_df[['FIPS', 'county', 'total_nitrogen_loss']]
    ]).groupby('FIPS').agg({
        'total_nitrogen_loss': 'sum',  # Sum the nitrogen loss
        'county': 'first'  # Keep the first non-null value of the county name
    }).reset_index()

    return nitrogen_df, area_df, inventory_df, crop_processing_nitrogen_df, animal_stage_nitrogen_df, total_nitrogen_df


app.layout = html.Div([
    html.H1(
        [
            html.Span("Impacts of Future Scenarios on Nitrogen Loss from Agricultural Supply Chains", style={'display': 'block'}),
            html.Span("in the Chesapeake Bay", style={'display': 'block'})
        ],
        style={'textAlign': 'center', 'fontWeight': 'bold'}
    ),
    # Text with hyperlink on the word "paper"
    html.P([
        "The Dashboard has been modeled based on this ",
        html.A("paper", href="https://www.DOI.org/10.1088/1748-9326/ad5d0b", target="_blank", style={'color': 'blue', 'textDecoration': 'underline'}),
        "."
    ], style={'textAlign': 'center', 'fontSize': '16px', 'marginTop': '20px'}),
    # Dropdown for Year Selection
    html.Label(
        'Select Year',
        style={'fontWeight': 'bold', 'textAlign': 'center', 'display': 'block', 'marginTop': '20px'}
    ),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in data_paths.keys()],
        value='2017',
        style={'width': '50%', 'margin': '0 auto'}
    ),

    # Contents Section with bold text titles
    html.H2("Contents", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'}),
    html.Ul([
        html.Li(html.Span("In What Stage Is Nitrogen Lost in the Food and Animal Supply Chain?",
                          style={'fontWeight': 'bold', 'fontSize': '18px'})),
        html.Li(html.Span("Where Does Nitrogen Loss Occur in the Chesapeake Bay?",
                          style={'fontWeight': 'bold', 'fontSize': '18px'})),
        html.Li(html.Span("What Are the Production Totals for Crops and Animals in the Chesapeake Bay?",
                          style={'fontWeight': 'bold', 'fontSize': '18px'}))
    ], style={'textAlign': 'center', 'listStyleType': 'none', 'padding': 0}),

    # Section 1: Nitrogen Loss
    html.H2("In What Stage Is Nitrogen Lost in the Food and Animal Supply Chain?",
            id="nitrogen-loss", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'}),
    html.Div(id="chloropleth-maps"),

    # Nitrogen Loss Table
    html.H2("Nitrogen Loss Table", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '20px'}),
    html.Div(id="nitrogen-loss-table", style={'width': '80%', 'margin': '0 auto'}),

    # Section 2: Trade Behavior
    html.H2("Where Does Nitrogen Loss Occur in the Chesapeake Bay?",
            id="trade-behavior", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'}),
    html.Div(id="import-export-maps"),

    # Trade Behavior Tables
    html.Div(id="import-export-tables", style={'width': '80%', 'margin': '0 auto'}),

    # Section 3: Area and Inventory
    html.H2("What Are the Production Totals for Crops and Animals in the Chesapeake Bay?",
            id="area-inventory", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'}),
    html.Div(id="inventory-harvest-section")
], style={'padding': '20px'})



@app.callback(
    [
        Output("chloropleth-maps", "children"),
        Output("nitrogen-loss-table", "children"),
        Output("import-export-tables", "children"),
        Output("import-export-maps", "children"),
        Output("inventory-harvest-section", "children")
    ],
    [Input("year-dropdown", "value")]
)
def update_dashboard(selected_year):
    # Load data
    nitrogen_df, area_df, inventory_df, crop_df, animal_df, total_nitrogen_df = load_data(selected_year)

    # Nitrogen loss maps
    maps = []
    for i, (col, label) in enumerate(nitrogen_loss_labels.items()):
        df = crop_df if i < 2 else animal_df
        title = f"Nitrogen Loss Stage {i + 1}: {label}"
        df[f"log_{col}"] = np.log1p(df[col])  # Log-transform the column for color scale
        fig = px.choropleth(
            df,
            geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            locations="FIPS",
            color=f"log_{col}",
            hover_name="county",
            hover_data={
                col: True  # Show original (non-logarithmic) nitrogen loss
            },
            labels={f"log_{col}": "Log Nitrogen Loss"},
            title=title,
            color_continuous_scale="Viridis",
            scope="usa"
        )
        fig.update_layout(
            title={'text': title, 'x': 0.5, 'xanchor': 'center'},
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        fig.update_geos(fitbounds="locations")
        maps.append(dcc.Graph(figure=fig, style={'display': 'inline-block', 'width': '50%'}))
    # Total nitrogen loss map with log scale
    total_nitrogen_df["log_total_nitrogen_loss"] = np.log1p(total_nitrogen_df["total_nitrogen_loss"])

    total_loss_fig = px.choropleth(
        total_nitrogen_df,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="FIPS",
        color="log_total_nitrogen_loss",
        hover_name="county",
        hover_data={
                "total_nitrogen_loss": True  # Show original (non-logarithmic) nitrogen loss
            },
        labels={f"log_total_nitrogen_loss": "Log Nitrogen Loss"},
        title="Total Nitrogen Loss by County",
        color_continuous_scale="Viridis",
        scope="usa"
    )
    total_loss_fig.update_layout(
        title={'text': "Total Nitrogen Loss by County", 'x': 0.5, 'xanchor': 'center',
               'font': {'size': 20, 'color': 'black', 'family': 'Arial, sans-serif', 'weight': 'bold'}},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    total_loss_fig.update_geos(fitbounds="locations")
    maps.append(dcc.Graph(figure=total_loss_fig, style={'display': 'inline-block', 'width': '50%'}))

    # Total nitrogen loss table with rounding
    total_nitrogen_loss = round(
        crop_df[['nitrogen_loss1', 'nitrogen_loss2']].sum().sum() / 10 ** 6 +
        animal_df[['nitrogen_loss3', 'nitrogen_loss4', 'nitrogen_loss5', 'nitrogen_loss6',
                   'nitrogen_loss7']].sum().sum() / 10 ** 6
    , 2)
    nitrogen_loss_table = pd.DataFrame({
        "Nitrogen Loss ID": [f"Nitrogen Loss Stage {i}" for i in range(1, 8)] + ["Total Nitrogen Loss"],
        "Nitrogen Loss Type": [label for _, label in nitrogen_loss_labels.items()] + ["Total Nitrogen Loss"],
        "Total (K Tons)": (
                round(crop_df[['nitrogen_loss1', 'nitrogen_loss2']].sum().div(10 ** 6), 2).tolist() +
                round(animal_df[['nitrogen_loss3', 'nitrogen_loss4', 'nitrogen_loss5', 'nitrogen_loss6',
                           'nitrogen_loss7']].sum().div(10 ** 6), 2).tolist() +
                [total_nitrogen_loss]
        )
    })

    nitrogen_loss_table_component = dash_table.DataTable(
        data=nitrogen_loss_table.to_dict("records"),
        columns=[{"name": col, "id": col} for col in nitrogen_loss_table.columns],
        style_header={'fontWeight': 'bold', 'textAlign': 'center'},
        style_cell={'textAlign': 'center'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(248, 248, 248, 0.9)'}]
    )

    # Stage maps and tables
    stage_names = ["Crop Processing", "Animal Nitrogen", "Meat Nitrogen"]
    stage_dfs = [crop_df, animal_df, animal_df]
    stage_columns = [
        ["import_crop_processing_nitrogen", "export_crop_processing_nitrogen", "within_county_crop_processing_nitrogen"],
        ["import_animal_nitrogen", "export_animal_nitrogen", "within_county_animal_nitrogen"],
        ["import_meat_nitrogen", "export_meat_nitrogen", "within_county_meat_nitrogen"]
    ]

    import_export_sections = []
    for idx, stage in enumerate(stage_names):
        stage_df = stage_dfs[idx]
        columns = stage_columns[idx]
        stage_maps = []
        for col in columns:
            # Apply log transformation and add a new column with log values
            stage_df[f"log_{col}"] = np.log1p(stage_df[col])  # log1p to avoid log(0) issues

            fig = px.choropleth(
                stage_df,
                geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
                locations="FIPS",
                color=f"log_{col}",  # Use log-transformed column for color
                hover_name="county",
                hover_data={
                    col: True  # Show original (non-logarithmic) nitrogen loss
                },
                labels={f"log_{col}": "Log Nitrogen"},
                title=f"{col.replace('_', ' ').title()} - {stage}",
                color_continuous_scale="Viridis",
                scope="usa"
            )

            fig.update_layout(
                title={'text': col.replace('_', ' ').title(), 'x': 0.5, 'xanchor': 'center'},
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                paper_bgcolor="white",
                plot_bgcolor="white"
            )

            # Set legend title to log_nitrogen
            fig.update_coloraxes(colorbar_title="log_nitrogen")
            fig.update_geos(fitbounds="locations")

            stage_maps.append(dcc.Graph(figure=fig, style={'display': 'inline-block', 'width': '50%'}))

        # Group by commodity and sum the specified columns
        table_data = stage_df.groupby("commodity")[[columns[0], columns[1], columns[2]]].sum().reset_index()

        # Convert values to millions and round
        table_data[columns] = round(table_data[columns].div(10 ** 6), 2)

        # Format commodity names to title case and remove underscores
        table_data["commodity"] = table_data["commodity"].str.title().str.replace('_', ' ')

        # Rename columns for clarity
        table_data.columns = ["Commodity", "Import (K Tons)", "Export (K Tons)", "Within County (K Tons)"]

        stage_table = dash_table.DataTable(
            data=table_data.to_dict("records"),
            columns=[{"name": col, "id": col} for col in table_data.columns],
            style_header={'fontWeight': 'bold', 'textAlign': 'center'},
            style_cell={'textAlign': 'center'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(248, 248, 248, 0.9)'}]
        )

        import_export_sections.append(html.Div(children=stage_maps + [stage_table], style={'padding': '10px'}))

    # Inventory and area charts
     # Apply formatting to the "Commodity" column in inventory_df
    if "Commodity" in inventory_df.columns:
        inventory_df["Commodity"] = inventory_df["Commodity"].str.title().str.replace("_", " ")

    # Apply formatting to the "Commodity" column in area_df
    if "Commodity" in area_df.columns:
        area_df["Commodity"] = area_df["Commodity"].str.title().str.replace("_", " ")
    plasma_colors = px.colors.sequential.Viridis
    inventory_chart = px.pie(inventory_df, names="Commodity", values="Total Inventory (head)",
                             title="Inventory by Commodity")
    inventory_chart.update_traces(marker=dict(colors=plasma_colors))
    area_chart = px.pie(area_df, names="Commodity", values="Total Harvested Area (Acre)",
                        title="Harvested Area by Commodity")
    area_chart.update_traces(marker=dict(colors=plasma_colors))

    # Round values in area_df and inventory_df to 2 decimal places
    area_df = area_df.round()
    inventory_df = inventory_df.round()

    # Create the Inventory table
    inventory_table = dash_table.DataTable(
        data=inventory_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in inventory_df.columns]
    )

    # Create the Harvested Area table
    area_table = dash_table.DataTable(
        data=area_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in area_df.columns]
    )

    inventory_harvest_section = html.Div([
        html.Div([
            dcc.Graph(figure=inventory_chart, style={'width': '50%'}),
            dcc.Graph(figure=area_chart, style={'width': '50%'})
        ], style={'display': 'flex'}),
        html.Div([
            html.Div(inventory_table, style={'width': '50%', 'padding': '10px'}),
            html.Div(area_table, style={'width': '50%', 'padding': '10px'})
        ], style={'display': 'flex', 'width': '100%'})
    ])

    return (
        maps,
        nitrogen_loss_table_component,
        import_export_sections,
        [],
        inventory_harvest_section
    )


if __name__ == "__main__":
    app.run_server(debug=True)
