import streamlit as st
import plotly.express as px
from PIL import Image
import pandas as pd
from datetime import datetime
import time
import io

# Import custom modules
from utils.image_processor import preprocess_image, enhance_image
from utils.mock_ml import MockClassifier
from utils.price_analyzer import PriceAnalyzer
from utils.price_predictor import PricePredictor

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
if 'price_predictor' not in st.session_state:
    st.session_state.price_predictor = PricePredictor()

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

    # Add file size limit warning
    st.info("Maximum file size: 200MB. Supported formats: JPG, JPEG, PNG")

    try:
        uploaded_file = st.file_uploader(
            "Upload an image of your agricultural product",
            type=['jpg', 'jpeg', 'png'],
            help="Supported formats: JPG, JPEG, PNG"
        )

        if uploaded_file:
            try:
                # Verify file content
                if uploaded_file.size > 200 * 1024 * 1024:  # 200MB limit
                    st.error("File size too large. Please upload an image smaller than 200MB.")
                else:
                    with st.spinner("Processing image..."):
                        # Process image
                        image = preprocess_image(uploaded_file)
                        enhanced_image = enhance_image(image)

                        # Display image
                        st.image(enhanced_image, caption="Uploaded Image", use_column_width=True)

                        # Analyze image
                        results = st.session_state.classifier.analyze_image(image)

                        if results["product"] != "Unknown":
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

                            # Display current price and change
                            price_col1, price_col2 = st.columns(2)
                            with price_col1:
                                st.metric(
                                    "Current Price",
                                    f"${price_data['current_price']:.2f}/kg",
                                    f"{price_data['price_change']:+.1f}%",
                                    delta_color="normal"
                                )

                            # Display average price
                            with price_col2:
                                st.metric(
                                    "30-Day Average",
                                    f"${price_data['average_price']:.2f}/kg"
                                )

                            # Display price range
                            st.markdown("#### Price Range (30 Days)")
                            range_col1, range_col2 = st.columns(2)
                            with range_col1:
                                st.metric("Lowest Price", f"${price_data['min_price']:.2f}/kg")
                            with range_col2:
                                st.metric("Highest Price", f"${price_data['max_price']:.2f}/kg")

                            # Get real-time price data
                            real_time_data = st.session_state.price_predictor.get_real_time_price(results['product'])

                            # Real-time price updates
                            st.markdown("### Real-Time Market Data")
                            rt_col1, rt_col2 = st.columns(2)

                            with rt_col1:
                                st.metric(
                                    "Real-Time Price",
                                    f"${real_time_data['current_price']:.2f}/kg",
                                    f"Next Hour: ${real_time_data['next_hour_prediction']:.2f}/kg",
                                    delta_color="normal"
                                )
                            with rt_col2:
                                st.text(f"Last Updated: {real_time_data['update_time']}")

                            # Price predictions
                            predictions = st.session_state.price_predictor.predict_price(results['product'])

                            st.markdown("### Price Predictions")
                            pred_col1, pred_col2 = st.columns(2)

                            with pred_col1:
                                st.metric(
                                    "Price Trend",
                                    predictions['trend'].title(),
                                    f"Confidence: {predictions['confidence']*100:.1f}%"
                                )

                            # Create forecast chart
                            if predictions['forecast']:
                                forecast_df = pd.DataFrame(predictions['forecast'])
                                forecast_df['date'] = pd.to_datetime(forecast_df['date'])

                                fig = px.line(
                                    forecast_df,
                                    x='date',
                                    y='price',
                                    title=f"{results['product']} Price Forecast (7 Days)",
                                    labels={'date': 'Date', 'price': 'Predicted Price ($/kg)'}
                                )
                                fig.update_layout(
                                    template='plotly_white',
                                    hovermode='x unified'
                                )
                                st.plotly_chart(fig, use_container_width=True)

                                # Market recommendations based on predictions
                                st.markdown("### Market Recommendations")
                                if predictions['trend'] == 'up':
                                    st.success("📈 Prices are expected to rise - Consider buying now")
                                elif predictions['trend'] == 'down':
                                    st.warning("📉 Prices are expected to fall - Consider waiting")
                                else:
                                    st.info("📊 Prices are expected to remain stable")


                        else:
                            st.error("Could not analyze the image. Please try uploading a clearer image.")
            except Exception as e:
                st.error(f"Error processing image: Please try again with a different image.")
                print(f"Error details: {str(e)}")

    except Exception as e:
        st.error("Error uploading file. Please try again.")
        print(f"Upload error details: {str(e)}")

with col2:
    st.subheader("Price Trends")
    if uploaded_file and results["product"] != "Unknown":
        try:
            # Get historical price data
            historical_data = st.session_state.price_analyzer.get_price_history(
                results['product'], days=90
            )

            if not historical_data.empty:
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
                st.warning("No price data available for this product")
        except Exception as e:
            st.error("Error loading price trends. Please try again.")
            print(f"Price trend error details: {str(e)}")
    else:
        st.info("Upload an image to view price trends and market insights")

# Footer
st.markdown("---")
st.markdown(
    "🌾 Agricultural Product Analyzer - Helping farmers make data-driven decisions"
)