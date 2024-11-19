from flask import Flask, render_template, jsonify, request
import requests
import datetime
import sqlite3
import threading
import time
import schedule
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
API_KEY = 'e9f073e1f765bd9909d2aed3354a8715' #Replace with your OpenWeatherMap API key
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
API_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'
PREFERENCE = 'Celsius'  # Default preference

# User-defined thresholds
ALERT_THRESHOLDS = {
    'temperature': 35,  # Alert threshold for temperature (Celsius)
    'humidity': 80,     # Humidity threshold
    'wind_speed': 20    # Wind speed threshold
}

#  Email credentials storage
email_credentials = {
    'sender_email': None,
    'password': None,
    'receiver_email': None
}


def create_db():
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    # Create table with additional columns
    c.execute('''CREATE TABLE IF NOT EXISTS weather_summary (
                         date TEXT,
                         city TEXT,
                         avg_temp REAL,
                         max_temp REAL,
                         min_temp REAL,
                         dominant_weather TEXT,
                         feels_like REAL,
                         humidity INTEGER,
                         wind_speed REAL
                     )''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
                         timestamp TEXT,
                         city TEXT,
                         condition TEXT,
                         threshold REAL,
                         alert_message TEXT
                     )''')
    c.execute('''CREATE TABLE IF NOT EXISTS forecast_data (
                        date TEXT, city TEXT, temp REAL, humidity INTEGER, 
                        wind_speed REAL, description TEXT)''')
    conn.commit()
    conn.close()

# Initialize database
create_db()

def convert_temperature(kelvin, preference):
    if preference == 'Celsius':
        return kelvin - 273.15
    elif preference == 'Fahrenheit':
        return (kelvin - 273.15) * 9/5 + 32


