The original project is an offline video indexing + online visual retrieval system

The pipeline attempting to be reconstructed looks like:


Surveillance Video -> frame preprocessing -> background subtraction -> moving regions -> find contours -> multi object tracking -> feature extraction -> store in db

Image query -> similar feature extraction -> distance calculation of features -> sort -> retrieve timestamps + thumbnails + video previews. 

Consider each of the pipeline stages described in full:

## Video Preprocessing
---
- Get the original resolution of the video ```W_orig x H_orig```
- Resize video so that width = 200, and the height maintains some aspect ration calculated as: 
```
new_width = 200
img_aspect_ratio = W_orig/H_orig

new_height = int(200 * img_aspect_ratio)
```
## 2. Background Subtraction
- Used ViBe background-subtraction algorithm from pybgs package. 
- After doing the background subtraction we get the moving regions as a binary image

## 3. Find Contours
- The binary image from the previous step is passed to ```cv2.findContours```. Specifically using external contours only and *cv2.CHAIN_APPROX_NONE* for the contours approximation
- Then for each contour found we find its area and only keep the contours whose area is >=100

## 3.1 Maping detections to original resolution
- Maintain a scale factor so that each contour found is mapped back to the original resolution image
- Something like:
```
scale_x = new_width/ W_orig

scale_y =  new_height/H_orig

```
- Then using the scales, each valid contour detected in the resized image, it's co-ordinates are divided by those scale factors to obtain co-ordinates in the original frame
- the we use the contours to find bounding rectangles and centroids
- The **centroid** calculation step is done by finding the mean of all the contour points, and not using the moments? perhaps at the time I didn't know about moments. Worth investigating further

## 4. Object Tracking
- Uses a kalman filter
- Some values that might be of concern
```
distance threshold = 10
maximum skipped frames = 25
starting object ID = 1
```
- No idea about all this... Perhaps it will show itself as we do the implementation. 

\<see the chatgpt chat for more info description on this \>

## 5. Feature extraction
- For each tracked object, the following descriptors are extracted:
	+ Fourier shape descriptor
	+ colour descriptors
- Saved finally as the mean of both, fourier_descriptor/n, colour_descriptor/n

How the process of feature extraction is undertaken:
- When an object is first observed, we extract:
	+ shape descriptor
	+ colour descriptor
	+ a thumbnail
	+ Classify the object
- For every subsequent matched observation, we extract:
	+ shape descriptor
	+ colour descriptor
- The thumbnail and classifier aren't repeatedly recomputed possibly to save on processing time.
- I don't understand this part, (if a track isn't matched in a frame):
	+ No descriptor is added,
	+ kalman filter predicts forward
	+ draw is disabled for that frame.
	
## 5.1 colour descriptor
- It uses the HSV colour space, using bins = (8, 12, 3)
- The object ROI is converted from BGR to HSV and divided into four corner regions and a central ellipse
- For each region, a histogram is calculated for each region, then another histogram is calculated for the central ellipse. 
- The 5 histograms are then normalised, flattened and concatenated. 
- Histogram ranges used are: 
	+ Hue (0 - 180)
	+ Saturation (0 - 256)
	+ Value (0 - 256)
	+ with bins (8,12,3) whatever the hell that means
	
## 5.2 Fourier shape descriptor
A mini pipeline for:
binary/contour image -> largest external contour -> sample contour to 64 points -> centroid-distance signature -> dft -> magnitude -> normalisation

- Centroid distance signature ```sqrt((x-cx)**2 + (y - cy)**2))```
- Contour is sampled to 64 points
- A complex DFT is calculated
- Magnitude of each frequency component is taken
- The DC component is used to normalise the remaining coefficients, retaining the first half of the spectrum.

---
# Query Image Processing
- Load query image as BGR
- Convert to grayscale
- Threshold (default threshold is the otsu threshold), and then user can be able to manually adjust the threshold. 
- Convert to binary image
- Colour descriptors are then extracted from the colour image
- Shape descriptor is extracted from the binary query image
- The user can then select to search using colour only descriptor, shape only descriptor, or both. 

# Object Classification
---
A squeezenet1_1 model is used. It has 5 categories. (I believe it was chosen then, because it provided faster execution on the machine the student had at the time)

The prediction pipeline is as you would image:
- Resize image to (224,224)
- convert to Pytorch Tensor
- move to CUDA if available
- Run SqueezeNet
- take maximum prediction
- apply softmax
- Take classification if confidence >= 0.85 else classify as **Other**

## Database Saving strategy
---
- Each extractions are placed in some form of cache.
- Once the cache reaches around 2000 items, they are saved in batch to the database

# Retrieval
---
After getting the query_colour_vector, and query_shape_vector:
- The euclidean distance is used to compare between the vectors stored in the database
```
colour_distance = euclidean(query_colour_vector, db_colour_vector)
shape_distance = euclidean(query_shape_vector,db_shape_vector)

#If both descriptors are being used, we calculate the final distance as 
final_distance =  0.5*colour_distance + 05*shape_distance
```
- The final_distance is then sorted in ascending order
- There is also an option for filtering by category e.g. (Person, Bike, Car, Bus, Lorry, Other, ALL)

# Search Result behaviour
---
- The user interface displays upto 10 records. 
- Each record containing a thumbnail, start time, end time, video preview, option to use thumbnail as new query

## Thumbnail Refinement
- A retrieved object's thumbnail can itself become the query image to try and refine the search results. 
