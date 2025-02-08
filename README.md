# Dashboard_N_Project
# Chesapeake Bay Nitrogen Loss Dashboard

## Overview
This interactive **Dash web application** visualizes nitrogen loss across the **Chesapeake Bay agricultural supply chain** for the years **2017, 2030, and 2050**. The dashboard provides insights into **where and how nitrogen is lost**, **trade behavior**, and **crop and animal production trends** under future scenarios.

The model is based on research outlined in this [paper](https://www.DOI.org/10.1088/1748-9326/ad5d0b), supporting **USDA’s 2030 nitrogen reduction goals** by identifying key nitrogen loss hotspots and potential mitigation strategies.

## Features
- 📊 **Nitrogen Loss Visualization** – Interactive **choropleth maps** showing nitrogen loss across supply chain stages.
- 🔄 **Yearly Comparison (2017, 2030, 2050)** – Select different years and compare nitrogen loss trends.
- 🌍 **Trade Behavior Analysis** – Identify nitrogen movement across counties (import/export/within-county flows).
- 🌾 **Agricultural Production Trends** – Pie charts & tables summarizing **harvested area and inventory by commodity**.
- 📉 **Data Processing & Modeling** – **Machine learning (K-means clustering), ETL pipelines, and statistical analysis** applied for insights.

## Tech Stack
- **Python**: Data processing, modeling, and visualization.
- **Dash & Plotly**: Web-based interactive visualizations.
- **Pandas & NumPy**: Data wrangling and statistical computations.
- **Dash Bootstrap Components (DBC)**: UI enhancements.
- **GeoJSON & Plotly Choropleth Maps**: Spatial analysis & visualization.

## Installation
To set up and run the dashboard locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/chesapeake-nitrogen-dashboard.git
   cd chesapeake-nitrogen-dashboard
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```

5. Open the browser and navigate to **http://127.0.0.1:8050/**

## Project Structure
```
chesapeake-nitrogen-dashboard/
│── data/                  # Folder containing datasets for 2017, 2030, 2050
│── app.py                 # Main Dash application
│── requirements.txt       # Python dependencies
│── README.md              # Project documentation
│── assets/                # CSS, images, and external assets (if needed)
```

## Data Sources
The data used in this dashboard includes:
- **Nitrogen Loss Data**: Aggregated from **crop production, feed waste, livestock processing, food waste, and human nitrogen waste**.
- **USDA & EPA Climate Data**: Used to model future nitrogen loss scenarios.
- **NREL Renewable Energy Data**: Integrated for further energy-climate interactions (if applicable).

## Future Improvements
🚀 Potential enhancements include:
- **Performance optimization** with Dash caching & lazy loading.
- **More granular trade analysis** using network graphs.
- **Integration with live USDA/EPA APIs** for real-time data updates.

## License
This project is open-source under the **MIT License**.

## Author
👨‍💻 **Tarun Kumanduri**  
📧 tarun.kumanduri99@gmail.com 
🌐 https://www.linkedin.com/in/tarun-kumanduri

