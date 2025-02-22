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
        products = ["Tomatoes", "Potatoes", "Wheat", "Corn", 
                   "Soybeans", "Rice", "Apples", "Oranges"]

        for product_name in products:
            # Check if product exists
            product = self.db.query(db.Product).filter(
                db.Product.name == product_name
            ).first()

            if not product:
                # Create new product
                product = db.Product(name=product_name)
                self.db.add(product)
                self.db.commit()

                # Generate sample price data
                base_price = float(np.random.uniform(0.5, 5.0))  # Convert to Python float

                # Adjust base price for different products
                if product_name == "Rice":
                    base_price = float(2.5)  # Set realistic base price for rice
                elif product_name == "Corn":
                    base_price = float(1.8)  # Set realistic base price for corn

                dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

                for date in dates:
                    # Add seasonal variation (different patterns for different products)
                    day_of_year = date.dayofyear
                    if product_name in ["Rice", "Wheat", "Corn"]:
                        # Grains have different seasonal patterns
                        seasonal = float(0.15 * np.sin(2 * np.pi * (day_of_year + 90) / 365))
                    else:
                        seasonal = float(0.2 * np.sin(2 * np.pi * day_of_year / 365))

                    # Add market trends
                    trend = float(0.1 * (date - dates[0]).days / 365)

                    # Add random noise
                    noise = float(np.random.normal(0, 0.02))

                    # Calculate final price
                    price = base_price * (1 + seasonal + trend + noise)

                    price_record = db.PriceRecord(
                        product_id=product.id,
                        timestamp=date.to_pydatetime(),  # Convert pandas timestamp to Python datetime
                        price=float(round(max(price, 0.1), 2))  # Convert to Python float
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

            # Convert to DataFrame
            data = [{
                'date': record.timestamp,
                'price': record.price
            } for record in records]

            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting price history: {str(e)}")
            return pd.DataFrame(columns=['date', 'price'])

    def get_price_statistics(self, product: str) -> dict:
        """Calculate price statistics for a product"""
        try:
            recent_data = self.get_price_history(product, days=30)

            if recent_data.empty:
                return {
                    'current_price': 0.0,
                    'average_price': 0.0,
                    'price_change': 0.0
                }

            current_price = float(recent_data['price'].iloc[-1])
            avg_price = float(recent_data['price'].mean())
            price_change = float(((current_price - recent_data['price'].iloc[0]) / 
                         recent_data['price'].iloc[0] * 100))

            return {
                'current_price': round(current_price, 2),
                'average_price': round(avg_price, 2),
                'price_change': round(price_change, 1)
            }
        except Exception as e:
            print(f"Error calculating price statistics: {str(e)}")
            return {
                'current_price': 0.0,
                'average_price': 0.0,
                'price_change': 0.0
            }