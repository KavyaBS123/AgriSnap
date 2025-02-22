import cv2
import numpy as np
from PIL import Image
import io

def preprocess_image(uploaded_file) -> Image.Image:
    """Preprocess uploaded image for analysis"""
    # Read uploaded file
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize image while maintaining aspect ratio
    max_size = (800, 800)
    image.thumbnail(max_size, Image.LANCZOS)
    
    return image

def enhance_image(image: Image.Image) -> Image.Image:
    """Enhance image for better visualization"""
    # Convert PIL Image to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Apply basic enhancement
    img_cv = cv2.convertScaleAbs(img_cv, alpha=1.1, beta=10)
    
    # Convert back to PIL Image
    enhanced = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    return enhanced
