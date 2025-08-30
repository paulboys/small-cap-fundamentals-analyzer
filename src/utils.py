import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import logging
from datetime import datetime, timedelta

def calculate_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate various financial ratios from raw financial data.
    
    Args:
        financial_data (Dict): Raw financial data
        
    Returns:
        Dict containing calculated ratios
    """
    ratios = {}
    
    try:
        # Price ratios
        if 'market_cap' in financial_data and 'revenue' in financial_data:
            ratios['price_to_sales'] = financial_data['market_cap'] / financial_data['revenue']
        
        if 'market_cap' in financial_data and 'net_income' in financial_data:
            if financial_data['net_income'] > 0:
                ratios['price_to_earnings'] = financial_data['market_cap'] / financial_data['net_income']
        
        if 'market_cap' in financial_data and 'book_value' in financial_data:
            ratios['price_to_book'] = financial_data['market_cap'] / financial_data['book_value']
        
        # Profitability ratios
        if 'net_income' in financial_data and 'revenue' in financial_data:
            ratios['net_profit_margin'] = financial_data['net_income'] / financial_data['revenue']
        
        if 'gross_profit' in financial_data and 'revenue' in financial_data:
            ratios['gross_profit_margin'] = financial_data['gross_profit'] / financial_data['revenue']
        
        if 'operating_income' in financial_data and 'revenue' in financial_data:
            ratios['operating_margin'] = financial_data['operating_income'] / financial_data['revenue']
        
        # Return ratios
        if 'net_income' in financial_data and 'total_equity' in financial_data:
            if financial_data['total_equity'] > 0:
                ratios['return_on_equity'] = financial_data['net_income'] / financial_data['total_equity']
        
        if 'net_income' in financial_data and 'total_assets' in financial_data:
            ratios['return_on_assets'] = financial_data['net_income'] / financial_data['total_assets']
        
        # Liquidity ratios
        if 'current_assets' in financial_data and 'current_liabilities' in financial_data:
            if financial_data['current_liabilities'] > 0:
                ratios['current_ratio'] = financial_data['current_assets'] / financial_data['current_liabilities']
        
        if 'quick_assets' in financial_data and 'current_liabilities' in financial_data:
            if financial_data['current_liabilities'] > 0:
                ratios['quick_ratio'] = financial_data['quick_assets'] / financial_data['current_liabilities']
        
        # Leverage ratios
        if 'total_debt' in financial_data and 'total_equity' in financial_data:
            if financial_data['total_equity'] > 0:
                ratios['debt_to_equity'] = financial_data['total_debt'] / financial_data['total_equity']
        
        if 'total_debt' in financial_data and 'total_assets' in financial_data:
            ratios['debt_to_assets'] = financial_data['total_debt'] / financial_data['total_assets']
        
    except (ZeroDivisionError, TypeError, KeyError) as e:
        logging.warning(f"Error calculating ratios: {e}")
    
    return ratios

def validate_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean financial data.
    
    Args:
        data (Dict): Raw financial data
        
    Returns:
        Dict containing validated data
    """
    validated_data = {}
    
    for key, value in data.items():
        try:
            # Handle None values
            if value is None:
                validated_data[key] = 0
                continue
            
            # Handle string numeric values
            if isinstance(value, str):
                try:
                    value = float(value.replace(',', '').replace('$', '').replace('%', ''))
                except ValueError:
                    validated_data[key] = 0
                    continue
            
            # Handle negative values for certain metrics
            if key in ['market_cap', 'revenue', 'total_assets'] and value < 0:
                validated_data[key] = 0
            else:
                validated_data[key] = float(value)
                
        except (ValueError, TypeError):
            validated_data[key] = 0
    
    return validated_data

def calculate_growth_rate(current_value: float, previous_value: float) -> float:
    """
    Calculate growth rate between two values.
    
    Args:
        current_value (float): Current period value
        previous_value (float): Previous period value
        
    Returns:
        Growth rate as percentage
    """
    if previous_value == 0:
        return 0.0
    
    return ((current_value - previous_value) / abs(previous_value)) * 100

