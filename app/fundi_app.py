
import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.analyzer import FundamentalsAnalyzer
from src.screener import SmallCapScreener
from src.visualizer import FinancialVisualizer
from src.data_extractor import DataExtractor
import time

# Page configuration
st.set_page_config(
    page_title="Stock Fundamentals Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def initialize_components():
    analyzer = FundamentalsAnalyzer()
    screener = SmallCapScreener()
    visualizer = FinancialVisualizer()
    extractor = DataExtractor()
    return analyzer, screener, visualizer, extractor

def main():
    st.title("📊 Stock Fundamentals Analyzer")
    st.markdown("**Identify undervalued small-cap investment opportunities**")
    
    # Initialize components
    analyzer, screener, visualizer, extractor = initialize_components()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "🔍 Stock Screener", "📈 Company Analysis", "🏢 Sector Comparison", "📊 Dashboard"]
    )
    
    if page == "🏠 Home":
        home_page()
    elif page == "🔍 Stock Screener":
        screener_page(screener, visualizer)
    elif page == "📈 Company Analysis":
        company_analysis_page(analyzer, visualizer)
    elif page == "🏢 Sector Comparison":
        sector_comparison_page(analyzer, visualizer)
    elif page == "📊 Dashboard":
        dashboard_page(analyzer, visualizer)

def home_page():
    st.header("Welcome to Stock Fundamentals Analyzer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔍 Stock Screening")
        st.write("Filter stocks based on fundamental criteria")
        st.write("• Market cap filters")
        st.write("• Financial ratios")
        st.write("• Sector-specific analysis")
    
    with col2:
        st.subheader("📈 Company Analysis")
        st.write("Deep dive into individual companies")
        st.write("• Fundamental metrics")
        st.write("• Financial health indicators")
        st.write("• Valuation analysis")
    
    with col3:
        st.subheader("📊 Visualizations")
        st.write("Interactive charts and dashboards")
        st.write("• Sector comparisons")
        st.write("• Performance metrics")
        st.write("• Screening results")
    
    st.markdown("---")
    st.info("💡 **Tip**: Start with the Stock Screener to find potential investment opportunities!")

def screener_page(screener, visualizer):
    st.header("🔍 Stock Screener")
    st.write("Filter small-cap stocks based on fundamental criteria")
    
    # Screening parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Screening Criteria")
        
        sector = st.selectbox(
            "Select Sector:",
            ["Healthcare", "Technology", "Financial Services", "Consumer Discretionary", 
             "Industrial", "Energy", "Materials", "Consumer Staples", "Utilities"]
        )
        
        max_market_cap = st.number_input(
            "Maximum Market Cap ($B):",
            min_value=0.1,
            max_value=10.0,
            value=2.0,
            step=0.1
        ) * 1e9
        
        min_revenue = st.number_input(
            "Minimum Revenue ($M):",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        ) * 1e6
    
    with col2:
        st.subheader("📊 Financial Ratios")
        
        max_pe_ratio = st.slider(
            "Maximum P/E Ratio:",
            min_value=5,
            max_value=30,
            value=18,
            step=1
        )
        
        min_roe = st.slider(
            "Minimum ROE (%):",
            min_value=5,
            max_value=25,
            value=12,
            step=1
        ) / 100
        
        max_debt_equity = st.slider(
            "Maximum Debt/Equity:",
            min_value=0.1,
            max_value=2.0,
            value=0.6,
            step=0.1
        )
    
    # Run screening
    if st.button("🔍 Run Screening", type="primary"):
        criteria = {
            'max_market_cap': max_market_cap,
            'min_revenue': min_revenue,
            'max_pe_ratio': max_pe_ratio,
            'min_roe': min_roe,
            'max_debt_equity': max_debt_equity
        }
        
        with st.spinner(f"Screening {sector} sector..."):
            try:
                candidates = screener.screen_by_criteria(sector, criteria)
                
                if candidates:
                    st.success(f"Found {len(candidates)} candidates!")
                    
                    # Display results table
                    df_results = pd.DataFrame(candidates)
                    st.subheader("📋 Screening Results")
                    
                    # Format the dataframe for display
                    display_df = df_results.copy()
                    display_df['market_cap'] = display_df['market_cap'].apply(lambda x: f"${x/1e9:.2f}B")
                    display_df['pe_ratio'] = display_df['pe_ratio'].round(2)
                    display_df['roe'] = (display_df['roe'] * 100).round(1)
                    display_df['profit_margin'] = (display_df['profit_margin'] * 100).round(1)
                    display_df['score'] = display_df['score'].round(1)
                    
                    st.dataframe(
                        display_df[['symbol', 'market_cap', 'pe_ratio', 'roe', 'profit_margin', 'score']],
                        column_config={
                            'symbol': 'Symbol',
                            'market_cap': 'Market Cap',
                            'pe_ratio': 'P/E Ratio',
                            'roe': 'ROE (%)',
                            'profit_margin': 'Profit Margin (%)',
                            'score': 'Score'
                        }
                    )
                    
                    # Visualization
                    fig = visualizer.plot_screening_results(candidates)
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.warning("No candidates found matching the criteria. Try adjusting the parameters.")
                    
            except Exception as e:
                st.error(f"Error during screening: {str(e)}")

