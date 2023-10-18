import cv2

cap = cv2.VideoCapture('pipe:')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Process the frame as needed
    cv2.imshow('Camera Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
