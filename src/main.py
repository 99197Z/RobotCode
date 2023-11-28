#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()
#competition=Competition(None,None)

# Robot configuration code
controller_1 = Controller(PRIMARY)
motor_1_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
motor_1_motor_b = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
motor_1 = MotorGroup(motor_1_motor_a, motor_1_motor_b)
motor_2_motor_a = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)
motor_2_motor_b = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
motor_2 = MotorGroup(motor_2_motor_a, motor_2_motor_b)


# wait for rotation sensor to fully initialize
wait(30, MSEC)


#endregion VEXcode Generated Robot Configuration
autopilot = False



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
        "r":3
    }
    statz = ["R","T","G",'r']
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
        if val > 50:
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

steer_speed_mult = 0.5
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
        def wrapper(*arg,**kwargs):
            raise ButtonDirectCall(func,self)
        return wrapper
    def Release(self,func):
        btnz[self.btn].released(self.release(func))
        def wrapper(*arg,**kwargs):
            raise ButtonDirectCall(func,self)
        return wrapper
    
class speedControlls:
    def __init__(self,mx):
        self.diff = 0
        self.speed = 0
        self.speed_mult = 0
        self.max_speed = mx
    
    def drive(self,speed,diff):
        self.speed = speed
        self.diff = diff
        self.calcMotors()
    
    def stop(self):
        self.drive(0,0)

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
    
    @state.autopilotOnly
    def driveSequence(self):
        self.drive(25,0)
        wait(1500)
        self.drive(50,-1)
        wait(500)
        self.drive(10,0)
        wait(100)
        self.stop()

        

speed = speedControlls(driver_pilot_max_speed)

def autonomous_start():
    state.mode = modes.ap
    speed.driveSequence()
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

reverseMode = ButtonBinding('L1',modes.mode1)
@status.restrict_all
@reverseMode.Press
def press():
    speed.speed_mult = -steer_speed_mult
    anunciator.tgl('r')

@reverseMode.Release
def release():
    speed.speed_mult = steer_speed_mult
    anunciator.tgl('r')

test = ButtonBinding('R1',modes.mode1)
@status.restrict_all
@test.Press
def press():
    autonomous_start()
    anunciator.warn('T')

@test.Release
def release():
    anunciator.warn('T')

# Register event with a callback function.
controller_1.axis3.changed(speed.mspeed)
controller_1.axis4.changed(speed.dspeed)
motor_1.spin(FORWARD)
motor_2.spin(FORWARD)
speed.calcMotors()
