from machine import Pin
from kx.config import kx_init,kx_term
import webrepl 

usr = Pin(36,Pin.IN)
run = Pin(39,Pin.IN)

if run.value()==0:
    print('KRAX.MAIN: RUN switch is ON. Loading TASK module...')
    try:
        import task
    except Exception as e:
        print('KRAX.MAIN: Exception in TASK. SafeMode!',e)
        kx_term( )
        plc,hw = kx_init(passive)
else:
    if usr.value()==0:
        print('KRAX.MAIN: USR is ON. Passive mode')
        import passive
    else:
        print('KRAX.MAIN: RUN switch is OFF. Welcome to REPL console!')
        plc,hw = kx_init( passive = True )

webrepl.stop()
webrepl.start()