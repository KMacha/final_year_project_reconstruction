import cv2
import numpy as np

from motion_detection.background_subtractor import BackgroundSubtractor
from motion_detection.three_frame_difference import ThreeFrameDifference

class Detector:
    def _initialise_detector(self,detector_type):
        match detector_type:
            case "background_subtractor":
                return BackgroundSubtractor()
            case "three_frame_difference":
                return ThreeFrameDifference()
            case _:
                raise Exception(f"No Such detector as {detector_type}")

    def __init__(self,detector_type="background_subtractor",contour_area_thresh:float=100):
        self._detector = self._initialise_detector(
            detector_type = detector_type
        )

        self._CONTOUR_AREA_THRESH = contour_area_thresh

    def suppression(self,contours:list[np.ndarray]):
        contours = sorted(contours,key=cv2.contourArea,reverse=True)
        bboxes = list()

        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            bboxes.append((x,y,x+w,x+h))

        remove,keep = list(),list()
        for i in range(len(bboxes)):
            if i in remove:
                continue

            keep.append(i)
            box_i_area = (bboxes[i][2] - bboxes[i][0]) * (bboxes[i][3] - bboxes[i][1])
            for j in range(i+1,len(bboxes)):
                intersection_tl_x = max(bboxes[i][0],bboxes[j][0])
                intersection_tl_y = max(bboxes[i][1],bboxes[j][1])

                intersection_br_x = min(bboxes[i][2],bboxes[j][2])
                intersection_br_y = min(bboxes[i][3],bboxes[j][3])

                width = max(0,(intersection_br_x - intersection_tl_x))
                height = max(0,(intersection_br_y - intersection_tl_y))

                intersection_area = width * height

                box_j_area = (bboxes[j][2] - bboxes[j][0]) * (bboxes[j][3] - bboxes[j][1])

                union_area = box_i_area + box_j_area - intersection_area

                iou = intersection_area/union_area

                if iou > 0.1:
                    remove.append(j)


            return [contour for i,contour in enumerate(contours) if i in keep]



    def _detect_moving_objects(self,motion_image:np.ndarray,contour_area_thresh:float|None=None):
        contour_area_thresh = contour_area_thresh if contour_area_thresh is not None else self._CONTOUR_AREA_THRESH

        contours,hierarchy = cv2.findContours(motion_image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

        contours = [contour for contour in contours if cv2.contourArea(contour) >= contour_area_thresh]

        #don't suppress it removes important contours
        #contours = self.suppression(contours)

        return contours

    def get_motion_image(self,bgr_img)->None|np.ndarray:
        return self._detector.get_motion_image(
            img = bgr_img
        )

    def get_motion_image_and_objects(self,bgr_img)->tuple:
        motion_img = self._detector.get_motion_image(img = bgr_img)
        contours = self._detect_moving_objects(motion_image = motion_img)

        return motion_img,contours
