from pyplc.sfc import *
@sfc(outputs=['q'])
class HeartBeat(SFC):
    def __init__(self):
        self.q = False

    @sfcaction
    def main(self):
        while True:
            self.q = False
            yield True
            for i in self.pause(2000):
                yield i
            self.q = True
            yield True
            