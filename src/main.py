#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()

# Robot configuration code
controller_1 = Controller(PRIMARY)
motor_1_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
motor_1_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
motor_1 = MotorGroup(motor_1_motor_a, motor_1_motor_b)
motor_2_motor_a = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
motor_2_motor_b = Motor(Ports.PORT12, GearSetting.RATIO_18_1, True)
motor_2 = MotorGroup(motor_2_motor_a, motor_2_motor_b)


# wait for rotation sensor to fully initialize
wait(30, MSEC)






#endregion VEXcode Generated Robot Configuration
autopilot = False

def driverNeeded(func):
    def wrapper(*args, **kwargs):
        if not autopilot:
            func(*args, **kwargs)
        
        #func(*args, **kwargs)
    return wrapper

def autopilotOnly(func):
    def wrapper(*args, **kwargs):
        if autopilot:
            func(*args, **kwargs)
        #func(*args, **kwargs)
    return wrapper

#max speeds
speed_mult = 0.5
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

class speedControlls:
    def __init__(self,mx):
        self.diff = 0
        self.speed = 0
        self.max_speed = mx
    def calcSpeed(self,inv):
        if inv:
            spdDiff = -self.diff
        else:
            spdDiff = self.diff
        return clamp(self.speed - spdDiff,-self.max_speed,self.max_speed)*speed_mult

    def calcMotors(self):
        
        
        motor_1.set_velocity(self.calcSpeed(False), PERCENT)
        motor_2.set_velocity(self.calcSpeed(True), PERCENT)

    @driverNeeded
    def mspeed(self):
        pos = controller_1.axis3.position()
        brain.screen.set_cursor(1,1)
        brain.screen.clear_screen()
        brain.screen.print(str(pos))
        self.speed = pos
        self.calcMotors()

    @driverNeeded
    def dspeed(self):
        pos = controller_1.axis4.position()
        self.diff = pos
        self.calcMotors()
    
    @autopilotOnly
    def driveSequence(self):
        pass







speed = speedControlls(driver_pilot_max_speed)

class modes:
    stop = 0
    ap = 1
    mode1 = 2
    mode2 = 3

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


# Register event with a callback function.
controller_1.axis3.changed(speed.mspeed)
controller_1.axis4.changed(speed.dspeed)
motor_1.spin(FORWARD)
motor_2.spin(FORWARD)
speed.calcMotors()