def company_analysis_page(analyzer, visualizer):
    st.header("📈 Company Analysis")
    st.write("Analyze individual companies in detail")
    
    # Stock symbol input
    col1, col2 = st.columns([1, 3])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol:", value="AAPL", help="e.g., AAPL, GOOGL, MSFT").upper()
        
        if st.button("📊 Analyze Company", type="primary"):
            if symbol:
                with st.spinner(f"Analyzing {symbol}..."):
                    try:
                        fundamentals = analyzer.get_fundamentals(symbol)
                        
                        if fundamentals:
                            st.success(f"Analysis complete for {symbol}")
                            
                            # Company info
                            col_info1, col_info2, col_info3 = st.columns(3)
                            
                            with col_info1:
                                st.metric(
                                    "Market Cap",
                                    f"${fundamentals.get('market_cap', 0)/1e9:.2f}B"
                                )
                                st.metric(
                                    "P/E Ratio",
                                    f"{fundamentals.get('pe_ratio', 0):.2f}"
                                )
                            
                            with col_info2:
                                st.metric(
                                    "ROE",
                                    f"{fundamentals.get('roe', 0)*100:.1f}%"
                                )
                                st.metric(
                                    "Profit Margin",
                                    f"{fundamentals.get('profit_margin', 0)*100:.1f}%"
                                )
                            
                            with col_info3:
                                st.metric(
                                    "Debt/Equity",
                                    f"{fundamentals.get('debt_to_equity', 0):.2f}"
                                )
                                st.metric(
                                    "Revenue Growth",
                                    f"{fundamentals.get('revenue_growth', 0):.1f}%"
                                )
                            
                            # Company dashboard
                            with col2:
                                fig = visualizer.create_company_dashboard(symbol, fundamentals)
                                st.plotly_chart(fig, use_container_width=True)
                                
                        else:
                            st.error(f"Could not retrieve data for {symbol}")
                            
                    except Exception as e:
                        st.error(f"Error analyzing {symbol}: {str(e)}")

