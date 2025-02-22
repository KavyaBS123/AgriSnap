import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PriceAnalyzer:
    def __init__(self):
        # Generate sample price data
        self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample price data for demonstration"""
        products = ["Tomatoes", "Potatoes", "Wheat", "Corn", 
                   "Soybeans", "Rice", "Apples", "Oranges"]
        
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        data = []
        
        for product in products:
            base_price = np.random.uniform(0.5, 5.0)
            for date in dates:
                # Add seasonal variation
                seasonal = 0.2 * np.sin(2 * np.pi * date.dayofyear / 365)
                # Add random noise
                noise = np.random.normal(0, 0.05)
                price = base_price * (1 + seasonal + noise)
                data.append({
                    'date': date,
                    'product': product,
                    'price': round(max(price, 0.1), 2)
                })
        
        self.df = pd.DataFrame(data)
        
    def get_price_history(self, product: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data for a product"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        mask = (self.df['product'] == product) & \
               (self.df['date'].dt.date >= start_date) & \
               (self.df['date'].dt.date <= end_date)
        
        return self.df[mask].copy()
    
    def get_price_statistics(self, product: str) -> dict:
        """Calculate price statistics for a product"""
        recent_data = self.get_price_history(product, days=30)
        current_price = recent_data['price'].iloc[-1]
        avg_price = recent_data['price'].mean()
        price_change = ((current_price - recent_data['price'].iloc[0]) / 
                       recent_data['price'].iloc[0] * 100)
        
        return {
            'current_price': round(current_price, 2),
            'average_price': round(avg_price, 2),
            'price_change': round(price_change, 1)
        }
