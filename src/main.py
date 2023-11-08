#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()
competition=Competition()

# Robot configuration code
controller_1 = Controller(PRIMARY)
motor_1_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
motor_1_motor_b = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
motor_1 = MotorGroup(motor_1_motor_a, motor_1_motor_b)
motor_2_motor_a = Motor(Ports.PORT7, GearSetting.RATIO_18_1, True)
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


class ButtonDirectCall(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.add_note('button press func called Without A/P')
class State:
    def __init__(self) -> None:
        self.mode = modes.mode1
        self.errors = 0
        self.buttons = {
            "a": False,
            "b": False,
            "x": False,
            "y": False,
            "u": False,
            "d": False,
            "l": False,
            "r": False,
            "L1": False,
            "L2": False,
            "R1": False,
            "R2": False
        }
        
        controller_1.buttonA.pressed(self.call_btn_rel('a'))
        controller_1.buttonB.pressed(self.call_btn_rel('b'))
        controller_1.buttonX.pressed(self.call_btn_rel('x'))
        controller_1.buttonY.pressed(self.call_btn_rel('y'))
        controller_1.buttonUp.pressed(self.call_btn_rel('u'))
        controller_1.buttonDown.pressed(self.call_btn_rel('d'))
        controller_1.buttonLeft.pressed(self.call_btn_rel('l'))
        controller_1.buttonRight.pressed(self.call_btn_rel('r'))
        controller_1.buttonL1.pressed(self.call_btn_rel('L1'))
        controller_1.buttonL2.pressed(self.call_btn_rel('L2'))
        controller_1.buttonR1.pressed(self.call_btn_rel('R1'))
        controller_1.buttonR2.pressed(self.call_btn_rel('R2'))

        controller_1.buttonA.pressed(self.call_btn_press('a'))
        controller_1.buttonB.pressed(self.call_btn_press('b'))
        controller_1.buttonX.pressed(self.call_btn_press('x'))
        controller_1.buttonY.pressed(self.call_btn_press('y'))
        controller_1.buttonUp.pressed(self.call_btn_press('u'))
        controller_1.buttonDown.pressed(self.call_btn_press('d'))
        controller_1.buttonLeft.pressed(self.call_btn_press('l'))
        controller_1.buttonRight.pressed(self.call_btn_press('r'))
        controller_1.buttonL1.pressed(self.call_btn_press('L1'))
        controller_1.buttonL2.pressed(self.call_btn_press('L2'))
        controller_1.buttonR1.pressed(self.call_btn_press('R1'))
        controller_1.buttonR2.pressed(self.call_btn_press('R2'))

        self.M1 = {}
        self.M2 = {}

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
    def press(self):
        pass
    def release(self):
        pass
    def PressRebind(self,func):
        self.press = func
        def wrapper(*arg,**kwargs):
            raise ButtonDirectCall(func,self)
        return wrapper
    def ReleaseRebind(self,func):
        self.release = func
        def wrapper(*arg,**kwargs):
            raise ButtonDirectCall(func,self)
        return wrapper
class speedControlls:
    def __init__(self,mx):
        self.diff = 0
        self.speed = 0
        self.speed_mult = 0.5
        self.max_speed = mx
        
    def calcSpeed(self,inv):
        if inv:
            spdDiff = -self.diff
        else:
            spdDiff = self.diff
        return clamp(self.speed - spdDiff,-self.max_speed,self.max_speed)*self.speed_mult

    def calcMotors(self):
        motor_1.set_velocity(self.calcSpeed(False), PERCENT)
        motor_2.set_velocity(self.calcSpeed(True), PERCENT)

    @state.driverNeeded
    def mspeed(self):
        pos = controller_1.axis3.position()
        brain.screen.set_cursor(1,1)
        brain.screen.clear_screen()
        brain.screen.print(str(pos))
        self.speed = pos
        self.calcMotors()

    @state.driverNeeded
    def dspeed(self):
        pos = controller_1.axis4.position()
        self.diff = pos
        self.calcMotors()
    
    @state.autopilotOnly
    def driveSequence(self):
        pass
        

speed = speedControlls(driver_pilot_max_speed)

def autonomous_start():
    state.mode = modes.ap
    speed.driveSequence()

competition.autonomous = autonomous_start


speedMode = ButtonBinding('L2',modes.mode1)
@speedMode.PressRebind
def press():
    speed.speed_mult = gas_speed_mult
    
@speedMode.ReleaseRebind
def release():
    speed.speed_mult = steer_speed_mult

# Register event with a callback function.
controller_1.axis3.changed(speed.mspeed)
controller_1.axis4.changed(speed.dspeed)
motor_1.spin(FORWARD)
motor_2.spin(FORWARD)
speed.calcMotors()
