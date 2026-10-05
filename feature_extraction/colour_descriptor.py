import cv2
import numpy as np

def get_local_colour_hist(image:np.ndarray,mask:np.ndarray|None = None,n:int=3)->np.ndarray:
    hsv_img = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

    if mask is None:
        ys = image.shape[0]

        vals = np.linspace(0,ys,n+1).astype(int)
    else:
        ys = np.where(mask!=0)[0]

        vals = np.linspace(ys.min(),ys.max(),n+1).astype(int)

    collected_hist=list()
    for i in range(n):
        if mask is None:
            area_mask = np.zeros(shape=hsv_img.shape[:-1],dtype=np.uint8)
            area_mask[vals[i]:vals[i+1]] = 1
        else:
            area_mask = np.zeros_like(mask)
            area_mask[vals[i]:vals[i+1]] = mask[vals[i]:vals[i+1]]

        hist = cv2.calcHist([hsv_img],[0,1],area_mask,[8,8],[0,180,0,256])
        cv2.normalize(hist,hist,alpha=1.0,beta=0,norm_type=cv2.NORM_L1)
        collected_hist.append(hist.flatten())

    return np.concatenate(collected_hist)

def get_colour_descriptor(frame:np.ndarray,contours,images_bboxes:list[tuple])->list[np.ndarray]:
    local_colour_descriptor = list()

    full_mask = np.zeros_like(frame,dtype=np.uint8)
    cv2.drawContours(full_mask,contours,-1,(255,255,255),thickness=cv2.FILLED)

    full_mask = cv2.cvtColor(full_mask,cv2.COLOR_BGR2GRAY)


    for (x,x_1,y,y_1) in images_bboxes:
        image = frame[y:y_1,x:x_1]
        image_mask = full_mask[y:y_1,x:x_1]

        local_colour_descriptor.append(
            get_local_colour_hist(
                image = image,
                mask = image_mask
            )
        )

    return local_colour_descriptor
