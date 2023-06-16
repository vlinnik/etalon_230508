from machine import Pin
import webrepl 

usr = Pin(36,Pin.IN)
run = Pin(39,Pin.IN)

if run.value()==0:
    print('KRAX.MAIN: RUN switch is ON. Loading TASK module...')
    try:
        import task
    except Exception as e:
        from kx.config import kx_init,kx_term
        print('KRAX.MAIN: Exception in TASK. SafeMode!',e)
        kx_term( )
        plc,hw = kx_init(passive)
else:
    if usr.value()==0:
        print('KRAX.MAIN: USR is ON. Passive mode')
        import passive
    else:
        from kx.config import kx_init
        print('KRAX.MAIN: RUN switch is OFF. Welcome to REPL console!')
        plc,hw = kx_init( passive = True )

webrepl.stop()
webrepl.start()