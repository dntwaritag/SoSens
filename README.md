# SoSens - Soil Quality Monitoring &amp; Decision Support

# SoSens – Crop Recommendation System

## Description
SoSens is a Machine Learning-based crop recommendation system designed to assist farmers and agricultural professionals in selecting the most suitable crop based on soil properties and weather data. The project integrates a trained ML model, a RESTful FastAPI backend, and a responsive web interface for user interaction.

## GitHub Repository
[GitHub Repository Link](https://github.com/dntwaritag/SoSens)

## Environment Setup and Project Configuration

### 1. Clone the Repository
```
git clone https://github.com/dntwaritag/SoSens.git
cd SoSens
```

### 2. Create and Activate a Virtual Environment
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Train the Model
```
python train_model.py
```
This generates model files under the `models/` directory:
```
models/
 ├── baseline_model.pkl
 ├── feature_names.pkl
 ├── label_encoder.pkl
 └── scaler.pkl
```

### 5. Start the Backend Server
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Access API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 6. Run the Frontend Interface
Open the file `frontend/index.html` in your browser. The interface will communicate with the running backend automatically.

## Designs and Screens
- Figma Prototype: View [[Figma Design](https://www.figma.com/design/RPA8CQDQhmZm6mkEIMBJ3n/Farming?node-id=0-1&t=Ji1KlmsOBSqDAzLJ-1)]
## Deployment Plan
| Stage | Description |
|--------|-------------|
| Local Testing | Train and test model locally with CSV dataset. |
| Backend Deployment | Deploy FastAPI API to Render, Heroku, or AWS EC2. |
| Frontend Deployment | Deploy static web files to GitHub Pages or Netlify. |
| Integration | Connect the frontend to the hosted backend API endpoint. |
| Maintenance | Monitor performance, collect user feedback, and retrain the model periodically. |

## Video Demonstration

Demo Video [Link](https://www.figma.com/design/RPA8CQDQhmZm6mkEIMBJ3n/Farming?node-id=0-1&t=Ji1KlmsOBSqDAzLJ-1)


## Features
- Predicts suitable crops using soil nutrients and weather data
- Includes multiple crop classes (12+)
- Responsive and user-friendly interface
- Displays model confidence and top crop recommendations
- Designed for integration with IoT-based soil sensors

## Project Structure
```
SoSens/
├── app/
│   ├── main.py
│   └── __init__.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── models/
│   ├── baseline_model.pkl
│   ├── feature_names.pkl
│   ├── label_encoder.pkl
│   └── scaler.pkl
├── data/
│   └── Crop Recommendation using Soil Properties and Weather Prediction.csv
├── train_model.py
├── requirements.txt
└── README.md
```

## Author
**Denys Ntwaritaganzwa**    
Email: [d.ntwaritag@alustudent.com]  
