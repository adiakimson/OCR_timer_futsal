import cv2
import pytesseract
import re
import csv

# Define video path and output CSV file
video_path = 'test_counter_2.mp4'
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
        exit()

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
        else:
            format_match = 'N'
            matched_text = ''

        # Write results to CSV
        writer.writerow({'OCR Text': timer_text, 'MM:SS Format': format_match})

        # Draw ROI rectangle for visualization
        cv2.rectangle(frame, (x, y), (x+roi_width, y+roi_height), (255, 0, 0), 2)

        # Display the frame and ROI
        cv2.imshow('Frame', frame)
        cv2.imshow('ROI', binary_roi)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
