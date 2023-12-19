# Project Title

This Python project is designed to convert TLOG files to CSV, process them, and then plot the data. It supports both TLOG and CSV file formats.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Python installed on your machine. The project also requires the following Python libraries:

- pandas
- argparse
- matplotlib
- os
- numpy
- pymavlink

You can install these using pip:

```bash
pip install pandas argparse matplotlib os numpy pymavlink
```

### Usage
The script can be run from the command line with the following arguments:

--path_4g: Path to the 4G TLOG file
--path_rf: Path to the RF TLOG file

Example:

```bash
python main.py --path_4g path_to_4g_file --path_rf path_to_rf_file
```
If the provided files are TLOG files, they will be converted to CSV. If they are already CSV files, they will be processed directly.

The script will then plot the data from the files.

## Output

The script generates two types of graphs from the processed data:

1. **Main Graph**: This graph plots the data from both the 4G and RF files. It provides a visual comparison of the two datasets.

2. **Histogram Graphs**: These are separate graphs for the 4G and RF data. They plot the frequency of the timestamp differences, providing a visual representation of the distribution of these differences.

The graphs are displayed using matplotlib's `plt.show()` function, which opens a new window with the graph. You can zoom in, pan, and save the graph as an image file using the toolbar provided by matplotlib.