def fetch_weather_data(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(API_URL, params=params)
    data = response.json()

    if data.get('main'):
        return {
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'main': data['weather'][0]['main'],
            'dt': data['dt']
        }
    return None

def fetch_forecast_data(city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    response = requests.get(FORECAST_URL, params=params)
    forecast_data = response.json()
    daily_forecast = []
    if 'list' in forecast_data:
        for entry in forecast_data['list']:
            daily_forecast.append({
                'date': entry['dt_txt'],
                'temp': entry['main']['temp'],
                'humidity': entry['main']['humidity'],
                'wind_speed': entry['wind']['speed'],
                'description': entry['weather'][0]['description']
            })
    return daily_forecast

def store_forecast_data(city, forecast_data):
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    for entry in forecast_data:
        c.execute('''INSERT INTO forecast_data (date, city, temp, humidity, wind_speed, description)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (entry['date'], city, entry['temp'], entry['humidity'], entry['wind_speed'], entry['description']))
    conn.commit()
    conn.close()


def store_weather_data(city, weather_info):
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()

    date = datetime.datetime.fromtimestamp(weather_info['dt'], datetime.timezone.utc).strftime('%Y-%m-%d')

    # Check if an entry already exists for the same date and city
    c.execute('SELECT * FROM weather_summary WHERE date = ? AND city = ?', (date, city))
    entry = c.fetchone()

    if entry:
        # Update the existing entry
        c.execute('''
                UPDATE weather_summary
                SET avg_temp = ?, max_temp = ?, min_temp = ?, dominant_weather = ?, feels_like = ?, humidity = ?, wind_speed = ?
                WHERE date = ? AND city = ?
            ''', (weather_info['temp'], weather_info['temp'], weather_info['temp'],
                  weather_info['main'], weather_info['feels_like'], weather_info['humidity'],
                  weather_info['wind_speed'],
                  date, city))
    else:
         #Insert a new entry
         c.execute('''
                INSERT INTO weather_summary (date, city, avg_temp, max_temp, min_temp, dominant_weather, feels_like, humidity, wind_speed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, city, weather_info['temp'], weather_info['temp'], weather_info['temp'],
                  weather_info['main'], weather_info['feels_like'], weather_info['humidity'],
                  weather_info['wind_speed']))

    conn.commit()
    conn.close()

def get_weather_data():
    for city in CITIES:
        weather_info = fetch_weather_data(city)
        if weather_info:
            store_weather_data(city, weather_info)
            alerts = check_alerts(city, weather_info)
            forecast = fetch_forecast_data(city)
            store_forecast_data(city, forecast)


def calculate_daily_summary():
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()

    # Aggregate weather data by date and city
    query = '''SELECT city, date,
                      AVG(avg_temp) AS avg_temp,
                      MAX(max_temp) AS max_temp,
                      MIN(min_temp) AS min_temp,
                      MAX(dominant_weather) AS dominant_weather
               FROM weather_summary
               GROUP BY date, city'''

    c.execute(query)
    daily_summary = c.fetchall()
    conn.close()
    return daily_summary


def check_alerts(city, weather_info):
    alerts = []

    if weather_info['temp'] > ALERT_THRESHOLDS['temperature']:
        alert_msg = f"Temperature alert in {city}: {weather_info['temp']}°C exceeds {ALERT_THRESHOLDS['temperature']}°C"
        alerts.append(alert_msg)
        print(alert_msg)

    if weather_info['humidity'] > ALERT_THRESHOLDS['humidity']:
        alert_msg = f"Humidity alert in {city}: {weather_info['humidity']}% exceeds {ALERT_THRESHOLDS['humidity']}%"
        alerts.append(alert_msg)
        print(alert_msg)

    if weather_info['wind_speed'] > ALERT_THRESHOLDS['wind_speed']:
        alert_msg = f"Wind speed alert in {city}: {weather_info['wind_speed']} m/s exceeds {ALERT_THRESHOLDS['wind_speed']} m/s"
        alerts.append(alert_msg)
        print(alert_msg)

    # Store alerts in the database
    if alerts:
        conn = sqlite3.connect('weather_data.db')
        c = conn.cursor()
        for alert in alerts:
            c.execute('''INSERT INTO alerts (timestamp, city, condition, threshold, alert_message)
                         VALUES (?, ?, ?, ?, ?)''',
                      (datetime.datetime.now(), city, "Weather", weather_info['temp'], alert))
        conn.commit()
        conn.close()

        # Send email notification for each alert
        for alert in alerts:
            send_email_alert(alert)


def send_email_alert(alert_message):
    sender = email_credentials['sender_email']
    password = email_credentials['password']
    receiver = email_credentials['receiver_email']

    if sender and password and receiver:
        try:
            msg = MIMEText(alert_message)
            msg['Subject'] = "Weather Alert Notification"
            msg['From'] = sender
            msg['To'] = receiver

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            print("Alert email sent successfully!")
        except Exception as e:
            print("Error sending email:", e)
    else:
        print("Email credentials not set. Please enter them in the interface.")


def schedule_weather_updates():
    schedule.every(5).minutes.do(get_weather_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=schedule_weather_updates).start()

@app.route('/get_forecast')
def get_forecast():
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forecast_data')
    forecast = c.fetchall()
    conn.close()
    return jsonify(forecast)

@app.route('/set_email_credentials', methods=['POST'])
def set_email_credentials():
    email_credentials['sender_email'] = request.form.get('sender_email')
    email_credentials['password'] = request.form.get('password')
    email_credentials['receiver_email'] = request.form.get('receiver_email')
    return jsonify({"message": "Email credentials updated successfully!"})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_preference', methods=['POST'])
def set_preference():
    global PREFERENCE
    PREFERENCE = request.form.get('preference')
    return jsonify({"message": "Preference updated"})

@app.route('/get_daily_summary')
def get_daily_summary():
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM weather_summary')
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)


@app.route('/get_visualization_data')
def get_visualization_data():
    # Fetch daily summaries
    summaries = calculate_daily_summary()
    # Fetch alerts
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM alerts')
    alerts = c.fetchall()
    conn.close()
    return jsonify({'summaries': summaries, 'alerts': alerts})

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)