!pip install tensorflow keras numpy matplotlib  opencv-python pydrive moviepy twilio requests geopy

import os
import numpy as np
import tensorflow as tf
import cv2
import requests
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from twilio.rest import Client
from geopy.geocoders import Nominatim
import time

 !wget 'https://www.kaggle.com/api/v1/datasets/download/asefjamilajwad/car-crash-dataset-ccd'

import os
import zipfile

# Define dataset paths
zip_path = "/content/car-crash-dataset-ccd.zip"
extract_path = "/content/CarCrashDataset"

# Unzipping dataset
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Check files
print("✅ Dataset extracted! Checking files...")
print(os.listdir(extract_path))
import os
import re

image_folder = "/content/CarCrashDataset/CrashBest"
image_files = os.listdir(image_folder)

image_info = []
for file in image_files:
    match = re.match(r"C_(\d+)_(\d+)\.jpg", file)
    if match:
        vidname, frame = map(int, match.groups())
        image_info.append((file, vidname, frame))

print(image_info[:5])  # Check extracted info

import pandas as pd

df = pd.read_csv("/content/CarCrashDataset/Crash_Table.csv")

matched_images = []
for file, vidname, frame in image_info:
    if vidname in df["vidname"].values:
        row = df[df["vidname"] == vidname]
        frame_col = f"frame_{frame}"
        if frame_col in row.columns and row[frame_col].values[0] == 1:
            matched_images.append((file, "crash"))
        else:
            matched_images.append((file, "non-crash"))

print(matched_images[:5])  # Check sample classification


import os
import shutil
import random

# Paths
image_folder = "/content/CarCrashDataset/CrashBest"
dataset_folder = "/content/CarCrashDataset"

# Create directory structure
for split in ["train", "test"]:
    for category in ["crash", "non-crash"]:
        os.makedirs(os.path.join(dataset_folder, split, category), exist_ok=True)

# Shuffle and split dataset (80% train, 20% test)
random.shuffle(matched_images)
split_index = int(0.8 * len(matched_images))
train_data = matched_images[:split_index]
test_data = matched_images[split_index:]

# Function to move images
def move_images(data, split):
    for file, label in data:
        src = os.path.join(image_folder, file)
        dest = os.path.join(dataset_folder, split, label, file)
        shutil.move(src, dest)

# Move images
move_images(train_data, "train")
move_images(test_data, "test")

print("✅ Dataset successfully structured!")
def build_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
        MaxPooling2D(2, 2),

        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

model = build_model()
model.summary()
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=20, zoom_range=0.2, horizontal_flip=True)
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory("/content/CarCrashDataset/train", target_size=(150, 150), batch_size=32, class_mode='binary')
test_generator = test_datagen.flow_from_directory("/content/CarCrashDataset/test", target_size=(150, 150), batch_size=32, class_mode='binary')

history = model.fit(train_generator, epochs=40,validation_data=test_generator)

model.save("accident_detection_model.h5")
# ✅ Evaluate on test data
test_loss, test_acc = model.evaluate(test_generator)
print(f" Test Accuracy: {accuracy * 100:.2f}%")
!pip install geopy
from geopy.geocoders import Nominatim
import requests

def get_location():
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        response = requests.get("http://ipinfo.io/json")
        data = response.json()
        loc = geolocator.reverse(f"{data['loc']}")
        return data['loc'], loc.address
    except:
        return "Unknown", "Location not found"

import requests

def get_weather_reminder(lat, lon):
    API_KEY = "a711657b83ab3c0dfe4369531843e457"  # Replace with a valid API key
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()
        condition = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']

        # Generate a safety reminder based on weather
        reminder = "Drive safely!"
        if "rain" in condition or "drizzle" in condition:
            reminder = "🌧️ Roads may be slippery! Drive with caution."
        elif "snow" in condition:
            reminder = "❄️ Snowy roads ahead! Reduce speed and be careful."
        elif "fog" in condition:
            reminder = "🌫️ Low visibility due to fog! Use fog lights."
        elif "clear" in condition and temp > 35:
            reminder = "☀️ It's hot outside! Stay hydrated and check tire pressure."
        elif "thunderstorm" in condition:
            reminder = "⛈️ Thunderstorm warning! Avoid unnecessary travel."

        return f"{condition.capitalize()}, Temp: {temp}°C. {reminder}"

    print(f"Error: {response.status_code}, Response: {response.text}")  # Debugging
    return "Weather data not available"

# Example usage
result = get_weather_reminder(39.0742, 21.8243)  # Example location (greece)
print(result)


import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os

def send_emergency_alert():
    from twilio.rest import Client
    # Twilio credentials
    account_sid = "*******************"
    auth_token = "********************"
    # Send SMS
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to="EMERGENCY NUMBER",
        from_="VICTIM NUMBER",
        body=["Accident detected near Narasaraopeta, Palnadu latitude:16.176050, longitude:80.076828", ]

    )


    print("🚨 Emergency Alert: Crash Detected! Notifying authorities...")
    print(f"✅ Emergency Alert Sent! SID: {message.sid}")

def accident_detection_on_image():
    model = load_model("accident_detection_model.h5")

    # Ask user for image name or use default
    input_image_path = input("Enter input image filename (or press Enter to use 'input_image.jpg'): ") or "input_image.jpg"

    # Load image
    frame = cv2.imread(input_image_path)
    if frame is None:
        print(f"❌ Error: Unable to read image at {input_image_path}")
        return

    print(f"✅ Image loaded successfully from {input_image_path}")

    # Preprocess image
    img = cv2.resize(frame, (150, 150))
    img = np.expand_dims(img, axis=0) / 255.0

    # Predict accident
    prediction = model.predict(img)
    print(f"🔍 Prediction Score: {prediction[0][0]}")

    label = "✅ No Crash"
    color = (0, 255, 0)

    if prediction[0][0] > 0.5:
        label = "🚗 Crash Detected!"
        color = (0, 0, 255)
        send_emergency_alert()  # Call send_emergency_alert inside the if block

        # Display result on image
        cv2.putText(frame, label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Save output in the same directory as script
        output_image_path = "output_image.jpg"
        cv2.imwrite(output_image_path, frame)

        print(f"✅ Processed image saved as {output_image_path}")


# Run the function
accident_detection_on_image()




 
