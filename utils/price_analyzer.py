import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import database as db

class PriceAnalyzer:
    def __init__(self):
        # Initialize database session
        self.db = next(db.get_db())
        self._ensure_sample_data()

    def _ensure_sample_data(self):
        """Ensure sample data exists in database"""
        # Define realistic base prices and seasonal patterns for each product
        product_configs = {
            "Rice": {"base_price": 2.50, "seasonal_shift": 90, "volatility": 0.10},
            "Wheat": {"base_price": 1.80, "seasonal_shift": 60, "volatility": 0.12},
            "Corn": {"base_price": 1.50, "seasonal_shift": 30, "volatility": 0.15},
            "Soybeans": {"base_price": 2.20, "seasonal_shift": 45, "volatility": 0.13},
            "Tomatoes": {"base_price": 3.50, "seasonal_shift": 0, "volatility": 0.20},
            "Potatoes": {"base_price": 1.20, "seasonal_shift": 120, "volatility": 0.15},
            "Apples": {"base_price": 2.80, "seasonal_shift": 180, "volatility": 0.18},
            "Oranges": {"base_price": 2.60, "seasonal_shift": 150, "volatility": 0.16}
        }

        for product_name, config in product_configs.items():
            # Check if product exists
            product = self.db.query(db.Product).filter(
                db.Product.name == product_name
            ).first()

            if not product:
                # Create new product
                product = db.Product(name=product_name)
                self.db.add(product)
                self.db.commit()

                # Generate price data with realistic patterns
                base_price = float(config["base_price"])
                seasonal_shift = config["seasonal_shift"]
                volatility = config["volatility"]

                dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

                for date in dates:
                    # Add seasonal variation with product-specific patterns
                    day_of_year = date.dayofyear
                    seasonal = float(0.15 * np.sin(2 * np.pi * (day_of_year + seasonal_shift) / 365))

                    # Add gradual market trend (slight upward bias)
                    trend = float(0.05 * (date - dates[0]).days / 365)

                    # Add controlled random noise
                    noise = float(np.random.normal(0, volatility / 3))

                    # Calculate final price with bounds
                    price = base_price * (1 + seasonal + trend + noise)
                    price = float(max(base_price * 0.7, min(base_price * 1.5, price)))

                    price_record = db.PriceRecord(
                        product_id=product.id,
                        timestamp=date.to_pydatetime(),
                        price=float(round(price, 2))
                    )
                    self.db.add(price_record)

                self.db.commit()

    def get_price_history(self, product: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data for a product"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query price records
            records = self.db.query(db.PriceRecord).join(db.Product).filter(
                db.Product.name == product,
                db.PriceRecord.timestamp >= start_date,
                db.PriceRecord.timestamp <= end_date
            ).order_by(db.PriceRecord.timestamp).all()

            if not records:
                print(f"No price records found for {product}")
                return pd.DataFrame(columns=['date', 'price'])

            # Convert to DataFrame
            data = [{
                'date': record.timestamp,
                'price': float(record.price)  # Ensure price is float
            } for record in records]

            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting price history: {str(e)}")
            return pd.DataFrame(columns=['date', 'price'])

    def get_price_statistics(self, product: str) -> dict:
        """Calculate price statistics for a product"""
        try:
            # Get all price records for the product
            records = self.db.query(db.PriceRecord).join(db.Product).filter(
                db.Product.name == product
            ).order_by(db.PriceRecord.timestamp.desc()).all()

            if not records:
                print(f"No price records found for {product}")
                return {
                    'current_price': 0.0,
                    'average_price': 0.0,
                    'price_change': 0.0,
                    'min_price': 0.0,
                    'max_price': 0.0
                }

            # Calculate statistics
            current_price = float(records[0].price)
            prices = [float(record.price) for record in records[:30]]  # Last 30 days

            if not prices:
                return {
                    'current_price': 0.0,
                    'average_price': 0.0,
                    'price_change': 0.0,
                    'min_price': 0.0,
                    'max_price': 0.0
                }

            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)

            # Calculate price change from previous day
            if len(prices) > 1:
                prev_price = prices[1]  # Yesterday's price
                price_change = ((current_price - prev_price) / prev_price) * 100
            else:
                price_change = 0.0

            return {
                'current_price': round(current_price, 2),
                'average_price': round(avg_price, 2),
                'price_change': round(price_change, 1),
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2)
            }
        except Exception as e:
            print(f"Error calculating price statistics: {str(e)}")
            return {
                'current_price': 0.0,
                'average_price': 0.0,
                'price_change': 0.0,
                'min_price': 0.0,
                'max_price': 0.0
            }