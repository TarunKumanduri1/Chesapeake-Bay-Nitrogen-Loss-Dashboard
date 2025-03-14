import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
import os

# Get the absolute path to the directory where the script is located
base_dir = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
    # Title
    html.H1(
        [
            html.Span("Impacts of Future Scenarios on Nitrogen Loss from Agricultural Supply Chains",
                      style={'display': 'block'}),
            html.Span("in the Chesapeake Bay",
                      style={'display': 'block'})
        ],
        style={'textAlign': 'center', 'fontWeight': 'bold'}
    ),

    # Text with hyperlink to paper
    html.P([
        "The Dashboard has been modeled based on this ",
        html.A("paper", href="https://www.DOI.org/10.1088/1748-9326/ad5d0b", target="_blank",
               style={'color': 'blue', 'textDecoration': 'underline'}),
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

    # Table of Contents
    html.H2("Contents", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'}),
    html.Ul([
        html.Li(html.Span("In What Stage Is Nitrogen Lost in the Food and Animal Supply Chain?",
                          style={'fontWeight': 'bold', 'fontSize': '18px'})),
        html.Li(html.Span("Where Does Nitrogen Loss Occur in the Chesapeake Bay?",
                          style={'fontWeight': 'bold', 'fontSize': '18px'})),
        html.Li(html.Span("What Are the Production Totals for Crops and Animals in the Chesapeake Bay?",
                          style={'fontWeight': 'bold', 'fontSize': '18px'}))
    ], style={'textAlign': 'center', 'listStyleType': 'none', 'padding': 0}),

    # Section 1: Nitrogen Loss Maps (Tabs)
    html.Div(id="chloropleth-maps"),

    # Section 1.1: Nitrogen Loss Table
    html.H2("Nitrogen Loss Table",
            style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '20px'}),
    html.Div(id="nitrogen-loss-table",
             style={'width': '80%', 'margin': '0 auto'}),

    # Section 2: Trade Behavior Maps (Tabs)
    html.Div(id="import-export-maps"),

    # Section 2.1: Trade Behavior Tables
    html.Div(id="import-export-tables",
             style={'width': '80%', 'margin': '0 auto'}),

    # Section 3: Inventory & Harvested Area (Tabs)
    html.Div(id="inventory-harvest-section")
], style={'padding': '20px'})



@app.callback(
    [
        Output("chloropleth-maps", "children"),  # Section 1: Nitrogen Loss Maps
        Output("nitrogen-loss-table", "children"),  # Section 1.1: Nitrogen Loss Table
        Output("import-export-tables", "children"),  # Section 2.1: Trade Behavior Tables
        Output("import-export-maps", "children"),  # Section 2: Trade Behavior Maps
        Output("inventory-harvest-section", "children")  # Section 3: Inventory & Harvested Area
    ],
    [Input("year-dropdown", "value")]
)
def update_dashboard_wrapper(selected_year):
    return update_dashboard(selected_year)

