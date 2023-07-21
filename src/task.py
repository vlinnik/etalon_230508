# This is project entry point.
import sys,gc,time

ts = time.time_ns()
enter_ts = ts
def progress(msg):
    global ts
    print(msg,(time.time_ns() - ts)/1000000 )
    ts = time.time_ns( )

try:
    for x in sys.modules:
        # if x.startswith('pyplc') or x.startswith('kx') or x.startswith('misc') or x.startswith('concrete'):
        if x.startswith('concrete'):
            sys.modules.pop(x)
except Exception as e:
    print(e)
    pass
gc.collect()
progress('cleanup/reload complete')

from kx.config import *
progress('KX config loaded')
from concrete import Dosator, Container, Weight, MSGate, ElevatorGeneric as Elevator, Motor, Mixer, Transport, Factory, Readiness, Loaded, Lock, Accelerator, Manager
from concrete.vibrator import Vibrator,UnloadHelper
from heartbeat import HeartBeat
from concrete.imitation import *
from pyplc.utils.trig import TRANS
progress('CONCRETE loaded')

print('Starting up PYPLC-230713 project!')
plc, hw = kx_init()
progress('CONF loaded')

from pyplc.sfc import *

factory_1 = Factory(id='factory_1')
heartbeat_1 = HeartBeat(id='heartbeat_1')

# дозатор цемента с 1 шнеком
cement_m_1 = Weight(mmax=1500, raw=plc.CEMENT_M_1, id='cement_m_1')
silage_1 = Container(m=lambda: cement_m_1.m, out=plc.AUGER_ON_1, closed=~
                     plc.AUGER_ON_1, lock=Lock(key=~plc.DCEMENT_CLOSED_1), max_sp = 500, id='silage_1')
dcement_1 = Dosator(m=lambda: cement_m_1.m, closed=plc.DCEMENT_CLOSED_1, out=plc.DCEMENT_OPEN_1,
                    containers=[silage_1], fast=cement_m_1.mode, lock=Lock(key=lambda: hw.AUGER_ON_1 or not hw.MIXER_ISON_1), unloadT=3, id='cement_1')

# дозатор воды
water_m_1 = Weight(mmax=500, raw=plc.WATER_M_1, id='water_m_1')
wpump_1 = Transport( power = plc.WPUMP_ON_1, ison = plc.WPUMP_ISON_1,out = plc.WATER_OPEN_1 )
water_1 = Container(m=lambda: water_m_1.m, out=wpump_1.set_auto, max_sp = 500, closed=~
                    plc.WATER_OPEN_1, lock=Lock(key=~plc.DWATER_CLOSED_1), id='water_1')
dwater_1 = Dosator(m=lambda: water_m_1.m, closed=plc.DWATER_CLOSED_1, out=plc.DWATER_OPEN_1,
                   containers=[water_1], lock=Lock(key=plc.WATER_OPEN_1), unloadT=3, fast=water_m_1.mode, id='dwater_1')

# дозатор хд
additions_m_1 = Weight(mmax=50, raw=plc.ADDITIONS_M_1, id='additions_m_1')
addition_1 = Container(m=lambda: additions_m_1.m, out=plc.APUMP_ON_1, max_sp = 15, closed=~
                       plc.APUMP_ON_1, lock=~plc.DADDITIONS_CLOSED_1,  id='addition_1')
addition_2 = Container(m=lambda: additions_m_1.m, out=plc.APUMP_ON_2, max_sp = 15, closed=~
                       plc.APUMP_ON_2, lock=~plc.DADDITIONS_CLOSED_1,  id='addition_2')
addition_3 = Container(m=lambda: additions_m_1.m, out=plc.APUMP_ON_3, max_sp = 15, closed=~
                       plc.APUMP_ON_3, lock=~plc.DADDITIONS_CLOSED_1,  id='addition_3')
dadditions_1 = Dosator(m=lambda: additions_m_1.m, closed=plc.DADDITIONS_CLOSED_1, out=plc.DADDITIONS_OPEN_1,
                       containers=[addition_1,addition_2,addition_3], unloadT=0, fast=additions_m_1.mode, lock=Lock(key=lambda: hw.APUMP_ON_1 or hw.APUMP_ON_2 or hw.APUMP_ON_3), id='daddition_1')

# инертные
fillers_m_1 = Weight(mmax=8000, raw=plc.FILLERS_M_1, id='fillers_m_1')

accel_1 = Accelerator(outs=[plc.FILLER_OPEN_1, plc.FILLER_OPEN_2], sts=[
                      plc.FILLER_CLOSED_1, plc.FILLER_CLOSED_2])
