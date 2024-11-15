import cv2
import requests
import numpy as np

# URL of the video feed endpoint
url = "http://127.0.0.1:5000/video_feed"  # Replace with your IP if needed

# Open the video feed as a stream
response = requests.get(url, stream=True)

if response.status_code == 200:
    print("Successfully connected to video feed")
    
    # Read the frames from the video feed
    bytes_data = b''  # Initialize an empty bytes object to collect frame data
    
    for chunk in response.iter_content(chunk_size=1024):
        bytes_data += chunk  # Append each chunk to the bytes_data
        
        # Look for the frame boundary and split
        a = bytes_data.find(b'\xff\xd8')  # Start of JPEG
        b = bytes_data.find(b'\xff\xd9')  # End of JPEG
        
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]  # Extract the JPEG frame
            bytes_data = bytes_data[b+2:]  # Reset bytes_data after each frame

            # Convert the bytes to an image
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Display the frame
            cv2.imshow("Video Feed", frame)

            # Press 'q' to exit the video display
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

else:
    print("Failed to connect to video feed:", response.status_code)
