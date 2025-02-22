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
        """Extract detailed image features for crop classification"""
        # Convert to numpy array and ensure RGB
        img_array = np.array(image.convert('RGB'))

        # Calculate color features
        mean_color = img_array.mean(axis=(0, 1))
        std_color = img_array.std(axis=(0, 1))

        # Calculate brightness and contrast
        brightness = mean_color.mean()
        contrast = std_color.mean()

        # Calculate color ratios
        r, g, b = mean_color
        total = r + g + b + 1e-6  # Avoid division by zero
        color_ratios = {
            'r_ratio': r / total,
            'g_ratio': g / total,
            'b_ratio': b / total
        }

        # Calculate texture features
        texture_std = img_array.std(axis=(0, 1)).mean()

        return {
            'mean_color': mean_color,
            'std_color': std_color,
            'brightness': brightness,
            'contrast': contrast,
            'color_ratios': color_ratios,
            'texture': texture_std
        }

    def _classify_product(self, features: dict) -> str:
        """Enhanced crop classification based on image features"""
        try:
            brightness = features['brightness']
            contrast = features['contrast']
            color_ratios = features['color_ratios']
            texture = features['texture']
            mean_color = features['mean_color']

            # Rice detection: light colored, low color variation, medium texture
            if (brightness > 180 and 
                np.std(mean_color) < 25 and
                texture > 10 and texture < 40 and
                color_ratios['r_ratio'] > 0.3 and
                color_ratios['g_ratio'] > 0.3):
                return "Rice"

            # Corn detection: yellow-dominant
            elif (color_ratios['r_ratio'] > 0.4 and
                  color_ratios['g_ratio'] > 0.35 and
                  color_ratios['b_ratio'] < 0.25):
                return "Corn"

            # Tomatoes detection: red-dominant
            elif (color_ratios['r_ratio'] > 0.45 and
                  color_ratios['g_ratio'] < 0.35 and
                  color_ratios['b_ratio'] < 0.3):
                return "Tomatoes"

            # Default to using consistent random choice based on features
            np.random.seed(int(brightness * 1000))
            return np.random.choice(self.products)

        except Exception as e:
            print(f"Error in product classification: {str(e)}")
            return "Unknown"

    def _assess_quality(self, features: dict) -> tuple:
        """Assess quality and disease based on image features"""
        try:
            brightness = features['brightness']
            contrast = features['contrast']
            texture = features['texture']

            # Calculate quality score based on multiple factors
            quality_score = (
                0.4 * (brightness / 255) +
                0.3 * (min(contrast, 100) / 100) +
                0.3 * (min(texture, 50) / 50)
            )

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

        except Exception as e:
            print(f"Error in quality assessment: {str(e)}")
            return "Unknown", "Unknown", 0.0

    def analyze_image(self, image: Image.Image) -> dict:
        """Analyze image using enhanced mock ML classification"""
        try:
            # Extract image features
            features = self._extract_features(image)

            # Classify product and assess quality
            product_name = self._classify_product(features)
            quality, disease, confidence = self._assess_quality(features)

            if product_name != "Unknown":
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