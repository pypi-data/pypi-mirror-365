# AESB: Advanced Energy Storage Analytics

`aesb` is a Python package for fetching, processing, analyzing, and visualizing battery cell data from various manufacturing databases. It is designed to help engineers and data scientists monitor battery quality, identify anomalies, and understand cell behavior.

## Key Features

- **Data Fetching:**
    - Connects to multiple database systems (MySQL, Doris) to retrieve battery cell data.
    - Fetches data based on cell IDs, date ranges, or specific manufacturing processes (CP).
    - Retrieves detailed FTP curve data for in-depth analysis.
    - Handles data from different manufacturing bases (e.g., 'jy', 'sy', 'ordos').
- **Data Processing:**
    - Removes rework data to ensure analysis is based on first-pass results.
    - Enriches data with defect information.
    - Calculates dQ/dV, a key metric for battery health analysis.
- **Data Visualization:**
    - Generates various plots to visualize cell characteristics and compare them with their peers.
    - Analyzes and plots feature distributions to identify outliers.
    - Visualizes FTP curves to understand charging and discharging behavior.
- **Data Management:**
    - Provides a unified `BatteryDataManager` class to streamline data operations.
    - Allows uploading processed data back to a database.
    - Enables marking cells with defect codes directly through an API.

## Installation

To install the project, you can use pip:

```bash
pip install .
```

## Usage

To use the project, you can import the package and use the `BatteryDataManager` class:

```python
from aesb import BatteryDataManager

# Initialize the data manager for a specific manufacturing base and line
dm = BatteryDataManager(base='jy', wip_line='JYP1')

# Get data for a list of cell IDs
cell_data = dm.get_data_by_cell_ids(['cell_id_1', 'cell_id_2'], cp_names=['CAP', 'FOR'])

# Get FTP curve data for a cell
curve_data = dm.get_curves_by_cell_ids(['cell_id_1'], proc='CAP')

# Analyze a cell and visualize its characteristics
dm.analyze_cell_cp('cell_id_1')
```

## Development

To set up the development environment, first create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Then, install the dependencies:

```bash
pip install -r requirements.txt
```

To run the tests:

```bash
python3 -m pytest
```