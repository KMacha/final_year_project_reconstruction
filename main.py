#!/usr/bin/python
import time
import cv2

from motion_detection.detector import Detector


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

    if video_cap.isOpened():
        start_time = time.perf_counter()
        while True:
            ret, frame = video_cap.read()

            if not ret: break

            resized_frame = cv2.resize(frame,(new_width,new_height))

            #motion_img = detector_obj.get_motion_image(bgr_img = frame)
            motion_img,contours = detector_obj.get_motion_image_and_objects(bgr_img = resized_frame)

            #mapping the contours to the original size
            for contour in contours:
                x,y,w,h = cv2.boundingRect(contour)
                x = int(x/scale_x)
                y = int(y/scale_y)
                w = int(w/scale_x)
                h = int(h/scale_y)


                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

            contours = [(contour/[scale_x,scale_y]).astype(int) for contour in contours]
            cv2.drawContours(frame,contours,-1,(0,255,0))

            cv2.imshow("img",frame)
            if motion_img is not None:
                cv2.imshow("motion_img",motion_img)

            key = cv2.waitKey(0) & 0xff;

            if key == ord('q'): break

        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Duration:{duration:.4f} seconds")
        video_cap.release()
        cv2.destroyAllWindows()


