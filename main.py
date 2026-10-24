#!/usr/bin/python
import time
import yaml
import cv2

from motion_detection.detector import Detector
from feature_extraction.colour_descriptor import get_colour_descriptor
from feature_extraction.shape_descriptor import get_fourier_descriptors
from object_tracker.object_tracker import ObjectTracker

def get_configuration(config_file:str="./config.yaml")->dict:
    with open(config_file,'r') as file_obj:
        return yaml.safe_load(file_obj)

def scale_contours(contours,scale_factor)->list:
    return [(contour/scale_factor).astype(int) for contour in contours]

def get_scaled_detection_bboxes(contours,scale_factor:float)->list:
    detections_bboxes = list()

    upscaled_contours = [(contour/scale_factor).astype(int) for contour in contours]

    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        x_1 = x+w
        y_1 = y+h

        detections_bboxes.append((x,x_1,y,y_1))

    return detections_bboxes


def get_detection_bboxes(contours)->tuple[list,list]:
    detections,detections_bboxes = list(),list()

    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        x_1 = x+w
        y_1 = y+h

        c_x = (x + x_1)/2
        c_y = (y + y_1)/2

        detections.append((c_x,c_y,w,h))
        detections_bboxes.append((x,x_1,y,y_1))


    return contours,detections,detections_bboxes

def process_frame(
    orig_frame:'np.ndarray',
    frame_timestamp:float,
    detector_obj:Detector,
    tracker_obj:ObjectTracker,
    measurements_std_list:list = [3.0,3.0,10.0,10.0],
    resize_frame:bool = False,
    scale_factor:float = 1.0,
    draw:bool=False
)->tuple['np.ndarray'|None,'np.ndarray'|None]:
    #orig_frame is the original frame that hasn't become the working frame... (wow such a good explanation)

    #working_frame is the frame we are working on which might potentially be resized
    working_frame = orig_frame.copy()
    if resize_frame:
        working_frame = cv2.resize(orig_frame,fx=scale_factor,fy=scale_factor,interpolation=cv2.INTER_AREA)

    motion_img,contours = detector_obj.get_motion_image_and_objects(bgr_img = working_frame)

    #mapping the contours to the original size

    contours,detections,detections_bboxes = get_detection_bboxes(contours = contours)

    colour_descriptor = get_colour_descriptor(frame = working_frame,contours = contours,images_bboxes = detections_bboxes)
    shape_descriptor = get_fourier_descriptors(contours)

    #where upscaled means those that have been 'upscaled' to the original frame... Only applied for those whose working_frame is different from the 
    #original one.
    upscaled_bboxes = detections_bboxes
    if resize_frame:
        upscaled_bboxes = get_scaled_detection_bboxes(contours,scale_factor = scale_factor)

    working_frame = tracker_obj.track(
        detections = detections,
        detected_bboxes = detections_bboxes,
        detected_colours_info = colour_descriptor,
        detected_shape_info = shape_descriptor,
        measurement_stds = measurements_std_list,
        orig_bboxes = upscaled_bboxes,
        orig_frame = orig_frame,
        working_frame = working_frame,
        frame_timestamp = frame_timestamp
    )

    if draw:
        for (x,x_1,y,y_1) in detections_bboxes:
            cv2.rectangle(working_frame,(x,y),(x_1,y_1),(255,0,0),2)

        #contours = [(contour/[scale_x,scale_y]).astype(int) for contour in contours]
        cv2.drawContours(working_frame,contours,-1,(0,255,0))

        return working_frame, motion_img

    return None,None


if __name__ == "__main__":
    config = get_configuration(config_file = "./config.yaml")

    video_cap = cv2.VideoCapture(config["main"]["video_path"])

    #minimum resolution 1280 x 720
    MIN_WIDTH = config["main"]["min_width"]

    width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    approx_number_frames = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)

    resize_frame = False
    max_dim = max(width,height)

    #we have 1280 x 720 as the largest resolution we are going to use without resizing
    #if a frame is larger than it, we scale it to 1280 x 720
    scale_factor = 1.0
    if max_dim > MIN_WIDTH:
        resize_frame = True
        scale_factor = MIN_WIDTH/max_dim

    print(f"Resizing: {resize_frame}")

    #this is the standard deviations for the measurements (in this case detections)
    #to be used with the kalman filter
    measurements_std_list = config["main"]["measurements_stds"]


    #detector_obj = Detector(detector_type="three_frame_difference")
    detector_obj = Detector(
        detector_type = config["motion_detector"]["detector_type"],
        contour_area_thresh= config["motion_detector"]["contour_area_threshold"]
    )

    tracker_obj = ObjectTracker(
        tracker_config = config["object_tracker"],
        model_config = config["model"],
        db_config = config["db"],
        video_file_path = config["main"]["video_path"]
    )

    if video_cap.isOpened():
        start_time = time.perf_counter()

        processed_frames = 0
        while True:
            ret, frame = video_cap.read()

            if not ret: break

            frame_timestamp = video_cap.get(cv2.CAP_PROP_POS_MSEC)

            working_frame, motion_img = process_frame(
                orig_frame = frame,
                frame_timestamp = frame_timestamp,
                detector_obj = detector_obj,
                tracker_obj = tracker_obj,
                resize_frame = resize_frame,
                scale_factor = scale_factor,
                draw = config["main"]["show_gui"]
            )


            if config["main"]["show_gui"]:
                cv2.imshow("img",working_frame)
                if motion_img is not None:
                    cv2.imshow("motion_img",motion_img)

                key = cv2.waitKey(config["main"]["gui_speed"]) & 0xff;

                if key == ord('q'): break
            else:
                processed_frames+=1
                print(f"Processed [{processed_frames:,}/{approx_number_frames:,}]",end='\r',flush=True)


        video_cap.release()
        cv2.destroyAllWindows()

        #before finishing completely we save the last of the remaining tracks
        tracker_obj.save_object_tracks()

        end_time = time.perf_counter()

        duration = end_time - start_time
        print(f"\nDuration:{duration:.4f} seconds")