accel_2 = Accelerator(outs=[plc.FILLER_OPEN_3, plc.FILLER_OPEN_4], sts=[
                      plc.FILLER_CLOSED_3, plc.FILLER_CLOSED_4])
filler_1 = Container(m=lambda: fillers_m_1.m, lock=Lock(key=lambda: hw.CONVEYOR_ISON_1 or not accel_2.closed),
                     closed=lambda: accel_1.closed, max_sp = 1000, id='filler_1')
accel_1.link(filler_1)

filler_2 = Container(m=lambda: fillers_m_1.m, lock=Lock(key=lambda: hw.CONVEYOR_ISON_1 or not accel_1.closed),
                     closed=lambda: accel_2.closed, max_sp = 1000, id='filler_2')
accel_2.link(filler_2)

transport_1 = Transport(power = plc.FLOW_DIR, ison = plc.FLOW_DIR_IN, out = plc.CONVEYOR_ON_1 )

fillers_1 = Dosator(m=lambda: fillers_m_1.m, containers=[filler_1, filler_2], lock=Lock(key=lambda: not (hw.FILLER_CLOSED_1 and hw.FILLER_CLOSED_2 and hw.FILLER_CLOSED_3 and hw.FILLER_CLOSED_4) or not hw.ELEVATOR_BELOW_1),
                    out=transport_1.set_auto, closed=~plc.CONVEYOR_ISON_1, fast=fillers_m_1.mode, id='fillers_1')


elevator_1 = Elevator( above = plc.ELEVATOR_ABOVE_1, below = plc.ELEVATOR_BELOW_1, up = plc.ELEVATOR_UP_1, down = plc.ELEVATOR_DOWN_1, 
                      containers = [filler_1,filler_2], loaded = lambda: fillers_1.unloaded , lock = Lock(key=~plc.FLOW_DIR_OUT ), id='elevator_1')

vibrator_1 = Vibrator(q=plc.VIBRATOR_ON_1, containers=[ filler_1], weight=fillers_m_1, id='vibrator_1')
vibrator_2 = Vibrator(q=plc.VIBRATOR_ON_2, containers=[ filler_2], weight=fillers_m_1, id='vibrator_2')
df_vibrator_1 = UnloadHelper(q = plc.DF_VIBRATOR_ON_1,dosator = fillers_1, weight = fillers_m_1,id = 'df_vibrator_1' )

# смеситель с 1 затвором
gate_1 = MSGate(closed=plc.MIXER_CLOSED_1, open=plc.MIXER_OPEN_1,
                opened=plc.MIXER_OPENED_1, id='gate_1')
motor_1 = Motor(powered=plc.MIXER_ON_1,
                ison=plc.MIXER_ISON_1, id='motor_1')
mixer_1 = Mixer(motor=motor_1, gate=gate_1,  flows=[s.q for s in [
    silage_1, water_1, addition_1] + elevator_1.flows +  [addition_2,addition_3]], id='mixer_1')

elevator_1.join('count',lambda: mixer_1.count)
elevator_1.join('go',lambda:mixer_1.go)
fillers_1.join('unload',lambda:elevator_1.load)

ready_1 = Readiness([mixer_1, dcement_1, dwater_1, dadditions_1,elevator_1])
loaded_1 = Loaded([dcement_1, dwater_1, dadditions_1, elevator_1])
manager_1 = Manager(collected=ready_1, loaded=loaded_1, mixer=mixer_1, dosators=[
                    dcement_1, dwater_1, dadditions_1, fillers_1],addons=[elevator_1],id='manager_1')

factory_1.on_mode = [x.switch_mode for x in [silage_1, dcement_1,
                                             water_1, addition_1, addition_2,addition_3, filler_1, filler_2, dwater_1, dadditions_1,fillers_1]]
factory_1.on_emergency = [x.emergency for x in [manager_1,silage_1, dcement_1, water_1,
                                                dwater_1, addition_1,addition_2,addition_3,dadditions_1, filler_1, filler_2, fillers_1, mixer_1, gate_1,elevator_1]]

instances = [heartbeat_1, factory_1, gate_1, motor_1, mixer_1, silage_1, dcement_1, water_1, dwater_1, addition_1,addition_2,addition_3,dadditions_1, filler_1, accel_1, filler_2, accel_2,
             fillers_1, vibrator_1, vibrator_2, elevator_1, cement_m_1, water_m_1, additions_m_1, fillers_m_1, manager_1,ready_1,loaded_1,df_vibrator_1,transport_1,wpump_1]  # here should be listed user defined programs
# instances = [heartbeat_1, factory_1, gate_1, motor_1, mixer_1, silage_1, dcement_1, water_1, dwater_1, addition_1,dadditions_1, filler_1, accel_1, filler_2, accel_2,
#              fillers_1, vibrator_1, vibrator_2, cement_m_1, water_m_1, additions_m_1, fillers_m_1]  # here should be listed user defined programs

