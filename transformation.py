import imageio
import numpy as np
from scipy import ndimage, stats

class Transformation:
    def __init__(self, metadata=None, video=None):
        if metadata is not None:
            self.meta = metadata
        elif video is not None:
            try:
                self.meta.video = video
                self.meta.read()
            except Exception:
                print('[error] cannot read metadata.')
        else:
            raise ValueError('transformation needs either metadata or video.')
                
    def transform(self):
        slope_window_top = int(self.meta.height*0.75)
        slope_window_bottom = self.meta.height
        slope_window_left = 50
        slope_window_right = int(self.meta.width*0.25)
        
        self.meta.slope_window_top = slope_window_top
        self.meta.slope_window_bottom = slope_window_bottom
        self.meta.slope_window_left = slope_window_left
        self.meta.slope_window_right = slope_window_right

        print('[info]slope_window_top: {}'.format(slope_window_top))
        print('[info]slope_window_bottom: {}'.format(slope_window_bottom))
        print('[info]slope_window_left: {}'.format(slope_window_left))
        print('[info]slope_window_right: {}'.format(slope_window_right))

        reader = imageio.get_reader(self.meta.video)
        frame100 = reader.get_data(100)

        slope_window = frame100[slope_window_top:slope_window_bottom, slope_window_left:slope_window_right, :]/255
        slope_window = np.sum(slope_window, axis=2)/3
        (base_line_y, base_line_x) = np.where(slope_window > np.mean(slope_window))
        slope, intercept, r_value, p_value, std_err = stats.linregress(base_line_x, base_line_y)

        self.meta.slope = slope

        print('[info]slope: {}'.format(slope))

        return self.meta


    
