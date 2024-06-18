import cv2
from Sort.sort import *
from ultralytics import YOLO
from utils import get_car, read_license_plate, write_csv
import matplotlib.pyplot as plt

# load models
yolo = YOLO('yolov8n.pt')
license_plate_detector = YOLO('./models/license_plate_detector.pt')

# results dictionary
results = {}

# tracker object
tracker = Sort()

#load video
cap = cv2.VideoCapture('./sample_video.mp4')
vehicle_class_ids = [2,3,5,7]
ret, frame = cap.read()
frame_no = -1
while ret:
    ret, frame = cap.read()
    frame_no += 1
    if ret and frame_no < 10:
        
        results[frame_no] = {}
        
        detections = yolo(frame)[0]
        detections_ = [] # store vehicle detections
        
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, conf, class_id = detection
            
            if (int(class_id) in vehicle_class_ids):
                detections_.append([x1, y1, x2, y2, conf])
        
        # track the vehicles
        track_ids = tracker.update(np.array(detections_))
        
        # get license plate coordinates
        license_plate_detections = license_plate_detector(frame)[0]
        
        for license_plate in license_plate_detections.boxes.data.tolist():
            x1, y1, x2, y2, conf, class_id = license_plate
        
            # get the vehicle coordinates and ID based on the license plate coordinates
            car_x1, car_y1, car_x2, car_y2, car_id  = get_car((x1, y1, x2, y2), track_ids)
            
            # crop the license plate
            license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2)]
            
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            info, license_plate_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV) 
            
            # plt.imshow(license_plate_thresh, cmap='gray')
            # plt.show()  
            
            # read the license plate text
            license_plate_text, confidence = read_license_plate(license_plate_thresh)
            
            results[frame_no][car_id] = {'vehicle':{ 'coordinates': [car_x1, car_y1, car_x2, car_y2]},
                                         'license_plate' :{'coordinates': [x1, y1, x2, y2],
                                                           'text': license_plate_text,
                                                           'coordinates_confidence': conf,
                                                            'text_confidence': confidence}}
    else:
        break
#write results to a file
write_csv(results, './results.csv')                                                     
                      
        