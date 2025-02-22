import numpy as np
from PIL import Image

class MockClassifier:
    def __init__(self):
        self.products = [
            "Tomatoes", "Potatoes", "Wheat", "Corn", 
            "Soybeans", "Rice", "Apples", "Oranges"
        ]
        self.qualities = ["Excellent", "Good", "Fair", "Poor"]
        self.diseases = ["Healthy", "Leaf Spot", "Blight", "Rust"]

    def analyze_image(self, image: Image.Image) -> dict:
        """Mock image analysis returning random but consistent results"""
        # Convert image to numpy array for demonstration
        img_array = np.array(image)
        
        # Use image characteristics to generate consistent random results
        seed = int(img_array.mean() * 1000)
        np.random.seed(seed)
        
        return {
            "product": np.random.choice(self.products),
            "quality": np.random.choice(self.qualities, p=[0.4, 0.3, 0.2, 0.1]),
            "disease": np.random.choice(self.diseases, p=[0.7, 0.1, 0.1, 0.1]),
            "confidence": round(np.random.uniform(0.85, 0.99), 2)
        }
