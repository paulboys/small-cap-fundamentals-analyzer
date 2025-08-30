import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os

class FinancialVisualizer:
    def __init__(self, style: str = 'seaborn'):
        """
        Initialize the FinancialVisualizer.
        
        Args:
            style (str): Matplotlib style to use
        """
        plt.style.use(style)
        sns.set_palette("husl")
        self.fig_size = (12, 8)
        
    def plot_sector_metrics(self, data: pd.DataFrame, sectors: List[str], metric: str) -> go.Figure:
        """
        Create a comparison plot of a specific metric across sectors.
        
        Args:
            data (DataFrame): Stock data
            sectors (List[str]): List of sectors to compare
            metric (str): Metric to plot
            
        Returns:
            Plotly figure object
        """
        sector_data = data[data['sector'].isin(sectors)]
        
        fig = px.box(sector_data, x='sector', y=metric, 
                     title=f'{metric.replace("_", " ").title()} by Sector',
                     color='sector')
        
        fig.update_layout(
            xaxis_title='Sector',
            yaxis_title=metric.replace('_', ' ').title(),
            height=500
        )
        
        return fig
    
    def create_company_dashboard(self, symbol: str, fundamentals: Dict[str, Any]) -> go.Figure:
        """
        Create a comprehensive dashboard for a single company.
        
        Args:
            symbol (str): Stock symbol
            fundamentals (Dict): Fundamental data
            
        Returns:
            Plotly figure with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Valuation Metrics', 'Profitability Metrics', 
                          'Financial Health', 'Growth Metrics'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Valuation metrics
        valuation_metrics = ['pe_ratio', 'pb_ratio', 'ps_ratio']
        valuation_values = [fundamentals.get(metric, 0) for metric in valuation_metrics]
        
        fig.add_trace(
            go.Bar(x=valuation_metrics, y=valuation_values, name='Valuation'),
            row=1, col=1
        )
        
        # Profitability metrics
        profit_metrics = ['profit_margin', 'operating_margin', 'roe']
        profit_values = [fundamentals.get(metric, 0) * 100 for metric in profit_metrics]  # Convert to percentage
        
        fig.add_trace(
            go.Bar(x=profit_metrics, y=profit_values, name='Profitability'),
            row=1, col=2
        )
        
        # Financial health
        health_metrics = ['current_ratio', 'debt_to_equity']
        health_values = [fundamentals.get(metric, 0) for metric in health_metrics]
        
        fig.add_trace(
            go.Bar(x=health_metrics, y=health_values, name='Financial Health'),
            row=2, col=1
        )
        
        # Growth metrics
        growth_metrics = ['revenue_growth']
        growth_values = [fundamentals.get(metric, 0)]
        
        fig.add_trace(
            go.Bar(x=growth_metrics, y=growth_values, name='Growth'),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f'{symbol} - Financial Dashboard',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def plot_screening_results(self, candidates: List[Dict[str, Any]]) -> go.Figure:
        """
        Visualize stock screening results.
        
        Args:
            candidates (List[Dict]): List of candidate stocks
            
        Returns:
            Plotly scatter plot
        """
        if not candidates:
            return go.Figure().add_annotation(text="No candidates found", 
                                            xref="paper", yref="paper",
                                            x=0.5, y=0.5, showarrow=False)
        
        df = pd.DataFrame(candidates)
        
        fig = px.scatter(df, x='pe_ratio', y='roe', 
                        size='market_cap', color='score',
                        hover_name='symbol',
                        title='Stock Screening Results',
                        labels={'pe_ratio': 'P/E Ratio', 'roe': 'ROE (%)'})
        
        fig.update_layout(height=500)
        
        return fig
    
    def create_correlation_heatmap(self, data: pd.DataFrame, metrics: List[str]) -> plt.Figure:
        """
        Create a correlation heatmap of financial metrics.
        
        Args:
            data (DataFrame): Stock data
            metrics (List[str]): List of metrics to include
            
        Returns:
            Matplotlib figure
        """
        correlation_data = data[metrics].corr()
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0,
                   square=True, ax=ax)
        
        ax.set_title('Financial Metrics Correlation Heatmap')
        plt.tight_layout()
        
        return fig
    
    def plot_historical_performance(self, symbol: str, historical_data: pd.DataFrame) -> go.Figure:
        """
        Plot historical stock price performance.
        
        Args:
            symbol (str): Stock symbol
            historical_data (DataFrame): Historical price data
            
        Returns:
            Plotly candlestick chart
        """
        fig = go.Figure(data=go.Candlestick(
            x=historical_data.index,
            open=historical_data['Open'],
            high=historical_data['High'],
            low=historical_data['Low'],
            close=historical_data['Close']
        ))
        
        fig.update_layout(
            title=f'{symbol} - Historical Price Performance',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            height=500
        )
        
        return fig
    
    def export_to_excel(self, data: pd.DataFrame, filename: str, 
                       charts: Optional[List[plt.Figure]] = None) -> None:
        """
        Export analysis results to Excel with optional charts.
        
        Args:
            data (DataFrame): Data to export
            filename (str): Output filename
            charts (List[Figure], optional): Charts to include
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write main data
            data.to_excel(writer, sheet_name='Analysis Results', index=False)
            
            # Add summary statistics
            summary = data.describe()
            summary.to_excel(writer, sheet_name='Summary Statistics')
            
            # If charts are provided, save them as images and reference in Excel
            if charts:
                chart_dir = filename.replace('.xlsx', '_charts')
                os.makedirs(chart_dir, exist_ok=True)
                
                chart_refs = []
                for i, chart in enumerate(charts):
                    chart_file = os.path.join(chart_dir, f'chart_{i+1}.png')
                    chart.savefig(chart_file, dpi=300, bbox_inches='tight')
                    chart_refs.append(chart_file)
                
                # Create a sheet with chart references
                chart_df = pd.DataFrame({'Chart_File': chart_refs})
                chart_df.to_excel(writer, sheet_name='Chart References', index=False)
        
        print(f"Analysis exported to {filename}")
    
    def create_sector_comparison_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        Create a comprehensive sector comparison chart.
        
        Args:
            data (DataFrame): Stock data with sector information
            
        Returns:
            Plotly figure with multiple metrics
        """
        sector_summary = data.groupby('sector').agg({
            'pe_ratio': 'mean',
            'roe': 'mean',
            'profit_margin': 'mean',
            'debt_to_equity': 'mean',
            'market_cap': 'median'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average P/E Ratio', 'Average ROE', 
                          'Average Profit Margin', 'Median Market Cap'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # P/E Ratio
        fig.add_trace(
            go.Bar(x=sector_summary['sector'], y=sector_summary['pe_ratio'], 
                   name='P/E Ratio'),
            row=1, col=1
        )
        
        # ROE
        fig.add_trace(
            go.Bar(x=sector_summary['sector'], y=sector_summary['roe'] * 100, 
                   name='ROE (%)'),
            row=1, col=2
        )
        
        # Profit Margin
        fig.add_trace(
            go.Bar(x=sector_summary['sector'], y=sector_summary['profit_margin'] * 100, 
                   name='Profit Margin (%)'),
            row=2, col=1
        )
        
        # Market Cap
        fig.add_trace(
            go.Bar(x=sector_summary['sector'], y=sector_summary['market_cap'] / 1e9, 
                   name='Market Cap ($B)'),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Sector Comparison Dashboard',
            height=600,
            showlegend=False
        )
        
        return fig