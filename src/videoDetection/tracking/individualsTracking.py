import cv2
import numpy as np

rtsp_url = 'rtsp://vtNgyn:Lsv3uvfY@192.168.0.237/ch0_0.h264'

# Load YOLO model and pre-trained weights
# https://github.com/AlexeyAB/darknet
yoloweightFile="../../../resources/models/YoloV4/yolov4.weights"
yoloCfgFile="../../../resources/models/YoloV4/yolov4.cfg"
yolo_model = cv2.dnn.readNet(yoloweightFile, yoloCfgFile)
#https://github.com/pjreddie/darknet/blob/master/data/coco.names
cocoNames = "../../../resources/models/YoloV4/coco.names"
with open(cocoNames, "r") as f:
    classes = f.read().strip().split('\n')

# Get output layer names
layer_names = yolo_model.getUnconnectedOutLayersNames()

# Load the video
video_path = 'path/to/your/video.mp4'  # Replace with the path to your video file
# cap = cv2.VideoCapture(video_path)
cap = cv2.VideoCapture(rtsp_url)

# Check if the video file is successfully opened
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Define the codec and create VideoWriter object for output video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
i=0
while True:
    print(f"read another frame : {i}")
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]

    # Detect objects (persons in this case) in the frame
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
    yolo_model.setInput(blob)
    outputs = yolo_model.forward(layer_names)

    # Process each detected object
    for output in outputs:
        for obj in output:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5 and class_id == 0:  # 0 is the class_id for 'person'
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                w = int(obj[2] * width)
                h = int(obj[3] * height)

                # Get the top-left corner coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Draw a bounding box and label around the person
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, 'Person', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Write the frame with the bounding boxes to the output video
    print("frame written")
    out.write(frame)

    # Display the resulting frame
    print("show next frame")
    cv2.imshow('Video', frame)

    i+=1

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and writer objects
cap.release()
out.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
