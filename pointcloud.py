import stl
import matplotlib.pyplot as plt
import numpy as np
import imageio
from scipy import ndimage, stats
from skimage.filters import frangi, hessian
import os

class PointCloud:
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

    def save_stl(self, center_axis = 305):
        start_frame = 100
        period = self.meta.period

        mask_frame = np.zeros((self.meta.height,
                               self.meta.width,
                               self.meta.channel),
                              dtype=np.int)
        mask_frame[self.meta.mask_top:self.meta.mask_bottom,
                   self.meta.mask_left:self.meta.mask_right,
                   :] = 1

        
        masked_center = center_axis - self.meta.mask_left
        self.meta.center_axis = center_axis
        print('[info] center_axis: {}'.format(center_axis))

        slices = 120
        self.meta.slices = slices
        print('[info] slices: {}'.format(slices))
        frame_per_slice = int(self.meta.period/slices)

        frame_index = list(range(int(self.meta.period/frame_per_slice)))
        
        reader = imageio.get_reader(self.meta.video)

        file_name = os.path.basename(self.meta.video).split(os.path.extsep)[0]
        with open(os.path.join(os.path.dirname(self.meta.video), file_name+os.path.extsep+'xyz'), 'w') as wfh:
            for i in frame_index:
                print('[info] working on frame indexed at {}.'.format(i))
                tindex = start_frame + i*frame_per_slice
                tframe = reader.get_data(tindex)
                tframe = tframe[self.meta.mask_top:self.meta.mask_bottom,
                                self.meta.mask_left:self.meta.mask_right,
                                :]/255
                tframe = np.sum(tframe, axis=2)/self.meta.channel
                tframe = 1 - tframe ## <-- due to a skimage bug#2700
                tframe = frangi(tframe)
            
                tframe = ndimage.affine_transform(tframe,
                                                  np.array([[1,self.meta.slope],
                                                            [0, 1]]))
            
                tframe = (tframe-np.min(tframe))/ (np.max(tframe) - np.min(tframe)
                                                 + 0.0001)
                
                tframe = 1 - tframe ## <-- due to a skimage bug#2700
                tframe = frangi(tframe)
            
                tframe = (tframe-np.min(tframe))/ (np.max(tframe) - np.min(tframe)
                                                 + 0.0001)
            
                tframe[tframe < 0.1] = 0
                tframe = ndimage.grey_erosion(tframe, size=2)
                

                tframe = tframe[:,:masked_center]
                tframe = np.fliplr(tframe)

                #plt.imshow(tframe)
                #plt.show()
                
                points = np.where(tframe>0)

                print(points[1].size/tframe.size)

                #print("{}, {}".format(np.cos(i/len(frame_index)*np.pi*2), np.sin(i/len(frame_index)*np.pi*2)))
            
                x = np.cos(i/len(frame_index)*np.pi*2)*(points[1])
                y = np.sin(i/len(frame_index)*np.pi*2)*(points[1])
                z = points[0]

                print(x.shape)
                for pindex in range(x.size):
                    wfh.write('{} {} {}\n'.format(x[pindex], y[pindex], z[pindex]))
            



                
if __name__ == "__main__":
    example_video = '/home/yguan/workspace/3dLaserScanner/data/motor.mp4'
    import meta
    meta1 = meta.Meta()
    meta1.video = example_video
    meta1.read()
    
    mesh = PointCloud(meta1)
    mesh.save_stl()
