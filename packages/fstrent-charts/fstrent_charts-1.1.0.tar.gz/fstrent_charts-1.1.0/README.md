# FSTrent Colors and Charts

[![PyPI version](https://badge.fury.io/py/fstrent_charts.svg)](https://badge.fury.io/py/fstrent_charts)
[![Build Status](https://github.com/wrm3/fstrent_charts/actions/workflows/publish.yml/badge.svg)](https://github.com/wrm3/fstrent_charts/actions)
[![License](https://img.shields.io/github/license/wrm3/fstrent_charts)](https://github.com/wrm3/fstrent_charts/blob/main/LICENSE)

Enhanced terminal color and charting library providing extensive color combinations, charting utilities, and demos for Python applications.

## Features

- 🎨 16 Base colors (including light variants)
- 📊 Charting utilities for terminal display
- 🖼️ Background colors for all combinations
- 🌈 Color on color support (e.g., red text on blue background)
- 🛠️ Utility functions for string coloring
- 📝 Simple API for color and chart manipulation
- 🔧 Cross-platform support via colorama

## Installation

```bash
pip install fstrent_charts
```

## Basic Usage

```python
from fstrent_charts import (
    # Utility functions
    cs, cp,
    
    # Basic colors
    R, G, B, W  # Red, Green, Blue, White
)

# Print colored text
cp("This is red text", R)
cp("This is green text", G)
cp("This is blue text", B)

# Create colored strings
colored_text = cs("Custom colored text", B)
print(colored_text)
```

## Charting with FSTrent Charts

The `fstrent_charts` library provides utilities for creating and displaying charts in the terminal. Below are examples from the demo functions included in the library.

### Demo 1: Basic Chart

```python
from fstrent_charts import CHRT

chrt = CHRT()
title = "Basic Chart Example"
chrt.chart_top(in_str=title)
chrt.chart_row(in_str="This is a row in the chart", align='left', font_color='white', bg_color='blue')
chrt.chart_bottom()
```

### Demo 2: Market Collection

```python
from fstrent_charts import CHRT

chrt = CHRT()
title1 = "Sell Market Collection"
subtitle1 = "adding markets with open positions (44) :"

markets1 = [
    "POLS-USDC", "SUI-USDC", "POL-USDC", "FLOKI-USDC", "SHIB-USDC"
    # ... more markets
]

chrt.chart_top(in_str=title1)
chrt.chart_title(in_str=subtitle1)

for market in markets1:
    chrt.chart_row(in_str=market, align='left', font_color='white', bg_color='green')

chrt.chart_bottom()
```

### Demo 3: Opened Positions

```python
from fstrent_charts import CHRT

chrt = CHRT()
title = "Last 25 Opened Positions - Live"
headers = "mkt      | T | pos_id | strat    | freq | age  | open @ est | buy_val | buy_prc   | curr_prc  | high_prc  | gain_pct % | gain_top % | drop_pct % | gain_loss | gain_loss_high"

rows = [
    "MOBILE-USDC |   | 32919  | drop     | 1d   | 0    | 12-01-2024 | 3.000000 | 0.00151779| 0.00151400| 0.00151400| -0.20 %    | 0.00 %     | -0.10 %    | 0.00000000 | 0.02360239",
    # ... more rows
]

chrt.chart_top(in_str=title)
chrt.chart_headers(in_str=headers)

for row in rows:
    chrt.chart_row(in_str=row, align='left', font_color='white', bg_color='black')

chrt.chart_bottom()
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/wrm3/fstrent_charts.git
cd fstrent_charts
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## License

MIT License - see LICENSE file for details.

## Author

Warren R Martel III (wrmartel3@gmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
