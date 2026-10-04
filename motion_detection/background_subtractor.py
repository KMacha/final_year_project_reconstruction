import cv2

class BackgroundSubtractor:
    def _initialise_background_subtractor(self,type_="mog2",detect_shadows:bool=True):
        match type_:
            case "mog2":
                return cv2.createBackgroundSubtractorMOG2(detectShadows = detect_shadows)
            case _:
                return cv2.createBackgroundSubtractorMOG2(detectShadows = detect_shadows)

    def __init__(self,type_="mog2",detect_shadows:bool=True):
        self._background_subtractor = self._initialise_background_subtractor(
            type_ = type_,
            detect_shadows = detect_shadows
        )

        self._morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))

    def get_motion_image(self,img:'np.ndarray',thresh_val:int=129)->'np.ndarray':
        gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        gray_img = cv2.GaussianBlur(gray_img,(3,3),0)

        fg_mask = self._background_subtractor.apply(gray_img)

        _,thresh_img = cv2.threshold(fg_mask,thresh_val,255,cv2.THRESH_BINARY)
        #thresh_img = cv2.medianBlur(thresh_img,3)

        #thresh_img = cv2.morphologyEx(thresh_img,cv2.MORPH_OPEN,self._morph_kernel)
        thresh_img = cv2.morphologyEx(thresh_img,cv2.MORPH_CLOSE,self._morph_kernel)

        return thresh_img
