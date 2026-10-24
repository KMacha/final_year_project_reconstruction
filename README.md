# INSTALLATION
---
Ensure you have uv installed https://docs.astral.sh/uv/getting-started/installation/

If on Arch Linux, as simple as ``` sudo pacman -Syu uv```

```
#change to the root directory i.e. where the gui.py file is at
uv run gui.py

or

uv sync
uv run --no-sync gui.py

```

# Motivation
---
Wanted to see how much I can recreate my final year project (done approximately 5 years ago) before trying to improve it to make it better. 

Perhaps also while offering a better documentation than the less inexperienced me from 5 years ago... But on looking at the code, it does use som staff that is making current me kinda just stare open mouthed, wondering how I was able to understand all that while at the same time I was studying.

I predict, it is going to be easier this time round, since I am not learning a lot of new concepts... And the reconstruction is constrained to use similar algorithms used in the past project

See the **original project** at:  <a href="https://github.com/KMacha/Final_year_project-Surveillance-Video-Search-and-Retrieval-.git"> final_year_project_surveillance_video_search_and_retrieval </a>

# Description
---
Implementing an archived surveillance video search and retrieval... 

The original work was using content based image retrieval. Hence this project reconstructs it. See implementation plan in docs


## Differences from Original
While I was aiming at a faithful reconstruction. Some libraries used a while ago were a pain to install currently or were unavailable, and some implementation produced worse results when implemented as were, hence for those I changed them.

Some of the changes include:
- The original work only used the centroid of the object as the measurement, in this reconstruction, after a couple of experimentation, changed the measurements to both the centroid and the width and height, while also changing the state to include the velocities for width and height to try and capture for changing width and height as the object moves away from the camera and as it comes closer to the camera.
- The original work used the pybgs library and particularly the ViBE background subtractor for motion detection. Using the current python version 3.14.8. I was unable to install the pybgs library. And I was not particularly feeling motivated to implement it myself. Hence just stack with the MOG offered by OpenCv.
- The Original work, which was used on a laptop with a low end gpu and a not so good processor did some preprocessing to the original image and resized it to smaller. and then rescaled the image after processing to get the 'original' contours. On investigation, this post processing to get the 'original' contours was causing the contour shape to be more distorted due to the upscaling. In this reimplementation on a desktop with a better processor. On investigation, it was seen as better to have a processing minimum size of 1280 x 720, and with that resolution it was used for everything apart from the final part of getting the object for classification which the original image was used, in the hopes of if the original image is of a higher resolution it would be better.
- The Original work used TKinter. I used PySide6.

# Testing
---
For the testing of the current Implementation, see the docs/testing

# Challenges & Future Improvements
---
## Challenges
- The MOG2 background subtractor wasn't performing particularly well, i.e. not really detecting complete moving objects, and since this is the first part of the pipeline, it distorts everything else:
	+ Since the motion detection pipeline isn't working well... Then we cannot get proper contours for the shape, we also cannot be able to get a proper mask for getting the colour features. Which in turn degrades the whole process
	+ Since the motion detection pipeline isn't working well and we cannot get proper contours and objects, then the tracker suffers too, and thus in one video we end up tracking a lot of objects because one object is detected differently in muliple consecutive frames. 
-  The Original work used a squeezenet model as the classifier... While it makes sense to use the squeezenet model since at the time the machine wasn't very capable with a low end gpu, hence using the squeezenet model offered a speed up, but it offered a speed up while having misclassifications. 
-  How to query: 
	+  This is perhaps the biggest challenge after the motion detector. The methods of querying right now are either using shape features, colour features or search using the object classification and then refine.
	+  Querying using shape features or colour features, requires the user to insert an image or sketch an image (not implemented). If a user inserts a very detailed image, we suffer from a similar issue to the motion detector. We cannot be able to get a proper binary (thresholded) image, from which to find contours, which in turn again means then the shape features and colour features, might not be accurate, which means the results gotten might not be accurate too.
	+  Querying using the object labels while nice, due to the use of the Squeezenet model, some objects are misclassified, hence we get bad results
	
---
## Future Improvements
### Assumptions
The biggest assumption is that improving the MOG2 background subtractor or rather improving the motion detection algorithm, will have better consequences down the whole pipeline

### Future Work
1. Improve the motion detector, either perhaps a machine learning background subtractor or object detection or motion segmentation.
2. Investigate using a larger classifier and perhaps if it is slower then now we know methods to try and fasten the inference.
3. Implement using sketching, which might help us to be more imaginative on how to do the querying
4. Implement perhaps a search/query by dominant colour(s). 
5. New project perhaps where we focus on using descriptions to search rather than using an image. 
6. Currently the gui is a use once kind of thing, i.e. after doing offline processing to a new table that doesn't exist, if you want to then do querying or if you want to do processing on another video, then you have to restart the gui, or rather you have to first quit and come back