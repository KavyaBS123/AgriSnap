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

        # Calculate color histogram
        hist_r = np.histogram(img_array[:,:,0], bins=32, range=(0,256))[0]
        hist_g = np.histogram(img_array[:,:,1], bins=32, range=(0,256))[0]
        hist_b = np.histogram(img_array[:,:,2], bins=32, range=(0,256))[0]

        # Normalize histograms
        hist_r = hist_r / hist_r.sum()
        hist_g = hist_g / hist_g.sum()
        hist_b = hist_b / hist_b.sum()

        # Calculate texture features using GLCM-like approach
        texture_features = self._calculate_texture_features(img_array)

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

        # Calculate color variance and standard deviation
        color_variance = np.var(mean_color)
        color_std = np.std(mean_color)

        return {
            'mean_color': mean_color,
            'std_color': std_color,
            'brightness': brightness,
            'contrast': contrast,
            'color_ratios': color_ratios,
            'histograms': {
                'r': hist_r,
                'g': hist_g,
                'b': hist_b
            },
            'texture': texture_features,
            'color_variance': color_variance,
            'color_std': color_std
        }

    def _calculate_texture_features(self, img_array: np.ndarray) -> dict:
        """Calculate texture features from image"""
        gray = np.mean(img_array, axis=2)  # Convert to grayscale

        # Calculate gradients
        grad_x = np.gradient(gray, axis=1)
        grad_y = np.gradient(gray, axis=0)

        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Calculate statistical features
        features = {
            'mean_gradient': np.mean(gradient_magnitude),
            'std_gradient': np.std(gradient_magnitude),
            'entropy': self._calculate_entropy(gray),
            'smoothness': 1 - (1 / (1 + np.std(gray)**2)),
            'uniformity': np.sum(np.square(np.histogram(gray, bins=32)[0] / gray.size))
        }

        return features

    def _calculate_entropy(self, gray_image: np.ndarray) -> float:
        """Calculate image entropy"""
        histogram = np.histogram(gray_image, bins=32)[0]
        histogram = histogram / histogram.sum()
        non_zero = histogram > 0
        return -np.sum(histogram[non_zero] * np.log2(histogram[non_zero]))

    def _classify_product(self, features: dict) -> str:
        """Enhanced crop classification based on image features"""
        try:
            brightness = features['brightness']
            contrast = features['contrast']
            color_ratios = features['color_ratios']
            texture = features['texture']
            histograms = features['histograms']
            color_variance = features['color_variance']
            color_std = features['color_std']

            # Calculate histogram similarities
            hist_peaks = {
                'r': np.argmax(histograms['r']),
                'g': np.argmax(histograms['g']),
                'b': np.argmax(histograms['b'])
            }

            # Rice detection: light colored, very uniform texture, low color variance
            if ((brightness > 160 and brightness < 220) and  # Typical rice brightness range
                color_variance < 100 and  # Low color variation
                color_std < 15 and  # Consistent color
                texture['uniformity'] > 0.2 and  # High uniformity
                texture['smoothness'] > 0.7 and  # Smooth texture
                abs(color_ratios['r_ratio'] - color_ratios['g_ratio']) < 0.1 and  # Similar R-G ratio
                color_ratios['b_ratio'] < 0.34 and  # Low blue component
                texture['entropy'] < 3.0):  # Low texture entropy
                return "Rice"

            # Corn detection: yellow-dominant, medium texture
            elif (color_ratios['r_ratio'] > 0.4 and
                  color_ratios['g_ratio'] > 0.35 and
                  color_ratios['b_ratio'] < 0.25 and
                  hist_peaks['r'] > hist_peaks['b'] and
                  texture['mean_gradient'] < 50):
                return "Corn"

            # Tomatoes detection: red-dominant, smooth texture
            elif (color_ratios['r_ratio'] > 0.45 and
                  color_ratios['g_ratio'] < 0.35 and
                  color_ratios['b_ratio'] < 0.3 and
                  hist_peaks['r'] > hist_peaks['g'] and
                  texture['smoothness'] > 0.7):
                return "Tomatoes"

            # Potatoes detection: brown/beige color, rough texture
            elif (abs(color_ratios['r_ratio'] - color_ratios['g_ratio']) < 0.1 and
                  color_ratios['b_ratio'] < 0.3 and
                  texture['mean_gradient'] > 30):
                return "Potatoes"

            # Wheat detection: yellow/brown, high texture detail
            elif (color_ratios['r_ratio'] > 0.35 and
                  color_ratios['g_ratio'] > 0.35 and
                  color_ratios['b_ratio'] < 0.3 and
                  texture['entropy'] > 3.5):
                return "Wheat"

            # Generate consistent random choice based on features if no clear match
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
            color_variance = features['color_variance']

            # Calculate quality score based on multiple factors
            color_balance = min(
                features['color_ratios'].values()
            ) / max(features['color_ratios'].values())

            texture_score = (
                0.3 * texture['uniformity'] +
                0.3 * (1 - texture['mean_gradient'] / 100) +
                0.4 * (1 - texture['entropy'] / 5)
            )

            # Add color consistency to quality assessment
            color_consistency = 1 - (color_variance / 1000)  # Normalize variance

            quality_score = (
                0.25 * (brightness / 255) +
                0.15 * (min(contrast, 100) / 100) +
                0.2 * color_balance +
                0.25 * texture_score +
                0.15 * color_consistency
            )

            # Determine quality and disease based on scores
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