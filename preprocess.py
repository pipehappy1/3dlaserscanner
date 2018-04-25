import imageio
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, stats
from skimage.filters import frangi, hessian
from meta import Meta

class Preprocess:
    def __init__(self, video_url):
        self.meta = Meta()
        self.meta.video = video_url

    def preprocess(self):
        reader = imageio.get_reader(self.meta.video)
        frame_acounts = reader.get_length()
        fps = int(reader.get_meta_data()['fps'])

        frame100 = reader.get_data(100)
        (height, width, channel) = frame100.shape

        self.meta.frame_acounts = frame_acounts
        self.meta.fps = fps
        self.meta.height = height
        self.meta.width = width
        self.meta.channel = channel

        print('[info] frame_acounts: {}'.format(frame_acounts))
        print('[info] fps: {}'.format(fps))
        print('[info] height: {}'.format(height))
        print('[info] width: {}'.format(width))
        print('[info] channel: {}'.format(channel))

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

        self.meta.mask_top = mask_top
        self.meta.mask_bottom = mask_bottom
        self.meta.mask_left = mask_left
        self.meta.mask_right = mask_right

        print('[info] mask_top: {}'.format(mask_top))
        print('[info] mask_bottom: {}'.format(mask_bottom))
        print('[info] mask_left: {}'.format(mask_left))
        print('[info] mask_right: {}'.format(mask_right))

        mask_frame = np.zeros((height, width, 3), dtype=np.int)
        mask_frame[mask_top:mask_bottom, mask_left:mask_right, :] = 1
        
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
        period = int(np.round(np.mean(period_ends[1:] - period_ends[:-1])))
        self.meta.period = period

        print('[info] period: {}'.format(period))

        try:
            self.meta.write()
        except Exception:
            print('[error] meta writing error!')

        return self.meta
