import os

class Meta:
    meta_postfix = 'meta'

    data_type = {'video':str,
                 'frame_acounts':int,
                 'fps':int,
                 'height':int,
                 'width':int,
                 'channel':int,
                 'mask_top':int,
                 'mask_bottom':int,
                 'mask_left':int,
                 'mask_right':int,
                 'period':int,
                 'slope_window_top':int,
                 'slope_window_bottom':int,
                 'slope_window_left':int,
                 'slope_window_right':int,
                 'slope':float,
                 'center_axis':int,
                 'slices':int}
    
    def __init__(self):
        self.video = ''
        self.frame_acounts = -1
        self.fps = -1
        self.height = -1
        self.width = -1
        self.channel = -1
        self.mask_top = -1
        self.mask_bottom = -1
        self.mask_left = -1
        self.mask_right = -1
        self.period = -1
        self.slope_window_top = -1
        self.slope_window_bottom = -1
        self.slope_window_left = -1
        self.slope_window_right = -1
        self.slope = 0.0
        self.center_axis = -1
        self.slices = -1

    def write(self):
        file_name = os.path.basename(self.video).split(os.path.extsep)[0]
        with open(os.path.join(os.path.dirname(self.video), file_name+os.path.extsep+Meta.meta_postfix), 'w') as wfh:
            for k, v in self.data_type.items():
                wfh.write('{}:{}\n'.format(k, self.__dict__[k]))

    def read(self):
        file_name = os.path.basename(self.video).split(os.path.extsep)[0]
        with open(os.path.join(os.path.dirname(self.video), file_name+os.path.extsep+Meta.meta_postfix), 'r') as rfh:
            line = rfh.readline()
            while line:
                line = line.strip()
                (name, value) = line.split(':')
                print("[info] {}:{}".format(name,value))
                self.__dict__[name] = Meta.data_type[name](value)
                line = rfh.readline()


    
