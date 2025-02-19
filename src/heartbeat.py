from pyplc.sfc import *
from pyplc.config import board
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
            board.run = not board.run
            yield True
            