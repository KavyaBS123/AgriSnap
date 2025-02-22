# 🌾 Agricultural Product Analyzer  
An advanced web application to analyze agricultural products using image processing and provide real-time market insights. The app predicts crop quality, detects diseases, and offers historical and predictive price analysis.  

---

## 🚀 Features  

1. **Image Analysis:**  
   - Upload images of agricultural products (e.g., fruits, vegetables, grains).  
   - Identify product type, quality grade, and plant health.  
   - Confidence scores for the analysis.  

2. **Price Analysis:**  
   - Retrieve current market prices, 30-day averages, and price changes.  
   - Historical price data visualization.  
   - Real-time price updates every 5 minutes.  
   - Price predictions for the next 7 days using trend analysis.  

3. **Data Flow:**  
   - Image Upload → Image Processing → Product Classification  
   - Product Identification → Price Data Retrieval → Market Analysis  
   - Historical Data → Price Prediction → Trend Analysis  

4. **User Interface:**  
   - Two-column layout:  
     - **Left Column:** Image analysis and results  
     - **Right Column:** Price trends and market insights  
   - Real-time updates, interactive charts, and market recommendations.  

---

## 🛠️ Tech Stack  

- **Frontend:** Streamlit (Python web framework)  
- **Backend:** Python (FastAPI), PostgreSQL for data persistence  
- **Machine Learning:** Mock ML Classifier for image analysis and Linear Regression & Exponential Smoothing for price prediction  
- **Deployment:** Replit (auto-scale and deploy on port 5000)  

---

## 📁 Project Structure  

```plaintext
├── main.py                 # Main application logic  
├── image_processor.py       # Image preprocessing and enhancement  
├── mock_ml.py               # Mock ML classifier for agricultural products  
├── price_analyzer.py        # Historical price data analysis  
├── price_predictor.py       # Price prediction using ML models  
├── database.py              # PostgreSQL database connection management  
└── requirements.txt         # Python dependencies  
---

## 🚀 Getting Started  

### Prerequisites  
- Python 3.x  
- PostgreSQL  

### Installation  

1. **Create a virtual environment:**  
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Linux/Mac
    venv\Scripts\activate      # On Windows
    ```

2. **Install dependencies:**  
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up PostgreSQL database:**  
   - Create a database and update connection details in `database.py`.  
   - Run migrations or initialize the tables manually:  
     - `Products` table: Stores product information  
     - `Analyses` table: Stores image analysis results  
     - `PriceRecord` table: Stores historical price data  

---

## 🚀 Running the Application  

```bash
streamlit run main.py

## 🤖 Mock ML Classification  
- **Image Analysis:** Analyzes color, texture, and patterns.  
- **Predefined Rules:** Simulates product identification and quality assessment.  
- **Confidence Scores:** Provides simulated confidence levels for predictions.  

---

## 📊 Price Prediction Models  
- **Linear Regression:** For trend analysis.  
- **Exponential Smoothing:** For short-term predictions.  
- **Hybrid Approach:** Combines multiple models for better accuracy.  

---

## 🎨 User Interface  
- **Interactive Dashboard:** Two-column layout for seamless navigation.  
- **Real-Time Updates:** Charts and metrics update dynamically.  
- **Market Recommendations:** Provides insights based on price trends.  

---

## 🌐 Deployment  
The application is configured to deploy on Replit, with auto-scaling and real-time updates.  

---

## 📈 Future Enhancements  
- Integrate advanced ML models (CNNs) for better image classification.  
- Incorporate real-world APIs for live market prices.  
- Implement user authentication for personalized experiences.  

---

## 🤝 Contributing  
Contributions are welcome! Please fork the repository and submit a pull request.  

---

## 📄 License  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---
