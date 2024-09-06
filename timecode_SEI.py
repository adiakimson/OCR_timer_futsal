import ffmpeg
import subprocess
import re
import tkinter as tk
from tkinter import messagebox

def extract_sei_from_rtmp(rtmp_url):
    # Start an ffmpeg process to capture SEI messages
    process = (
        ffmpeg
        .input(rtmp_url)
        .output('pipe:', format='null')
        .run_async(pipe_stderr=True, pipe_stdout=True)
    )

    sei_pattern = re.compile(r'(?<=sei:)0x[0-9a-fA-F]+')

    try:
        # Continuously read the stderr to capture SEI messages
        while True:
            line = process.stderr.readline().decode('utf-8', errors='replace')
            if not line:
                break

            sei_matches = sei_pattern.findall(line)
            for sei in sei_matches:
                print(f"SEI Data: {sei}")

    except KeyboardInterrupt:
        print("Stopping SEI extraction...")
    finally:
        process.terminate()

def start_extraction():
    rtmp_url = entry.get()
    if not rtmp_url:
        messagebox.showwarning("Warning", "Please enter a valid RTMP URL.")
        return

    root.destroy()  # Close the tkinter window
    extract_sei_from_rtmp(rtmp_url)

# Create the main tkinter window
root = tk.Tk()
root.title("RTMP Stream SEI Extractor")

# Create a label and entry for the RTMP URL
label = tk.Label(root, text="Enter RTMP URL:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# Create a button to start SEI extraction
button = tk.Button(root, text="Start Extraction", command=start_extraction)
button.pack(pady=10)

# Run the tkinter main loop
root.mainloop()
