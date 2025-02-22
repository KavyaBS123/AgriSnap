import streamlit as st
import plotly.express as px
from PIL import Image
import pandas as pd
from datetime import datetime
import time

# Import custom modules
from utils.image_processor import preprocess_image, enhance_image
from utils.mock_ml import MockClassifier
from utils.price_analyzer import PriceAnalyzer

# Page configuration
st.set_page_config(
    page_title="Agricultural Product Analyzer",
    page_icon="🌾",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'classifier' not in st.session_state:
    st.session_state.classifier = MockClassifier()
if 'price_analyzer' not in st.session_state:
    st.session_state.price_analyzer = PriceAnalyzer()

# Header
st.title("🌾 Agricultural Product Analyzer")
st.markdown("""
    Upload images of agricultural products to analyze their quality and track market prices.
    Our AI-powered system provides instant insights and historical price data.
""")

# Main layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Image Analysis")
    uploaded_file = st.file_uploader(
        "Upload an image of your agricultural product",
        type=['jpg', 'jpeg', 'png'],
        help="Supported formats: JPG, JPEG, PNG"
    )

    if uploaded_file:
        with st.spinner("Processing image..."):
            # Process image
            image = preprocess_image(uploaded_file)
            enhanced_image = enhance_image(image)
            
            # Display image
            st.image(enhanced_image, caption="Uploaded Image", use_column_width=True)
            
            # Analyze image
            results = st.session_state.classifier.analyze_image(image)
            
            # Display results
            st.markdown("### Analysis Results")
            results_col1, results_col2 = st.columns(2)
            
            with results_col1:
                st.metric("Product Type", results['product'])
                st.metric("Quality Grade", results['quality'])
            
            with results_col2:
                st.metric("Plant Health", results['disease'])
                st.metric("Confidence Score", f"{results['confidence']*100:.1f}%")
            
            # Get price data for detected product
            price_data = st.session_state.price_analyzer.get_price_statistics(results['product'])
            
            st.markdown("### Market Insights")
            price_col1, price_col2, price_col3 = st.columns(3)
            
            with price_col1:
                st.metric("Current Price", f"${price_data['current_price']}/kg")
            with price_col2:
                st.metric("30-Day Average", f"${price_data['average_price']}/kg")
            with price_col3:
                st.metric("Price Change", f"{price_data['price_change']}%")

with col2:
    st.subheader("Price Trends")
    if uploaded_file:
        # Get historical price data
        historical_data = st.session_state.price_analyzer.get_price_history(
            results['product'], days=90
        )
        
        # Create price trend chart
        fig = px.line(
            historical_data,
            x='date',
            y='price',
            title=f"{results['product']} Price Trend (90 Days)",
            labels={'date': 'Date', 'price': 'Price ($/kg)'}
        )
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Market recommendations
        st.markdown("### Market Recommendations")
        if price_data['price_change'] > 5:
            st.success("📈 Prices are trending upward - Consider selling")
        elif price_data['price_change'] < -5:
            st.warning("📉 Prices are trending downward - Consider holding")
        else:
            st.info("📊 Prices are stable - Monitor market conditions")
    else:
        st.info("Upload an image to view price trends and market insights")

# Footer
st.markdown("---")
st.markdown(
    "🌾 Agricultural Product Analyzer - Helping farmers make data-driven decisions"
)
