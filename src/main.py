#Code By Ben H
#region VEXcode Generated Robot Configuration
from typing import Any
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()
brain_inertial = Inertial(Ports.PORT1)


# Robot configuration code
controller_1 = Controller(PRIMARY)
motor_1_motor_a = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)
motor_1_motor_b = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
motor_1 = MotorGroup(motor_1_motor_a, motor_1_motor_b)
motor_2_motor_a = Motor(Ports.PORT19, GearSetting.RATIO_18_1, True)
motor_2_motor_b = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
motor_2 = MotorGroup(motor_2_motor_a, motor_2_motor_b)


motor_traparm = Motor(Ports.PORT6, GearSetting.RATIO_36_1, False)

motor_traparm.reset_position()

limit_traparm = Limit(brain.three_wire_port.h)
brain_inertial.calibrate()

# wait for rotation sensor to fully initialize
wait(30, MSEC)


#endregion VEXcode Generated Robot Configuration
autopilot = False
data = "time,X,Y,Z,Forward Left Drive,Forward Right Drive,Aft Left Drive,Aft Right Drive,ArmTemp,arm\n"
class DataPoint:
    def __init__(self,f,*a) -> None:
        self.f = f
        self.a = a
    def __call__(self) -> Any:
        return self.f(*self.a)
class Logger:
    def __init__(self,items) -> None:
        self.items = items
        self.data = ""
        self.line(items.keys())
        
    def line(self,items):
        line = ''
        for i in items:
            line += str(i) + ","
        self.data += line.removesuffix(',') + "\n"
    def __call__(self):
        data = []
        for k,v in self.items.items():
            data.append(v())
        self.line(data)
    def save(self):
        if brain.sdcard.savefile("matchData.csv",bytearray(self.data,'utf-8')) == 0:
            brain.screen.print('Save Faled')
        else:
            brain.screen.print('Saved')
        print(self.data)

log = Logger({
    "time":DataPoint(brain.timer.value),
    "X":DataPoint(brain_inertial.acceleration,XAXIS),
    "Y":DataPoint(brain_inertial.acceleration,YAXIS),
    "Z":DataPoint(brain_inertial.acceleration,ZAXIS),

    "Drive Forward Left Temp": DataPoint(motor_1_motor_a.temperature),
    "Drive Forward Left Current": DataPoint(motor_1_motor_a.current),
    "Drive Forward Left Torque": DataPoint(motor_1_motor_a.torque),
    "Drive Forward Left Velocity": DataPoint(motor_1_motor_a.velocity),

    "Drive Aft Left Temp": DataPoint(motor_1_motor_b.temperature),
    "Drive Aft Left Current": DataPoint(motor_1_motor_b.current),
    "Drive Aft Left Torque": DataPoint(motor_1_motor_b.torque),
    "Drive Aft Left Velocity": DataPoint(motor_1_motor_b.velocity),

    "Drive Forward Right Temp": DataPoint(motor_2_motor_a.temperature),
    "Drive Forward Right Current": DataPoint(motor_2_motor_a.current),
    "Drive Forward Right Torque": DataPoint(motor_2_motor_a.torque),
    "Drive Forward Right Velocity": DataPoint(motor_2_motor_a.velocity),

    "Drive Aft Right Temp": DataPoint(motor_2_motor_b.temperature),
    "Drive Aft Right Current": DataPoint(motor_2_motor_b.current),
    "Drive Aft Right Torque": DataPoint(motor_2_motor_b.torque),
    "Drive Aft Right Velocity": DataPoint(motor_2_motor_b.velocity),

})

class modes:
    stop = 0
    ap = 1
    mode1 = 2
    mode2 = 3

class Anunciator:
    status = {
        "R":0,
        "T":1,
        "G":2,
        "r":3,
        'A':4,
        'S':5
    }
    statz = ["R","T","G",'r','A',"S"]
    def __init__(self) -> None:
        self.stat = [False for i in self.statz]
        for i in self.statz:
            self.draw(i)
    def draw(self,c):
        controller_1.screen.set_cursor(1,self.status[c]+1)
        if self.stat[self.status[c]]:
            controller_1.screen.print(c)
        else:
            controller_1.screen.print("-")
    def tgl(self,c):
        self.stat[self.status[c]] = not self.stat[self.status[c]]
        self.draw(c)
    def disable(self,c):
        self.stat[self.status[c]] = False
        self.draw(c)
    def warn(self,c):
        self.tgl(c)
        if self.stat[self.status[c]]:
            controller_1.rumble("...---...") # sos
        else:
            controller_1.rumble(".")
        
