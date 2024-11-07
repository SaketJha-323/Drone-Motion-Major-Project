import cv2
import numpy as np
import time
import csv
import os

# Camera calibration parameters for each camera
fx1, fy1 = 700, 700  # Focal lengths for the front camera
cx1, cy1 = 320, 240  # Principal points for the front camera
fx2, fy2 = 700, 700  # Focal lengths for the side camera
cx2, cy2 = 320, 240  # Principal points for the side camera

baseline = 1000  # Distance between the two cameras in mm (baseline for triangulation)

# Conversion factors for pixel to mm conversion (based on calibration)
conversion_factor_x_front = 1 / fx1
conversion_factor_y_front = 1 / fy1
conversion_factor_x_side = 1 / fx2
conversion_factor_y_side = 1 / fy2

# Open video files or cameras
cap_front = cv2.VideoCapture('data/video/Drone2.mp4')
cap_side = cv2.VideoCapture('data/video/Drone1.mp4')

# Initialize variables
previous_position = None
previous_time = None
trajectory_data = []

def calculate_3d_position(x1, y1, x2):
    """Calculate 3D position using triangulation based on the front and side view coordinates."""
    disparity = abs(x1 - x2)
    z = fx1 * baseline / disparity if disparity != 0 else 0
    x_mm = (x1 - cx1) * conversion_factor_x_front * z
    y_mm = (y1 - cy1) * conversion_factor_y_front * z
    return np.array([x_mm, y_mm, z])

def calculate_velocity_acceleration(new_position, previous_position, dt):
    """Calculate velocity and acceleration vectors."""
    velocity = (new_position - previous_position) / dt
    if len(trajectory_data) > 1:
        prev_velocity = trajectory_data[-1]['velocity']
        acceleration = (velocity - prev_velocity) / dt
    else:
        acceleration = np.array([0, 0, 0])
    return velocity, acceleration

# Specify the path where the CSV file will be created
csv_file_path = 'C:/Users/SAKET JHA/Desktop/Drone_Motion_Data/trajectory_data.csv'

# Create the directory if it does not exist
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

# Open a CSV file to overwrite the previous data
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "X (mm)", "Y (mm)", "Z (mm)", "Velocity (mm/s)", "Acceleration (mm/s²)"])

    while cap_front.isOpened() and cap_side.isOpened():
        ret1, frame1 = cap_front.read()
        ret2, frame2 = cap_side.read()

        if not ret1 or not ret2:
            break

        # Resize frames for easier viewing if needed
        frame1 = cv2.resize(frame1, (640, 480))
        frame2 = cv2.resize(frame2, (640, 480))

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Simple thresholding for drone detection (replace with actual method if possible)
        ret1, thresh1 = cv2.threshold(gray1, 127, 255, cv2.THRESH_BINARY)
        ret2, thresh2 = cv2.threshold(gray2, 127, 255, cv2.THRESH_BINARY)

        contours1, _ = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours1 and contours2:
            largest_contour1 = max(contours1, key=cv2.contourArea)
            largest_contour2 = max(contours2, key=cv2.contourArea)

            x1, y1, w1, h1 = cv2.boundingRect(largest_contour1)
            x2, y2, w2, h2 = cv2.boundingRect(largest_contour2)

            position = calculate_3d_position(x1 + w1 // 2, y1 + h1 // 2, x2 + w2 // 2)

            current_time = time.time()
            if previous_time:
                dt = current_time - previous_time
            else:
                dt = 0
            previous_time = current_time

            if previous_position is not None:
                velocity, acceleration = calculate_velocity_acceleration(position, previous_position, dt)
            else:
                velocity, acceleration = np.array([0, 0, 0]), np.array([0, 0, 0])

            # Write the data point to the CSV file, overwriting previous data
            writer.writerow([current_time, position[0], position[1], position[2], np.linalg.norm(velocity), np.linalg.norm(acceleration)])

            previous_position = position

            # Draw bounding boxes
            cv2.rectangle(frame1, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
            cv2.rectangle(frame2, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
            cv2.putText(frame1, f"3D Position (mm): {position}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow('Front View Tracking', frame1)
        cv2.imshow('Side View Tracking', frame2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap_front.release()
cap_side.release()
cv2.destroyAllWindows()

print(f"Data extraction complete. Data saved to '{csv_file_path}'.")
