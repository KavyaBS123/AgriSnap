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

    def _extract_features(self, image: Image.Image) -> dict:
        """Extract basic image features for mock classification"""
        # Convert to numpy array and ensure RGB
        img_array = np.array(image.convert('RGB'))

        # Calculate color features
        mean_color = img_array.mean(axis=(0, 1))
        std_color = img_array.std(axis=(0, 1))

        # Calculate brightness and contrast
        brightness = mean_color.mean()
        contrast = std_color.mean()

        return {
            'mean_color': mean_color,
            'std_color': std_color,
            'brightness': brightness,
            'contrast': contrast
        }

    def _classify_product(self, features: dict) -> str:
        """Classify product based on image features"""
        # Use color characteristics for classification
        mean_color = features['mean_color']
        brightness = features['brightness']

        # Rice typically has high brightness and low color variation
        if brightness > 180 and np.std(mean_color) < 20:
            return "Rice"

        # Corn typically has more yellow tones
        elif mean_color[1] > mean_color[2] and mean_color[0] > 150:
            return "Corn"

        # Default to using consistent random choice based on features
        np.random.seed(int(brightness * 1000))
        return np.random.choice(self.products)

    def _assess_quality(self, features: dict) -> tuple:
        """Assess quality and disease based on image features"""
        brightness = features['brightness']
        contrast = features['contrast']

        # Higher contrast and brightness usually indicate better quality
        quality_score = (brightness + contrast) / (255 * 2)

        if quality_score > 0.8:
            quality = "Excellent"
            disease = "Healthy"
            confidence = float(np.random.uniform(0.9, 0.99))
        elif quality_score > 0.6:
            quality = "Good"
            disease = "Healthy"
            confidence = float(np.random.uniform(0.8, 0.9))
        elif quality_score > 0.4:
            quality = "Fair"
            disease = np.random.choice(self.diseases, p=[0.6, 0.2, 0.1, 0.1])
            confidence = float(np.random.uniform(0.7, 0.8))
        else:
            quality = "Poor"
            disease = np.random.choice(self.diseases, p=[0.3, 0.3, 0.2, 0.2])
            confidence = float(np.random.uniform(0.6, 0.7))

        return quality, disease, confidence

    def analyze_image(self, image: Image.Image) -> dict:
        """Analyze image using mock ML classification"""
        try:
            # Extract image features
            features = self._extract_features(image)

            # Classify product and assess quality
            product_name = self._classify_product(features)
            quality, disease, confidence = self._assess_quality(features)

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

        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return {
                "product": "Unknown",
                "quality": "Unknown",
                "disease": "Unknown",
                "confidence": 0.0
            }