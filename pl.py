import asyncio
import cv2
import websockets
import base64

# Set up video capture with the USB camera (usually /dev/video0 on a Pi)
video_capture = cv2.VideoCapture(0)  # Use 0 or change to the camera ID if needed

async def video_stream(websocket, path=None):  # Added 'path=None' to avoid the error
    while True:
        # Capture frame-by-frame
        success, frame = video_capture.read()
        if not success:
            break

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        # Convert to base64 to send over WebSocket as a text message
        frame_data = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the client
        await websocket.send(frame_data)
        await asyncio.sleep(0.05)  # Adjust the delay to control the frame rate

async def main():
    async with websockets.serve(video_stream, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
