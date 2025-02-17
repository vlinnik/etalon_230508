from pyplc.sfc import *
class HeartBeat(SFC):
    q = POU.output(False)
    def __init__(self,q:bool=False,id:str = None,parent:POU = None):
        super().__init__(id=id,parent=parent)
        self.q = q

    def main(self):
        while True:
            self.q = False
            yield True
            yield from self.pause(2000)
            self.q = True
            yield True
            