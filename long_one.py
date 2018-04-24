import imageio
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, stats
from skimage.filters import frangi, hessian


example_video = '/home/yguan/workspace/3dLaserScanner/data/motor.mp4'

reader = imageio.get_reader(example_video)
frame_acounts = reader.get_length()
fps = reader.get_meta_data()['fps']

# process steps:
# 1. find those read lines in each frame(remove background).
# 1+ find start and end frame for each iteration (a possible average over multiple iteration).
# 2. form a flat plot.
# 3. roll the flat plot into 3d plot.

frame100 = reader.get_data(100)
(height, width, channel) = frame100.shape

# 1. find those red lines in each frame(remove background).
# 1.a find mean and variance at each pixel,
# 1.b then histogram and threshold the variance.
# 1.c then get receptive field.
# 1.d find iteration length of the video.
# 1.e find those line by ridge detection.
all_mean = np.zeros((height, width, channel))
all_variance = np.zeros((height, width, channel))

for i, im in enumerate(reader):
    all_mean += im/255
    all_variance += (im/255)*(im/255)


all_mean /= frame_acounts
all_variance /= frame_acounts
all_std = np.sqrt(all_variance) - all_mean

maskr = all_std[:,:,0] > 0.02
maskg = all_std[:,:,1] > 0.02
maskb = all_std[:,:,2] > 0.02

common_mask = np.logical_or(maskr, maskg, maskb)

erosed_mask = ndimage.binary_erosion(common_mask, structure=np.ones((5,5))).astype(common_mask.dtype)

border = int(np.min((height, width))*0.03)

mask_top = np.min(np.where(erosed_mask)[0]) - border
mask_bottom = np.max(np.where(erosed_mask)[0]) + border
mask_left = np.min(np.where(erosed_mask)[1]) - border
mask_right = np.max(np.where(erosed_mask)[1]) + border

mask_frame = np.zeros((height, width, 3), dtype=np.int)
mask_frame[mask_top:mask_bottom, mask_left:mask_right, :] = 1

## the following is for dev only
writer = imageio.get_writer('/home/yguan/workspace/3dLaserScanner/tmp.mp4', fps=fps)
for im in reader:
    writer.append_data(im*mask_frame)

writer.close()

## end of dev only

masked_frame100 = frame100/255*mask_frame
distance = np.empty(frame_acounts)
for i, im in enumerate(reader):
    maked_im = im/255*mask_frame
    distance[i] = np.sqrt(np.sum((masked_frame100 - maked_im) * (masked_frame100 - maked_im)))

average_n = 500
cumsum, moving_aves = [0], []

for i, x in enumerate(distance, 1):
    cumsum.append(cumsum[i-1] + x)
    if i >= average_n:
        moving_ave = (cumsum[i] - cumsum[i-average_n])/average_n
        moving_aves.append(moving_ave)

mini_threshold = 30.0
a = np.array(moving_aves)
minimums = (np.r_[True, a[1:] < a[:-1]] & np.r_[a[:-1] < a[1:], True]) & (a < mini_threshold)
period_ends = np.where(minimums==True)[0][1:]
period = np.round(np.mean(period_ends[1:] - period_ends[:-1]))

ridge_frame100 = frame100[mask_top:mask_bottom, mask_left:mask_right, :]/255
ridge_frame100 = np.sum(ridge_frame100, axis=2)/3
ridge_frame100 = 1 - ridge_frame100
ridge_frame100 = frangi(ridge_frame100)

## the following is for dev only.
writer = imageio.get_writer('/home/yguan/workspace/3dLaserScanner/ridge.mp4', fps=fps)
for i, im in enumerate(reader):    
    tframe = im/255*mask_frame
    #tframe = tframe[mask_top:mask_bottom, mask_left:mask_right, :]
    tframe = (tframe[:,:,0] + tframe[:,:,1] + tframe[:,:,2])/3
    tframe = 1 - tframe
    tframe = frangi(tframe)
    tmax = np.max(tframe)
    tmin = np.min(tframe)
    tframe = (tframe - tmin)/ (tmax - tmin + 0.00001) * 255
    tframe = np.stack((tframe, tframe, tframe), axis=2)
    writer.append_data(tframe)

writer.close()

## end of dev only


# 2. form a flat plot.
# 2.a detect the flat base line
# 2.b use the flat base line to transform to side view by a simple cosine transformation.
quad_frame = frame100[int(height*0.75):height, 50:int(width*0.25), :]/255
quad_frame = np.sum(quad_frame, axis=2)/3
(base_line_y, base_line_x) = np.where(quad_frame > np.mean(quad_frame))
slope, intercept, r_value, p_value, std_err = stats.linregress(base_line_x, base_line_y)

side_view100 = ndimage.affine_transform(ridge_frame100, np.array([[1,slope],[0, 1]]))

## for dev only
writer = imageio.get_writer('/home/yguan/workspace/3dLaserScanner/side_view.mp4', fps=fps)
for i, im in enumerate(reader):    
    tframe = im/255*mask_frame
    #tframe = tframe[mask_top:mask_bottom, mask_left:mask_right, :]
    tframe = (tframe[:,:,0] + tframe[:,:,1] + tframe[:,:,2])/3
    tframe = 1 - tframe
    tframe = frangi(tframe)
    tframe = ndimage.affine_transform(tframe, np.array([[1,slope],[0, 1]]))
    tmax = np.max(tframe)
    tmin = np.min(tframe)
    tframe = (tframe - tmin)/ (tmax - tmin + 0.00001) * 255
    tframe = np.stack((tframe, tframe, tframe), axis=2)
    writer.append_data(tframe)

writer.close()
## end of dev only


# 3. roll the flat plot into 3d plot.
# 3.a find the center axis.
# 3.b roll it.
# 3.c create 3d mesh.