def update_dashboard(selected_year):
    # Load data
    nitrogen_df, area_df, inventory_df, crop_df, animal_df, total_nitrogen_df = load_data(selected_year)

    # Section 4: Nitrogen Loss Maps
    nitrogen_loss_section = html.H2("In What Stage Is Nitrogen Lost in the Food and Animal Supply Chain?",
                                    id="nitrogen-loss",
                                    style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'})

    nitrogen_loss_tabs = []
    for i, (col, label) in enumerate(nitrogen_loss_labels.items()):
        df = crop_df if i < 2 else animal_df
        title = f"<b>{label}</b>"  # Bolded Title for Visualization

        df[f"log_{col}"] = np.log1p(df[col])  # Log transformation

        fig = px.choropleth(
            df, geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            locations="FIPS", color=f"log_{col}", hover_name="county",
            hover_data={col: True},
            labels={f"log_{col}": "Log Nitrogen Loss"},  # Ensuring correct label
            title=title,  # Apply title
            color_continuous_scale="Viridis", scope="usa"
        )

        fig.update_layout(
            title={'text': title, 'x': 0.5, 'xanchor': 'center'},
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        fig.update_geos(fitbounds="locations")

        # Use the corresponding nitrogen loss title for the tab
        nitrogen_loss_tabs.append(dcc.Tab(label=label, children=[dcc.Graph(figure=fig)]))

    # Total Nitrogen Loss Map
    total_nitrogen_df["log_total_nitrogen_loss"] = np.log1p(total_nitrogen_df["total_nitrogen_loss"])

    total_loss_fig = px.choropleth(
        total_nitrogen_df,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="FIPS", color="log_total_nitrogen_loss", hover_name="county",
        hover_data={"total_nitrogen_loss": True},
        title="<b>Total Nitrogen Loss by County</b>",  # Bolded title
        labels={"log_total_nitrogen_loss": "Log Nitrogen Loss"},
        color_continuous_scale="Viridis", scope="usa"
    )

    total_loss_fig.update_layout(
        title={'text': "<b>Total Nitrogen Loss by County</b>", 'x': 0.5, 'xanchor': 'center'},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        paper_bgcolor="white", plot_bgcolor="white"
    )
    total_loss_fig.update_geos(fitbounds="locations")

    # Update tab label
    nitrogen_loss_tabs.append(dcc.Tab(label="Total Nitrogen Loss", children=[dcc.Graph(figure=total_loss_fig)]))

    # Nitrogen Loss Tabs Component
    nitrogen_loss_tabbed_maps = dcc.Tabs(children=nitrogen_loss_tabs, style={'marginTop': '20px'})
    maps = html.Div([nitrogen_loss_section, nitrogen_loss_tabbed_maps])

    # Section 5: Nitrogen Loss Table
    total_nitrogen_loss = round(
        crop_df[['nitrogen_loss1', 'nitrogen_loss2']].sum().sum() / 10 ** 6 +
        animal_df[['nitrogen_loss3', 'nitrogen_loss4', 'nitrogen_loss5', 'nitrogen_loss6', 'nitrogen_loss7']].sum().sum() / 10 ** 6,
        2
    )
    nitrogen_loss_table = pd.DataFrame({
        "Nitrogen Loss ID": [f"Nitrogen Loss Stage {i}" for i in range(1, 8)] + ["Total Nitrogen Loss"],
        "Nitrogen Loss Type": list(nitrogen_loss_labels.values()) + ["Total Nitrogen Loss"],
        "Total (K Tons)": (
                round(crop_df[['nitrogen_loss1', 'nitrogen_loss2']].sum().div(10 ** 6), 2).tolist() +
                round(animal_df[['nitrogen_loss3', 'nitrogen_loss4', 'nitrogen_loss5', 'nitrogen_loss6', 'nitrogen_loss7']].sum().div(10 ** 6), 2).tolist() +
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

    # Section 6: Where Does Nitrogen Loss Occur?
    nitrogen_loss_location_heading = html.H2("Where Does Nitrogen Loss Occur in the Chesapeake Bay?",
                                             id="trade-behavior",
                                             style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'})

    # Section 6: Where Does Nitrogen Loss Occur?
    nitrogen_loss_location_heading = html.H2(
        "Where Does Nitrogen Loss Occur in the Chesapeake Bay?",
        id="trade-behavior",
        style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'}
    )

    # Import/Export Tabs with Corresponding Tables
    import_export_sections = []
    for idx, stage in enumerate(["Crop Stage", "Live Animal Stage", "Animal Product Stage"]):
        stage_df = [crop_df, animal_df, animal_df][idx]
        columns = [
            ["import_crop_processing_nitrogen", "export_crop_processing_nitrogen",
             "within_county_crop_processing_nitrogen"],
            ["import_animal_nitrogen", "export_animal_nitrogen", "within_county_animal_nitrogen"],
            ["import_meat_nitrogen", "export_meat_nitrogen", "within_county_meat_nitrogen"]
        ][idx]

        # Section Heading (Centered)
        stage_heading = html.H3(
            stage,
            style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '30px'}
        )

        # List to store map tabs for Import/Export/Within County
        stage_tabs = []
        for col in columns:
            stage_df[f"log_{col}"] = np.log1p(stage_df[col])  # Log transformation

            fig = px.choropleth(
                stage_df, geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
                locations="FIPS", color=f"log_{col}", hover_name="county",
                hover_data={col: True}, title=f"<b>{col.replace('_', ' ').title()} - {stage}<b>",  # Bold Title
                color_continuous_scale="Viridis", scope="usa"
            )

            fig.update_layout(
                title={'text': f"<b>{col.replace('_', ' ').title()} - {stage}<b>", 'x': 0.5, 'xanchor': 'center'},
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                paper_bgcolor="white", plot_bgcolor="white"
            )

            fig.update_coloraxes(colorbar_title="Log Nitrogen Loss")
            fig.update_geos(fitbounds="locations")

            stage_tabs.append(dcc.Tab(label=col.replace('_', ' ').title(), children=[dcc.Graph(figure=fig)]))

        # Create Table for this Stage
        table_data = stage_df.groupby("commodity")[[columns[0], columns[1], columns[2]]].sum().reset_index()

        # Convert values to millions and round to 2 decimal places
        table_data[columns] = round(table_data[columns].div(10 ** 6), 2)

        # Format commodity names
        table_data["commodity"] = table_data["commodity"].str.title().str.replace('_', ' ')

        # Rename columns for clarity
        table_data.columns = ["Commodity", "Import (K Tons)", "Export (K Tons)", "Within County (K Tons)"]

        # Create Dash DataTable
        stage_table = dash_table.DataTable(
            data=table_data.to_dict("records"),
            columns=[{"name": col, "id": col} for col in table_data.columns],
            style_header={'fontWeight': 'bold', 'textAlign': 'center'},
            style_cell={'textAlign': 'center'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(248, 248, 248, 0.9)'}]
        )

        # Wrap everything for this stage inside a div
        stage_section = html.Div([
            stage_heading,
            dcc.Tabs(children=stage_tabs),
            html.Br(),
            html.Div(stage_table, style={'width': '80%', 'margin': '0 auto'})  # Centered Table
        ], style={'padding': '20px'})

        import_export_sections.append(stage_section)

    # Wrap all sections inside a container
    import_export_content = html.Div(
        [nitrogen_loss_location_heading] + import_export_sections,
        style={'width': '90%', 'margin': '0 auto'}
    )

    # Section 7: Production Totals (Inventory & Harvested Area)
    production_totals_heading = html.H2("What Are the Production Totals for Crops and Animals in the Chesapeake Bay?",
                                        id="area-inventory",
                                        style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '40px'})

    # Ensure "Commodity" column is formatted properly
    if "Commodity" in inventory_df.columns:
        inventory_df["Commodity"] = inventory_df["Commodity"].str.title().str.replace("_", " ")
    if "Commodity" in area_df.columns:
        area_df["Commodity"] = area_df["Commodity"].str.title().str.replace("_", " ")

    # Define consistent color scheme
    viridis_colors = px.colors.sequential.Viridis

    # Inventory Pie Chart
    inventory_chart = px.pie(
        inventory_df,
        names="Commodity",
        values="Total Inventory (head)",
        title="<b>Inventory by Commodity<b>"
    )
    inventory_chart.update_traces(marker=dict(colors=viridis_colors))

    # Harvested Area Pie Chart
    area_chart = px.pie(
        area_df,
        names="Commodity",
        values="Total Harvested Area (Acre)",
        title="<b> Harvested Area by Commodity <b>"
    )
    area_chart.update_traces(marker=dict(colors=viridis_colors))

    # Round values for better readability
    area_df = area_df.round(2)
    inventory_df = inventory_df.round(2)

    # Create Inventory table
    inventory_table = dash_table.DataTable(
        data=inventory_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in inventory_df.columns],
        style_header={'fontWeight': 'bold', 'textAlign': 'center'},
        style_cell={'textAlign': 'center'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(248, 248, 248, 0.9)'}]
    )

    # Create Harvested Area table
    area_table = dash_table.DataTable(
        data=area_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in area_df.columns],
        style_header={'fontWeight': 'bold', 'textAlign': 'center'},
        style_cell={'textAlign': 'center'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(248, 248, 248, 0.9)'}]
    )

    # Inventory & Harvested Area Section (Tabs)
    inventory_harvest_section = html.Div([
        production_totals_heading,
        dcc.Tabs(children=[
            dcc.Tab(label="Inventory", children=[
                dcc.Graph(figure=inventory_chart, style={'width': '70%', 'margin': '0 auto'}),
                html.Br(),
                inventory_table
            ]),
            dcc.Tab(label="Harvested Area", children=[
                dcc.Graph(figure=area_chart, style={'width': '70%', 'margin': '0 auto'}),
                html.Br(),
                area_table
            ])
        ])
    ])

    return maps, nitrogen_loss_table_component, import_export_content, [], inventory_harvest_section


if __name__ == "__main__":
    app.run_server(debug=True)