def normalize_sector_name(sector: str) -> str:
    """
    Normalize sector names to standard format.
    
    Args:
        sector (str): Raw sector name
        
    Returns:
        Normalized sector name
    """
    sector_mapping = {
        'tech': 'Technology',
        'technology': 'Technology',
        'healthcare': 'Healthcare',
        'health care': 'Healthcare',
        'financial': 'Financial Services',
        'financials': 'Financial Services',
        'finance': 'Financial Services',
        'consumer discretionary': 'Consumer Discretionary',
        'consumer staples': 'Consumer Staples',
        'industrials': 'Industrial',
        'industrial': 'Industrial',
        'energy': 'Energy',
        'materials': 'Materials',
        'utilities': 'Utilities',
        'real estate': 'Real Estate',
        'communication services': 'Communication Services',
        'communications': 'Communication Services'
    }
    
    normalized = sector.lower().strip()
    return sector_mapping.get(normalized, sector.title())

def filter_outliers(data: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """
    Filter outliers from a DataFrame column.
    
    Args:
        data (DataFrame): Input data
        column (str): Column to filter
        method (str): Method to use ('iqr' or 'zscore')
        
    Returns:
        DataFrame with outliers removed
    """
    if method == 'iqr':
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
    
    elif method == 'zscore':
        z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
        return data[z_scores < 3]
    
    return data

def create_market_cap_buckets(market_cap: float) -> str:
    """
    Categorize stocks by market cap size.
    
    Args:
        market_cap (float): Market capitalization
        
    Returns:
        Market cap category
    """
    if market_cap < 300e6:  # Less than $300M
        return 'Micro-cap'
    elif market_cap < 2e9:  # Less than $2B
        return 'Small-cap'
    elif market_cap < 10e9:  # Less than $10B
        return 'Mid-cap'
    elif market_cap < 200e9:  # Less than $200B
        return 'Large-cap'
    else:
        return 'Mega-cap'

def calculate_composite_score(metrics: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """
    Calculate a composite score based on multiple metrics.
    
    Args:
        metrics (Dict): Financial metrics
        weights (Dict): Weights for each metric
        
    Returns:
        Composite score
    """
    if weights is None:
        weights = {
            'pe_ratio': -0.2,  # Lower is better
            'roe': 0.3,        # Higher is better
            'profit_margin': 0.25,
            'revenue_growth': 0.15,
            'debt_to_equity': -0.1  # Lower is better
        }
    
    score = 0
    total_weight = 0
    
    for metric, weight in weights.items():
        if metric in metrics and metrics[metric] is not None:
            value = metrics[metric]
            
            # Normalize certain metrics
            if metric == 'pe_ratio':
                # Convert P/E to score (lower is better, but not too low)
                if 5 <= value <= 25:
                    normalized_value = (25 - value) / 20
                else:
                    normalized_value = 0
            elif metric in ['roe', 'profit_margin']:
                # These are already in decimal form, multiply by 100 for percentage
                normalized_value = min(value * 100, 100) / 100
            elif metric == 'revenue_growth':
                # Cap growth at 100%
                normalized_value = min(max(value, -50), 100) / 100
            elif metric == 'debt_to_equity':
                # Lower is better, cap at 2
                normalized_value = max(0, (2 - min(value, 2)) / 2)
            else:
                normalized_value = value
            
            score += normalized_value * weight
            total_weight += abs(weight)
    
    return score / total_weight if total_weight > 0 else 0

def format_currency(amount: float) -> str:
    """
    Format a number as currency.
    
    Args:
        amount (float): Amount to format
        
    Returns:
        Formatted currency string
    """
    if amount >= 1e12:
        return f"${amount/1e12:.1f}T"
    elif amount >= 1e9:
        return f"${amount/1e9:.1f}B"
    elif amount >= 1e6:
        return f"${amount/1e6:.1f}M"
    elif amount >= 1e3:
        return f"${amount/1e3:.1f}K"
    else:
        return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """
    Format a decimal as percentage.
    
    Args:
        value (float): Decimal value
        
    Returns:
        Formatted percentage string
    """
    return f"{value*100:.2f}%"

def setup_logging(log_file: str = 'stock_analyzer.log') -> None:
    """
    Set up logging configuration.
    
    Args:
        log_file (str): Log file name
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
