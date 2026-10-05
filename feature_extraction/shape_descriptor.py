import cv2
import numpy as np
import scipy

from feature_extraction.contour_sampler import sample_contour_points

def get_fourier_descriptor(contour,total_samples:int=64,shape_signature = "centroid"):
    moments = cv2.moments(contour)
    cx = int(moments['m10']/moments['m00'])
    cy = int(moments['m01']/moments['m00'])

    centroid = np.array((cx,cy))

    sampled_contour_points = sample_contour_points(contour_points = contour.squeeze(),total_samples=total_samples)

    if shape_signature == "centroid":
        single_d_contour_points = np.sqrt(np.sum(np.square(sampled_contour_points - centroid),axis=-1))

        #take only the magnitudes and make it scale invariant
        fourier_descriptor = np.abs(scipy.fft.rfft(single_d_contour_points))
        fourier_descriptor = fourier_descriptor[1:]/fourier_descriptor[0]
    else:
        #we try out the complex shape signature

        #subtract centroid to eliminate effect of bias
        sampled_contour_points-=centroid

        z = sampled_contour_points[:,0] + 1j * sampled_contour_points[:,1]

        #take only the magnitude and make it scale invariant
        fourier_descriptor = np.abs(scipy.fft.fft(z))
        fourier_descriptor = fourier_descriptor[2:]/fourier_descriptor[1]

    return fourier_descriptor

def get_fourier_descriptors(contours:list[np.ndarray])->list(np.ndarray):
    #fourier_descriptors = [get_fourier_descriptor(contour) for contour in contours]

    #return fourier_descriptor

    return [get_fourier_descriptor(contour) for contour in contours]
