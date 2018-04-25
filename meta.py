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
                 'period':int}
    
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

    def write(self):
        file_name = os.path.basename(self.video).split(os.path.extsep)[0]
        with open(os.path.join(os.path.dirname(self.video), file_name+os.path.extsep+Meta.meta_postfix), 'w') as wfh:
            wfh.write('video:{}\n'.format(self.video))
            wfh.write('frame_acounts:{}\n'.format(self.frame_acounts))
            wfh.write('fps:{}\n'.format(self.fps))
            wfh.write('height:{}\n'.format(self.height))
            wfh.write('width:{}\n'.format(self.width))
            wfh.write('channel:{}\n'.format(self.channel))
            wfh.write('mask_top:{}\n'.format(self.mask_top))
            wfh.write('mask_bottom:{}\n'.format(self.mask_bottom))
            wfh.write('mask_left:{}\n'.format(self.mask_left))
            wfh.write('mask_right:{}\n'.format(self.mask_right))
            wfh.write('period:{}\n'.format(self.period))

    def read(self):
        file_name = os.path.basename(self.video).split(os.path.extsep)[0]
        with open(os.path.join(os.path.dirname(self.video), file_name+os.path.extsep+Meta.meta_postfix), 'r') as rfh:
            line = rfh.readline()
            while line:
                line = line.strip()
                (name, value) = line.split(':')
                print("{},{}".format(name,value))
                self.__dict__[name] = Meta.data_type[name](value)
                line = rfh.readline()


    
