import cv2

# RTSP stream URL
rtsp_url = 'rtsp://vtNgyn:Lsv3uvfY@192.168.0.237/ch0_0.h264'  # Modify with your camera's RTSP URL

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url)

# Check if the camera opened successfully
if not cap.isOpened():
    print('Error: Could not open camera.')
    exit()

# Loop to continuously read frames and display them
while True:
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print('Error: Could not read frame.')
        break

    # Display the frame
    cv2.imshow('RTSP Stream', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
