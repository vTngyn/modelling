import cv2
from otherLibs.sort.sort import Sort

# Load the pre-trained Haar Cascade face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

rtsp_url = 'rtsp://vtNgyn:Lsv3uvfY@192.168.0.237/ch0_0.h264'

# Initialize the webcam
#video_capture = cv2.VideoCapture(0)
video_capture = cv2.VideoCapture(rtsp_url)

# Initialize the SORT tracker
tracker = Sort()

captured_faces = {}  # Dictionary to store captured faces for each person

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform face detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Update the SORT tracker with detected faces
    trackers = tracker.update(faces)

    # Iterate through tracked faces
    for person_id, (x, y, w, h) in enumerate(trackers):
        x, y, w, h = int(x), int(y), int(w), int(h)

        # Capture the face region
        face = frame[y:y+h, x:x+w]

        # Check if this person's face has not been captured yet
        if person_id not in captured_faces:
            # Save the face for this person
            captured_faces[person_id] = face

        # Draw bounding box and person ID
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f'Person {person_id}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop when the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV window
video_capture.release()
cv2.destroyAllWindows()