def sector_comparison_page(analyzer, visualizer):
    st.header("🏢 Sector Comparison")
    st.write("Compare performance across different sectors")
    
    # Sector selection
    sectors = ["Healthcare", "Technology", "Financial Services", "Consumer Discretionary", "Industrial"]
    selected_sectors = st.multiselect(
        "Select sectors to compare:",
        sectors,
        default=["Healthcare", "Technology"]
    )
    
    if st.button("📊 Compare Sectors", type="primary") and selected_sectors:
        with st.spinner("Analyzing sectors..."):
            try:
                # Generate sample data for demonstration
                sample_data = []
                for sector in selected_sectors:
                    symbols = screener._get_sample_symbols_by_sector(sector)[:5]  # Get first 5 symbols
                    for symbol in symbols:
                        fundamentals = analyzer.get_fundamentals(symbol)
                        if fundamentals:
                            sample_data.append(fundamentals)
                
                if sample_data:
                    df_data = pd.DataFrame(sample_data)
                    
                    # Filter for selected sectors
                    df_filtered = df_data[df_data['sector'].isin(selected_sectors)]
                    
                    if not df_filtered.empty:
                        # Sector comparison chart
                        fig = visualizer.create_sector_comparison_chart(df_filtered)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Summary statistics
                        st.subheader("📋 Sector Summary")
                        sector_summary = df_filtered.groupby('sector').agg({
                            'pe_ratio': 'mean',
                            'roe': 'mean',
                            'profit_margin': 'mean',
                            'market_cap': 'median'
                        }).round(2)
                        
                        st.dataframe(sector_summary)
                    else:
                        st.warning("No data available for the selected sectors")
                else:
                    st.warning("Could not retrieve sector data")
                    
            except Exception as e:
                st.error(f"Error in sector comparison: {str(e)}")

def dashboard_page(analyzer, visualizer):
    st.header("📊 Dashboard")
    st.write("Comprehensive view of market analysis")
    
    # Sample portfolio symbols
    portfolio_symbols = st.text_area(
        "Enter stock symbols (comma-separated):",
        value="AAPL,GOOGL,MSFT,JNJ,PFE",
        help="Enter stock symbols separated by commas"
    )
    
    if st.button("🚀 Generate Dashboard", type="primary"):
        symbols = [s.strip().upper() for s in portfolio_symbols.split(',') if s.strip()]
        
        if symbols:
            with st.spinner("Generating dashboard..."):
                try:
                    # Analyze portfolio
                    results = analyzer.analyze_companies(symbols)
                    
                    if not results.empty:
                        # Portfolio overview
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Companies", len(results))
                        with col2:
                            avg_pe = results['pe_ratio'].mean()
                            st.metric("Avg P/E", f"{avg_pe:.2f}")
                        with col3:
                            avg_roe = results['roe'].mean()
                            st.metric("Avg ROE", f"{avg_roe*100:.1f}%")
                        with col4:
                            total_market_cap = results['market_cap'].sum()
                            st.metric("Total Market Cap", f"${total_market_cap/1e12:.2f}T")
                        
                        # Portfolio composition chart
                        st.subheader("Portfolio Composition")
                        
                        # Market cap visualization
                        fig_pie = go.Figure(data=[go.Pie(
                            labels=results['symbol'],
                            values=results['market_cap'],
                            hole=0.3
                        )])
                        fig_pie.update_layout(title="Market Cap Distribution")
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Performance metrics
                        st.subheader("Performance Metrics")
                        metrics = ['pe_ratio', 'roe', 'profit_margin', 'debt_to_equity']
                        fig_metrics = visualizer.plot_sector_metrics(results, results['sector'].unique(), 'pe_ratio')
                        st.plotly_chart(fig_metrics, use_container_width=True)
                        
                        # Detailed table
                        st.subheader("Detailed Analysis")
                        display_results = results.copy()
                        display_results['market_cap'] = display_results['market_cap'].apply(lambda x: f"${x/1e9:.2f}B")
                        display_results['roe'] = (display_results['roe'] * 100).round(1)
                        display_results['profit_margin'] = (display_results['profit_margin'] * 100).round(1)
                        
                        st.dataframe(
                            display_results[['symbol', 'sector', 'market_cap', 'pe_ratio', 'roe', 'profit_margin']],
                            use_container_width=True
                        )
                        
                    else:
                        st.warning("No data available for the provided symbols")
                        
                except Exception as e:
                    st.error(f"Error generating dashboard: {str(e)}")

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Stock Fundamentals Analyzer v1.0**")
st.sidebar.markdown("*Educational use only - not financial advice*")

if __name__ == "__main__":
    main()