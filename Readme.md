# Project: Rule Engine System and Weather Monitoring System

This repository contains two standalone applications developed as part of an assignment to showcase expertise in backend development, API integration, and frontend interfacing.  

1. **Application 1**: **Rule Engine with AST**  
   A backend-driven rule engine that uses Abstract Syntax Trees (AST) to evaluate user-defined rules.  

2. **Application 2**: **Real-Time Data Processing System for Weather Monitoring with Rollups and Aggregates**  
   A real-time weather monitoring system with a user-friendly web interface to display live weather data, forecasts, and alerts.

---

## Application 1: Rule Engine with AST

### Overview
This is a 3-tier application that determines user eligibility based on custom-defined rules using an AST-based structure. The application includes:  
- **Rule Creation**: Converts rule strings into ASTs.  
- **Rule Combination**: Merges multiple rules using logical operators (AND, OR).  
- **Rule Evaluation**: Validates user attributes against the rules.

### Features
- Dynamic rule creation and combination.
- Backend API with endpoints for creating, combining, and evaluating rules.
- Lightweight UI for rule management.
- SQLite integration for rule storage.

![Screenshot 2024-11-19 222847](https://github.com/user-attachments/assets/70bb373f-39c3-4d85-b7d3-94cf43d0d93e)

### Build and Setup Instructions

1. **Clone the Repository:**
   ```
   git clone https://github.com/Pratham-Bajpai1/Rule-Engine-App-Weather-Monitoring-App.git
   cd Rule-Engine-App-Weather-Monitoring-App
   ```

2. **Navigate to Each Application:** For the Rule Engine with AST application
    ```
    cd Rule\ Engine\ App
    ```

3. **Set Up Virtual Environment:**
   ```
   python3 -m venv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Run the Application:**
   ```
   python app.py
   ```
 
6. **Access the UI:** [http://127.0.0.1:5000/ui](http://127.0.0.1:5000/ui)

---

## Application 2: Real-Time Data Processing System for Weather Monitoring with Rollups and Aggregates

### Overview

A real-time weather monitoring system that integrates with OpenWeatherMap API to display live weather data, 5-day forecasts, and weather alerts.

### Features
- Live weather data for multiple cities.
- Customizable preferences (temperature units: Celsius/Fahrenheit).
- SQLite storage for persistent weather summaries.
- Email alerts based on user-defined thresholds.

![Screenshot 2024-11-19 224045](https://github.com/user-attachments/assets/6637f115-309e-4060-8850-4ae80eab81fe)

![Screenshot 2024-11-19 224057](https://github.com/user-attachments/assets/a1f44462-1206-48a3-b5c3-091945baf4fd)


### Build and Setup Instructions

1. **Clone the Repository:**
   ```
   git clone https://github.com/Pratham-Bajpai1/Rule-Engine-App-Weather-Monitoring-App.git
   cd Rule-Engine-App-Weather-Monitoring-App
   ```

2. **Navigate to Each Application:** For the Weather Monitoring Application
    ```
    cd Weather\ Monitoring\ App
    ```

3. **Set Up Virtual Environment:**
   ```
   python3 -m venv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Set Your OpenWeatherMap API Key:**
-  Update config.py with your API key or export it as an environment variable.

6. **Run the Application:**
   ```
   python app.py
   ```
 
7. **Access the Web Interface:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## PDF Documentation

Refer to the PDF document for further design explanations and testing methodologies. The PDF will be more detailed, including:  
1. **Executive Summary** of both applications.  
2. **Key Features and Design Choices**.  
3. **GitHub Link** for the repository.  
4. **Detailed Testing Process**.  
5. **Future Enhancements and Known Issues**. 

---