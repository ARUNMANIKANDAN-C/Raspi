import cv2
import requests
import numpy as np

def fetch_frame(url="http://localhost:5000/get_frame"):
    """Fetch a single frame from the server."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Retrieve frame data from JSON response
        frame_hex = response.json().get('frame')
        if frame_hex:
            frame_bytes = bytes.fromhex(frame_hex)
            frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
            return frame
        else:
            print("Error: No frame data received")
    except Exception as e:
        print(f"Error fetching frame: {e}")
    return None

def stream_video(url="http://localhost:5000/video_feed"):
    """Stream video from the server."""
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print("Error: Unable to open video stream")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from stream")
            break
        
        cv2.imshow("Video Stream", frame)
        
        # Press 'q' to quit streaming
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("1: Fetch single frame")
    print("2: Stream video")
    choice = input("Select an option (1 or 2): ")

    if choice == "1":
        frame = fetch_frame()
        if frame is not None:
            cv2.imshow("Single Frame", frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    elif choice == "2":
        stream_video()
    else:
        print("Invalid choice")
