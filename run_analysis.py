# run_analysis.py
from src.analyzer import FundamentalsAnalyzer
import yfinance as yf

def main():
    # Initialize analyzer
    analyzer = FundamentalsAnalyzer()
    
    import requests
    from bs4 import BeautifulSoup
    import yfinance as yf
    import pandas as pd
    import os
    import time

    os.chdir("c:/Users/User/Documents/SmallCap_Finder/stock-fundamentals-analyzer")

    # Step 1: Scrape the list of Russell 2000 Tickers from Wikipedia
    data = pd.read_csv("data/raw/russell-2000-index-08-30-2025.csv")
    test_symbols = data['Symbol'].tolist()
    
    print("Analyzing companies...")
    results = analyzer.analyze_companies(test_symbols)
    print(results[['symbol', 'pe_ratio', 'roe', 'market_cap']].head())
    
    # Screen for small caps
    print("\nScreening for small caps...")
    small_caps = analyzer.screen_small_caps(test_symbols)
    print(f"Found {len(small_caps)} small cap opportunities")

if __name__ == "__main__":
    main()