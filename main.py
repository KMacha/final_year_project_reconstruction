#!/usr/bin/python
import time
import cv2

from motion_detection.detector import Detector
from feature_extraction.colour_descriptor import get_colour_descriptor
from feature_extraction.shape_descriptor import get_fourier_descriptors
from object_tracker.object_tracker import ObjectTracker

def get_detection_bboxes(contours,scale_x:float,scale_y:float)->tuple[list,list]:
    detections,detections_bboxes = list(),list()

    contours = [(contour/[scale_x,scale_y]).astype(int) for contour in contours]

    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        x_1 = x+w
        y_1 = y+h

        c_x = (x + x_1)/2
        c_y = (y + y_1)/2

        #x = int(x/scale_x)
        #y = int(y/scale_y)
        #w = int(w/scale_x)
        #h = int(h/scale_y)

        detections.append((c_x,c_y,w,h))
        detections_bboxes.append((x,x_1,y,y_1))


    return contours,detections,detections_bboxes


if __name__ == "__main__":
    #video_cap = cv2.VideoCapture("./assets/videos/overpass.mkv")
    video_cap = cv2.VideoCapture("./assets/videos/vtest.avi")
    #video_cap = cv2.VideoCapture("./assets/videos/pedestrian walking.mkv")

    width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    aspect_ratio = width/height

    new_width = 480
    new_height = int(new_width / aspect_ratio)

    scale_x = new_width/width
    scale_y = new_height/height


    print(f"orig: ({width}x{height}), new: ({new_width,new_height})")


    #detector_obj = Detector(detector_type="three_frame_difference")
    detector_obj = Detector(contour_area_thresh=50)
    tracker_obj = ObjectTracker()

    if video_cap.isOpened():
        start_time = time.perf_counter()
        while True:
            ret, frame = video_cap.read()

            if not ret: break

            frame_timestamp = video_cap.get(cv2.CAP_PROP_POS_MSEC)

            resized_frame = cv2.resize(frame,(new_width,new_height))

            #motion_img = detector_obj.get_motion_image(bgr_img = frame)
            motion_img,contours = detector_obj.get_motion_image_and_objects(bgr_img = resized_frame)

            #mapping the contours to the original size

            contours,detections,detections_bboxes = get_detection_bboxes(
                contours = contours,
                scale_x = scale_x,
                scale_y = scale_y
            )

            colour_descriptor = get_colour_descriptor(frame = frame,contours = contours,images_bboxes = detections_bboxes)
            shape_descriptor = get_fourier_descriptors(contours)

            tracker_obj.track(
                detections = detections,
                detected_bboxes = detections_bboxes,
                detected_colours_info = colour_descriptor,
                detected_shape_info = shape_descriptor,
                measurement_stds = [3.0,3.0,5.0,5.0],
                frame = frame,
                frame_timestamp = frame_timestamp
            )

            for (x,x_1,y,y_1) in detections_bboxes:
                cv2.rectangle(frame,(x,y),(x_1,y_1),(255,0,0),2)

            #contours = [(contour/[scale_x,scale_y]).astype(int) for contour in contours]
            cv2.drawContours(frame,contours,-1,(0,255,0))

            cv2.imshow("img",frame)
            if motion_img is not None:
                cv2.imshow("motion_img",motion_img)

            key = cv2.waitKey(1) & 0xff;

            if key == ord('q'): break


        video_cap.release()
        cv2.destroyAllWindows()

        #before finishing completely we save the last of the remaining tracks
        tracker_obj.save_object_tracks()

        end_time = time.perf_counter()

        duration = end_time - start_time
        print(f"Duration:{duration:.4f} seconds")