# igate_1 = iGATE(open=plc.MIXER_OPEN_1, close=~plc.MIXER_OPEN_1,
#                 opened=plc.MIXER_OPENED_1.force, closed=plc.MIXER_CLOSED_1.force)
# iwater_1 = iVALVE(open=plc.WATER_OPEN_1, closed=plc.WATER_CLOSED_1.force)
# idcement_1 = iVALVE(open=plc.DCEMENT_OPEN_1, closed=plc.DCEMENT_CLOSED_1.force)
# idwater_1 = iVALVE(open=plc.DWATER_OPEN_1, closed=plc.DWATER_CLOSED_1.force)
# idadditions_1 = iVALVE(open=plc.DADDITIONS_OPEN_1,
#                        closed=plc.DADDITIONS_CLOSED_1.force)
# ifiller_1 = iVALVE(open=plc.FILLER_OPEN_1, closed=plc.FILLER_CLOSED_1.force)
# ifiller_2 = iVALVE(open=plc.FILLER_OPEN_2, closed=plc.FILLER_CLOSED_2.force)
# ifiller_3 = iVALVE(open=plc.FILLER_OPEN_3, closed=plc.FILLER_CLOSED_3.force)
# ifiller_4 = iVALVE(open=plc.FILLER_OPEN_4, closed=plc.FILLER_CLOSED_4.force)

# icement_m_1 = iWEIGHT(loading=plc.AUGER_ON_1,
#                       unloading=plc.DCEMENT_OPEN_1, q=plc.CEMENT_M_1.force, speed=100)
# iwater_m_1 = iWEIGHT(loading=plc.WATER_OPEN_1,
#                      unloading=plc.DWATER_OPEN_1, q=plc.WATER_M_1.force, speed=150)
# iadditions_m_1 = iWEIGHT(loading=lambda: hw.APUMP_ON_1 or hw.APUMP_ON_2 or hw.APUMP_ON_3,
#                          unloading=plc.DADDITIONS_OPEN_1, q=plc.ADDITIONS_M_1.force, speed=50)
# ifillers_m_1 = iWEIGHT(loading=lambda: hw.FILLER_OPEN_1 or hw.FILLER_OPEN_2 or hw.FILLER_OPEN_3 or hw.FILLER_OPEN_4,
#                        unloading=plc.CONVEYOR_ON_1, q=plc.FILLERS_M_1.force, speed=200)

# itransport_1 = iGATE(open = plc.FLOW_DIR,close = ~plc.FLOW_DIR,closed = plc.FLOW_DIR_OUT.force,opened = plc.FLOW_DIR_IN.force )
# ielevator_1 = iELEVATOR(up = plc.ELEVATOR_UP_1, down=plc.ELEVATOR_DOWN_1, below = plc.ELEVATOR_BELOW_1.force, above = plc.ELEVATOR_ABOVE_1.force )

# imotor_1 = iMOTOR(simple=True, on=plc.MIXER_ON_1, ison=plc.MIXER_ISON_1.force)
# iconveyor_1 = iMOTOR(simple=True, on=plc.CONVEYOR_ON_1,
#                      ison=plc.CONVEYOR_ISON_1.force)
# iauger_1 = iMOTOR(simple=True, on=plc.AUGER_ON_1, ison=plc.AUGER_ISON_1.force)
# iapump_1 = iMOTOR(simple=True, on=plc.APUMP_ON_1, ison=plc.APUMP_ISON_1.force)
# iapump_2 = iMOTOR(simple=True, on=plc.APUMP_ON_2, ison=plc.APUMP_ISON_2.force)
# iapump_3 = iMOTOR(simple=True, on=plc.APUMP_ON_3, ison=plc.APUMP_ISON_3.force)

# imitations = [igate_1, iwater_1, idcement_1, idwater_1, idadditions_1, ifiller_1, iauger_1, iapump_1, iapump_2, iapump_3,
#               ifiller_2, ifiller_3, ifiller_4, icement_m_1, iwater_m_1, iadditions_m_1, ifillers_m_1, imotor_1, iconveyor_1,ielevator_1,itransport_1]

plc.config(ctx=globals(),persist=board.eeprom)

print('Startup time is',(time.time_ns() - enter_ts)/1000000)

try:
    while True:
        board.run = not board.run
        with plc:
            for i in instances:
                i()
except KeyboardInterrupt:
    print('keyboard interrupt')
except Exception as e:
    print(f'terminating program because of {e}')
    sys.print_exception(e)

kx_term( )