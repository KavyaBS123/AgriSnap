import numpy as np
from PIL import Image
from sqlalchemy.orm import Session
from datetime import datetime
from . import database as db

class MockClassifier:
    def __init__(self):
        self.products = [
            "Tomatoes", "Potatoes", "Wheat", "Corn", 
            "Soybeans", "Rice", "Apples", "Oranges"
        ]
        self.qualities = ["Excellent", "Good", "Fair", "Poor"]
        self.diseases = ["Healthy", "Leaf Spot", "Blight", "Rust"]
        self.db = next(db.get_db())

    def analyze_image(self, image: Image.Image) -> dict:
        """Mock image analysis returning random but consistent results"""
        # Convert image to numpy array for demonstration
        img_array = np.array(image)

        # Use image characteristics to generate consistent random results
        seed = int(img_array.mean() * 1000)
        np.random.seed(seed)

        # Generate analysis results
        product_name = np.random.choice(self.products)
        quality = np.random.choice(self.qualities, p=[0.4, 0.3, 0.2, 0.1])
        disease = np.random.choice(self.diseases, p=[0.7, 0.1, 0.1, 0.1])
        confidence = round(np.random.uniform(0.85, 0.99), 2)

        # Save analysis to database
        product = self.db.query(db.Product).filter(
            db.Product.name == product_name
        ).first()

        if not product:
            product = db.Product(name=product_name)
            self.db.add(product)
            self.db.commit()

        analysis = db.Analysis(
            product_id=product.id,
            quality=quality,
            disease=disease,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
        self.db.add(analysis)
        self.db.commit()

        return {
            "product": product_name,
            "quality": quality,
            "disease": disease,
            "confidence": confidence
        }