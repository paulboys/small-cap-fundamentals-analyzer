# Stock Fundamentals Analyzer

A Python-based tool for extracting, analyzing, and visualizing business fundamentals to identify undervalued small-cap companies across different sectors.

## Features

- Extract key financial metrics from Yahoo Finance (yfinance)
- Analyze fundamental indicators: Revenue, Sales, P/E Ratio, EPS, Profit Margins
- Sector-based analysis and comparison
- Interactive visualizations and dashboards
- Screening for undervalued small-cap opportunities
- Export capabilities for further analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stock-fundamentals-analyzer.git
cd stock-fundamentals-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from src.analyzer import FundamentalsAnalyzer
from src.screener import SmallCapScreener

# Initialize analyzer
analyzer = FundamentalsAnalyzer()

# Screen for small-cap opportunities in healthcare sector
screener = SmallCapScreener()
candidates = screener.screen_sector('Healthcare', max_market_cap=2e9)

# Analyze fundamentals
results = analyzer.analyze_companies(candidates)

# Generate visualizations
analyzer.create_sector_comparison(results, 'Healthcare')
```

## Project Structure

```
stock-fundamentals-analyzer/
├── src/
│   ├── __init__.py
│   ├── data_extractor.py      # Yahoo Finance data extraction
│   ├── analyzer.py            # Fundamental analysis logic
│   ├── screener.py            # Stock screening algorithms
│   ├── visualizer.py          # Chart and graph generation
│   └── utils.py               # Helper functions
├── notebooks/
│   ├── exploration.ipynb      # Data exploration
│   ├── sector_analysis.ipynb  # Sector-specific analysis
│   └── screening_demo.ipynb   # Screening demonstration
├── data/
│   ├── raw/                   # Raw data cache
│   ├── processed/             # Processed datasets
│   └── sectors/               # Sector classification data
├── tests/
│   ├── test_extractor.py
│   ├── test_analyzer.py
│   └── test_screener.py
├── config/
│   └── config.yaml            # Configuration settings
├── requirements.txt
├── setup.py
└── README.md
```

## Key Metrics Analyzed

### Financial Health Indicators
- **Revenue Growth**: Year-over-year revenue trends
- **Profit Margins**: Gross, operating, and net margins
- **Earnings Per Share (EPS)**: Basic and diluted EPS
- **Price-to-Earnings (P/E) Ratio**: Current and forward P/E
- **Return on Equity (ROE)**: Efficiency of equity usage
- **Debt-to-Equity Ratio**: Financial leverage assessment

### Valuation Metrics
- **Price-to-Book (P/B) Ratio**: Asset valuation
- **Price-to-Sales (P/S) Ratio**: Revenue multiple
- **Enterprise Value ratios**: EV/Revenue, EV/EBITDA
- **Free Cash Flow**: Operating cash flow analysis

## Usage Examples

### 1. Basic Fundamental Analysis
```python
from src.analyzer import FundamentalsAnalyzer

analyzer = FundamentalsAnalyzer()

# Analyze a single company
fundamentals = analyzer.get_fundamentals('AAPL')
print(f"P/E Ratio: {fundamentals['pe_ratio']}")
print(f"Revenue Growth: {fundamentals['revenue_growth']}%")

# Analyze multiple companies
companies = ['AAPL', 'GOOGL', 'MSFT']
comparison = analyzer.compare_companies(companies)
```

### 2. Small-Cap Screening
```python
from src.screener import SmallCapScreener

screener = SmallCapScreener()

# Screen healthcare small-caps
criteria = {
    'max_market_cap': 2e9,  # $2B max
    'min_revenue': 100e6,   # $100M min revenue
    'max_pe_ratio': 15,     # P/E < 15
    'min_roe': 0.10,        # ROE > 10%
    'max_debt_equity': 0.5  # D/E < 0.5
}

candidates = screener.screen_by_criteria('Healthcare', criteria)
```

## Testing
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/

# Run specific test file
python -m pytest tests/test_analyzer.py -v
```

## License
MIT License - see LICENSE file for details

**Disclaimer**: This tool is for educational and research purposes only. It does not constitute financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.