anunciator = Anunciator()

class Status_Warnings:
    def __init__(self) -> None:
        self.Temps = 0
        self.restrict = False
        self.states = {
            "T":False
        }
    def draw(self,text,bool):
        controller_1.screen.set_cursor(self.draw_pos[text],1)
        if bool:
            controller_1.screen.print(text)
        else:
            controller_1.screen.print("-")

    def temps(self,val):
        self.Temps = val
        if val > 40:
            self.states['T'] = True
            self.restrict = True
            anunciator.warn('T')
            controller_1.screen.set_cursor(2,1)
            controller_1.screen.print(val)

        elif self.states['T']:
            self.states['T'] = False
            anunciator.warn('T')

    def restrict_all(self,func):
        def wrapper(*args,**kwargs):
            if not self.restrict:
                return func(*args,**kwargs)
            else:
                return None
        return wrapper
status = Status_Warnings()


class ButtonDirectCall(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.add_note('button press func called Without A/P')
        

btnz = {
    "a":controller_1.buttonA,
    "b":controller_1.buttonB,
    "x":controller_1.buttonX,
    "y":controller_1.buttonY,
    "up":controller_1.buttonUp,
    "down":controller_1.buttonDown,
    "left":controller_1.buttonLeft,
    "right":controller_1.buttonRight,
    "L1":controller_1.buttonL1,
    "L2":controller_1.buttonL2,
    "R1":controller_1.buttonR1,
    "R2":controller_1.buttonR2
}
class State:
    def __init__(self) -> None:
        self.mode = modes.mode1
        self.errors = 0

    def call_btn_press(self,btn):
        def exec():
            if self.mode == modes.mode1:
                f = self.M1.get(btn)
                if f:
                    f.press()
            elif self.mode == modes.mode2:
                f = self.M2.get(btn)
                if f:
                    f.press()
        return exec
    
    def call_btn_rel(self,btn):
        def exec():
            if self.mode == modes.mode1:
                f = self.M1.get(btn)
                if f:
                    f.release()
            elif self.mode == modes.mode2:
                f = self.M2.get(btn)
                if f:
                    f.release()
        return exec
    

    def driverNeeded(self,func):
        def wrapper(*args, **kwargs):
            if self.mode != modes.stop and self.mode != modes.ap:
                func(*args, **kwargs)
            
            #func(*args, **kwargs)
        return wrapper
    

    def autopilotOnly(self,func):
        def wrapper(*args, **kwargs):
            if self.mode == modes.ap:
                func(*args, **kwargs)
            #func(*args, **kwargs)
        return wrapper

#max speeds

steer_speed_mult = 1 #0.5
gas_speed_mult = 1
autopilot_max_speed = 50 
driver_pilot_max_speed = 100 



def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 

state = State()

class ButtonBinding:
    def __init__(self,btn,mode) -> None:
        self.btn = btn
        self.mode = mode
    def press(self,f:function):
        def mode():
            if state.mode == self.mode:
                f()
        return mode
    def release(self,f):
        def mode():
            if state.mode == self.mode:
                f()
        return mode
    def Press(self,func):
        btnz[self.btn].pressed(self.press(func))
        #self.press = func
        def wrapper(*arg,**kwargs):
            raise ButtonDirectCall(func,self)
        return wrapper
    def Release(self,func):
        btnz[self.btn].released(self.release(func))
        #self.release = func
        def wrapper(*arg,**kwargs):
            raise ButtonDirectCall(func,self)
        return wrapper
    
class speedControlls:
    def __init__(self,mx):
        self.diff = 0
        self.speed = 0
        self.speed_mult = 1
        self.max_speed = mx
    @state.autopilotOnly
    def Adrive(self,speed,diff):
        self.speed = speed
        self.diff = diff
        self.calcMotors()
    
    def stop(self):
        self.Adrive(0,0)

    def calcSpeed(self,inv):
        if inv:
            spdDiff = -self.diff
        else:
            spdDiff = self.diff
        return clamp(self.speed - spdDiff,-self.max_speed,self.max_speed)*self.speed_mult

    def calcMotors(self):
        motor_1.set_velocity(self.calcSpeed(False), PERCENT)
        motor_2.set_velocity(self.calcSpeed(True), PERCENT)
        status.temps(max(motor_1_motor_a.temperature(),motor_1_motor_b.temperature(),motor_2_motor_a.temperature(),motor_2_motor_b.temperature()))

    @state.driverNeeded
    def mspeed(self):
        pos = controller_1.axis3.position()
        brain.screen.set_cursor(1,1)
        brain.screen.clear_screen()
        brain.screen.print(str(pos))
        brain.screen.set_cursor(2,2)
        brain.screen.print(str(self.speed_mult))
        self.speed = pos
        self.calcMotors()

    @state.driverNeeded
    def dspeed(self):
        pos = controller_1.axis4.position()
        self.diff = pos
        self.calcMotors()
    
    @state.driverNeeded
    def drive(self):
        log()
        pos = controller_1.axis3.position()
        R = clamp(pos,-self.max_speed,self.max_speed)*self.speed_mult
        pos = controller_1.axis2.position()
        L = clamp(pos,-self.max_speed,self.max_speed)*self.speed_mult
        motor_1.set_velocity(L, PERCENT)
        motor_2.set_velocity(R, PERCENT)
        status.temps(max(motor_1_motor_a.temperature(),motor_1_motor_b.temperature(),motor_2_motor_a.temperature(),motor_2_motor_b.temperature()))
    
    @state.autopilotOnly
    def driveSequence(self):
        self.Adrive(90,20)
        wait(1200)
        log()
        self.Adrive(15,-100)
        wait(100)
        log()
        self.Adrive(0,0)
        #Arm()
        #self.Adrive(10,0)
        #wait(100)
        #self.stop()
        pass
        

        

speed = speedControlls(driver_pilot_max_speed)

def autonomous_start():
    state.mode = modes.ap
    init()
    speed.driveSequence()
    state.mode = modes.mode1

def driver():
    init()
    state.mode = modes.mode1

#competition.autonomous = autonomous_start


speedMode = ButtonBinding('L2',modes.mode1)
@status.restrict_all
@speedMode.Press
def press():
    if speed.speed_mult>= 0:
        speed.speed_mult = gas_speed_mult
    else:
        speed.speed_mult = -gas_speed_mult
    anunciator.tgl('G')

@speedMode.Release
def release():
    if speed.speed_mult>= 0:
        speed.speed_mult = steer_speed_mult
    else:
        speed.speed_mult = -steer_speed_mult
    anunciator.tgl('G')


INITD = False
ARM = True


ArmBtn = ButtonBinding('R2',modes.mode1)

def Arm():
    global ARM
    if INITD:
        if ARM:
            motor_traparm.spin_to_position(0,DEGREES,25,RPM,True)
            #while not limit_pokearm.pressing():
            #    wait(100)
            motor_traparm.stop(COAST)
        else:
            motor_traparm.spin_to_position(-180,DEGREES,25,RPM,True)
            
            motor_traparm.stop(HOLD)
        ARM = not ARM
        anunciator.tgl('A')
        log()
@ArmBtn.Press
def press():
    Arm()

def init():
    global ARM, INITD
    log()
    if not INITD and competition.is_enabled():
        INITD = True
        anunciator.tgl('R')

        if not limit_traparm.pressing():
            anunciator.tgl('A')
            motor_traparm.spin_to_position(180,DEGREES,15,RPM,False)
            while not limit_traparm.pressing():
                wait(100)
                controller_1.rumble(".")
            motor_traparm.stop(COAST)
            
            anunciator.tgl('A')
        motor_traparm.reset_position()
        #lower arm
        motor_traparm.spin_to_position(-180,DEGREES,25,RPM)
        anunciator.tgl('A')

        controller_1.rumble(".")

        anunciator.warn('R')
        if brain.sdcard.is_inserted():
            pass
        else:
            anunciator.tgl("S")    


save = ButtonBinding('b',modes.mode1)
@save.Press
def press():
    log.save()

competition=Competition(driver,autonomous_start)
init()
#brain_inertial.collision()
# Register event with a callback function.
#controller_1.axis3.changed(speed.mspeed)
#controller_1.axis4.changed(speed.dspeed)
controller_1.axis3.changed(speed.drive)
controller_1.axis2.changed(speed.drive)
motor_1.spin(FORWARD)
motor_2.spin(FORWARD)
speed.calcMotors()
