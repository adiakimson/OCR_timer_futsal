import cv2
import pytesseract
import re
import csv
import time
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Function to open file dialog and set video path
def select_video_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
    if file_path:
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, file_path)

# Create main tkinter window
root = tk.Tk()
root.title("Video Path Input")

# Create a label and entry widget for video path
tk.Label(root, text="Video Path:").pack(pady=10)
video_path_entry = tk.Entry(root, width=50)
video_path_entry.pack(pady=5)

# Create a button to open file dialog
tk.Button(root, text="Browse", command=select_video_file).pack(pady=10)

# Create a button to start processing
def start_processing():
    video_path = video_path_entry.get()
    if not video_path:
        tk.messagebox.showwarning("Warning", "Please select a video file.")
        return
    root.destroy()  # Close the tkinter window

    # Define output CSV file path
    csv_file_path = 'ocr_results.csv'

    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='') as csvfile:
        fieldnames = ['OCR Text', 'MM:SS Format']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Initialize video capture
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        # Define ROI dimensions
        roi_width = 200
        roi_height = 100
        frame_width = 640
        frame_height = 480
        center_x = frame_width // 2
        center_y = frame_height // 2
        x = center_x - (roi_width // 2)
        y = center_y - (roi_height // 2)

        # Define regex pattern for MM:SS format
        timer_pattern = re.compile(r'\b\d{2}:\d{2}\b')

        # Initialize reverse timer variables
        max_time_seconds = 20 * 60  # Assuming the timer counts up to 20:00

        start_time = time.time()
        last_time_read = None

        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video or cannot read frame.")
                break

            # Extract ROI
            roi = frame[y:y+roi_height, x:x+roi_width]

            # Convert ROI to grayscale
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply basic thresholding
            _, binary_roi = cv2.threshold(gray_roi, 128, 255, cv2.THRESH_BINARY)

            # Use OCR to extract text
            timer_text = pytesseract.image_to_string(binary_roi, config='--psm 7 -c tessedit_char_whitelist=0123456789:')
            timer_text = timer_text.strip()
            print("Raw OCR output: ", timer_text)

            # Check if the text matches MM:SS format
            match = timer_pattern.search(timer_text)
            if match:
                format_match = 'Y'
                matched_text = match.group()
                # Convert MM:SS to seconds
                min_sec = matched_text.split(':')
                current_time_seconds = int(min_sec[0]) * 60 + int(min_sec[1])
                if last_time_read is None:
                    last_time_read = current_time_seconds
            else:
                format_match = 'N'
                matched_text = ''

            # Calculate reversed time
            if last_time_read is not None:
                elapsed_time = time.time() - start_time
                reversed_time_seconds = max(0, max_time_seconds - elapsed_time)
                reversed_minutes = reversed_time_seconds // 60
                reversed_seconds = reversed_time_seconds % 60
                reversed_time_text = f"{int(reversed_minutes):02}:{int(reversed_seconds):02}"
            else:
                reversed_time_text = "00:00"

            # Write results to CSV
            writer.writerow({'OCR Text': timer_text, 'MM:SS Format': format_match})

            # Draw ROI rectangle for visualization
            cv2.rectangle(frame, (x, y), (x+roi_width, y+roi_height), (255, 0, 0), 2)

            # Display the frame, ROI, and reversed time
            cv2.imshow('Frame', frame)
            cv2.imshow('ROI', binary_roi)

            # Create a black image for reversed timer display
            reversed_timer_img = 255 * np.ones((100, 200, 3), dtype=np.uint8)
            cv2.putText(reversed_timer_img, reversed_time_text, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

            cv2.imshow('Reversed Timer', reversed_timer_img)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Create a button to start processing
tk.Button(root, text="Start Processing", command=start_processing).pack(pady=10)

# Run the tkinter main loop
root.mainloop()
