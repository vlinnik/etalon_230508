from kx.config import *

def main():
    plc,hw = kx_init( passive=True)

    try:
        while True:
            board.run = not board.run
            with plc:
                pass
    except KeyboardInterrupt:
        pass
    kx_term( )
    
main( )