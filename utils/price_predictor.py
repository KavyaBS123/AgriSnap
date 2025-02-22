import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from . import database as db

class PricePredictor:
    def __init__(self):
        self.db = next(db.get_db())
        self.last_update = {}
        self.update_interval = 300  # 5 minutes in seconds

    def _get_historical_data(self, product: str, days: int = 90) -> pd.DataFrame:
        """Get historical price data for prediction"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            records = self.db.query(db.PriceRecord).join(db.Product).filter(
                db.Product.name == product,
                db.PriceRecord.timestamp >= start_date
            ).order_by(db.PriceRecord.timestamp).all()
            
            data = [{
                'timestamp': record.timestamp,
                'price': float(record.price)
            } for record in records]
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting historical data: {str(e)}")
            return pd.DataFrame()

    def _prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for prediction"""
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['trend'] = np.arange(len(df))
        
        X = df[['day_of_week', 'month', 'trend']].values
        y = df['price'].values
        return X, y

    def predict_price(self, product: str, days_ahead: int = 7) -> dict:
        """Predict future prices using multiple models"""
        try:
            # Get historical data
            df = self._get_historical_data(product)
            if df.empty:
                return {
                    'forecast': [],
                    'confidence': 0.0,
                    'trend': 'stable'
                }

            # Prepare data for prediction
            X, y = self._prepare_features(df)
            
            # Linear regression for trend
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate future dates
            last_date = df['timestamp'].max()
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=days_ahead,
                freq='D'
            )
            
            # Prepare future features
            future_df = pd.DataFrame({'timestamp': future_dates})
            future_df['day_of_week'] = future_df['timestamp'].dt.dayofweek
            future_df['month'] = future_df['timestamp'].dt.month
            future_df['trend'] = np.arange(len(df), len(df) + len(future_df))
            
            # Make predictions
            X_future = future_df[['day_of_week', 'month', 'trend']].values
            lr_predictions = model.predict(X_future)
            
            # Exponential smoothing for short-term predictions
            hw_model = ExponentialSmoothing(
                y,
                seasonal_periods=7,
                trend='add',
                seasonal='add'
            ).fit()
            hw_predictions = hw_model.forecast(days_ahead)
            
            # Combine predictions
            final_predictions = (lr_predictions + hw_predictions) / 2
            
            # Calculate confidence and trend
            confidence = float(model.score(X, y))
            recent_trend = np.mean(np.diff(y[-7:]))
            
            trend_direction = 'up' if recent_trend > 0.01 else \
                            'down' if recent_trend < -0.01 else 'stable'
            
            # Format predictions
            forecast = [{
                'date': date.strftime('%Y-%m-%d'),
                'price': float(round(price, 2))
            } for date, price in zip(future_dates, final_predictions)]
            
            return {
                'forecast': forecast,
                'confidence': round(confidence, 2),
                'trend': trend_direction
            }
            
        except Exception as e:
            print(f"Error in price prediction: {str(e)}")
            return {
                'forecast': [],
                'confidence': 0.0,
                'trend': 'stable'
            }

    def _update_real_time_price(self, product: str) -> float:
        """Update real-time price based on market factors"""
        try:
            # Get current price
            current_record = self.db.query(db.PriceRecord).join(db.Product).filter(
                db.Product.name == product
            ).order_by(db.PriceRecord.timestamp.desc()).first()
            
            if not current_record:
                return 0.0
            
            current_price = float(current_record.price)
            
            # Simulate real-time factors (replace with actual market data in production)
            time_factor = np.sin(datetime.now().hour / 24 * 2 * np.pi) * 0.002
            random_factor = np.random.normal(0, 0.001)
            
            # Calculate new price
            new_price = current_price * (1 + time_factor + random_factor)
            
            # Add new price record if enough time has passed
            last_update = self.last_update.get(product, datetime.min)
            if (datetime.now() - last_update).total_seconds() >= self.update_interval:
                new_record = db.PriceRecord(
                    product_id=current_record.product_id,
                    timestamp=datetime.utcnow(),
                    price=float(round(new_price, 2))
                )
                self.db.add(new_record)
                self.db.commit()
                self.last_update[product] = datetime.now()
            
            return float(round(new_price, 2))
            
        except Exception as e:
            print(f"Error updating real-time price: {str(e)}")
            return 0.0

    def get_real_time_price(self, product: str) -> dict:
        """Get real-time price and short-term prediction"""
        try:
            # Get updated price
            current_price = self._update_real_time_price(product)
            if current_price == 0.0:
                return {
                    'current_price': 0.0,
                    'next_hour_prediction': 0.0,
                    'update_time': datetime.now().strftime('%H:%M:%S')
                }
            
            # Short-term prediction
            df = self._get_historical_data(product, days=1)
            if not df.empty:
                recent_trend = np.mean(np.diff(df['price'].values[-12:]))  # Last 12 records
                next_hour = current_price * (1 + recent_trend)
            else:
                next_hour = current_price
            
            return {
                'current_price': current_price,
                'next_hour_prediction': float(round(next_hour, 2)),
                'update_time': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error getting real-time price: {str(e)}")
            return {
                'current_price': 0.0,
                'next_hour_prediction': 0.0,
                'update_time': datetime.now().strftime('%H:%M:%S')
            }
