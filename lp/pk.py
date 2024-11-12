import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Capture a single frame
ret, frame = cap.read()
if ret:
    cv2.imwrite("test_frame.jpg", frame)
    print("Frame saved as test_frame.jpg")
else:
    print("Failed to capture frame")

cap.release()
