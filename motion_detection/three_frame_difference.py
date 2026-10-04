import cv2

class ThreeFrameDifference:
    def __init__(self):
        self._morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        self._dilation_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))

        self._diff_img_1 = None
        self._prev_gray_img = None

        self._thresh_val = 15

    def _get_difference_image(self,img_1,img_2,use_adaptive_threshold:bool=True):
        diff_img = cv2.absdiff(img_1,img_2)
        diff_img = cv2.medianBlur(diff_img,5)

        thresh_val = self._thresh_val
        if use_adaptive_threshold:
            thresh_val = 3 * diff_img.mean()
            thresh_val = self._thresh_val if thresh_val < self._thresh_val else thresh_val

        _,thresh_img = cv2.threshold(diff_img,thresh_val,255,cv2.THRESH_BINARY)

        thresh_img = cv2.dilate(thresh_img,self._dilation_kernel)

        return thresh_img

    def get_motion_image(self,img,thresh_val:int|None=15)->None|'np.ndarray':
        #remember for 3 frame differencing we need 3 images (prev, curr, next) to get the motion image
        #we then have diff_img_1 = abs(prev - curr)
        # diff_img_2 = abs(curr - next)
        #we want to try and make the code from the main to be as simple as possible so that it can simply call this method and we update all the 
        #needed images as needed...
        # Essentially, start with diff_img_1 and prev_img as None, we get the first image, we initialise it as prev_img.
        # when we get the second image, which is the 'curr_img', we get diff_img_1 between it and the prev_img, and set it to prev_img
        # then after that when we receive another image, this one acts like the 'next_img' and the 'prev_img' acts as the curr_img, so we use them to get diff_img_2
        # then we assign next_img to prev_img, and diff_img_2 to diff_img_1, so that we only calculate only diff_img_2 as diff_img_1 in the next turn will basically be the previous diff_img_2

        self._thresh_val = self._thresh_val if thresh_val is None else thresh_val

        if self._diff_img_1 is None:
            if self._prev_gray_img is None:
                self._prev_gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            else:
                gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

                self._diff_img_1 = self._get_difference_image(
                    img_1 = self._prev_gray_img,
                    img_2 = gray_img
                )

                self._prev_gray_img = gray_img

            return None

        gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        diff_img_2 = self._get_difference_image(
            img_1 = self._prev_gray_img,
            img_2 = gray_img
        )

        motion_img = cv2.bitwise_and(self._diff_img_1,diff_img_2)

        motion_img = cv2.morphologyEx(motion_img,cv2.MORPH_CLOSE,self._morph_kernel)
        motion_img = cv2.morphologyEx(motion_img,cv2.MORPH_OPEN,self._morph_kernel)

        self._diff_img_1 = diff_img_2
        self._prev_gray_img = gray_img


        return motion_img





