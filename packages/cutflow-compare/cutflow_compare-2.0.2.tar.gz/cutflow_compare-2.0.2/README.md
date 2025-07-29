# cutflow_compare

## Overview
`cutflow_compare` is a Python package designed to compare cutflow histograms from ROOT files. It provides a straightforward command-line interface for users to analyze and visualize differences in cutflow data across different regions.

## Features
- Compare cutflow histograms from multiple ROOT files.
- Custom labels for each file using the `--labels` argument.
- Generate separate CSV reports for each region.
- Calculate relative errors and standard deviations across all files for each selection.
- Easy to use with command-line arguments for file input and region selection.

## Installation
You can install the package using pip:

```sh
pip install cutflow_compare
```

## Usage

After installation, you can use the command-line tool directly:

```sh
cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference
```

Or, if running from source:

```sh
python cutflow_compare.py --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference
```

### Note: 
Make sure the same regions are present in all files with the same name.

### Arguments
- `--files`: List of input ROOT files to compare. Required.
- `--regions`: List of regions to compare within the cutflow histograms. Required.
- `--labels`: Custom labels for each file, used in the output CSV. Optional.
- `--separate-selections`: Optional flag to keep selections separate instead of merging them.
- `--relative-error`: Optional flag to include relative error calculations in the output.

### Output
The tool generates **separate CSV files for each region** named `cutflow_comparison_{region}.csv`.  
Each CSV contains the comparison results for that specific region, with columns for each file and calculated relative errors when multiple files are compared.

## Example
```bash
cutflow_compare --files histoOut-compared.root histoOut-reference.root histoOut-third.root -r WZ ttbar --labels Compared Reference Third --relative-error
```

This command compares the specified regions (`WZ`, `ttbar`) in the three provided ROOT files. It outputs separate results to:
- `cutflow_comparison_WZ.csv`
- `cutflow_comparison_ttbar.csv`

Each file includes relative error and standard deviation calculations for each selection.

## Requirements

- Python 3.6+
- [ROOT](https://root.cern/) (must be installed separately, e.g., via conda: `conda install -c conda-forge root`)
- pandas (automatically installed with the package)
- uncertainties (automatically installed with the package)

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## Acknowledgments
This package utilizes the ROOT framework for data analysis and visualization.
