#Code By Ben H
#region Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()
brain_inertial = Inertial(Ports.PORT1)


# Robot connections
controller_1 = Controller(PRIMARY)
motor_1_motor_a = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)
motor_1_motor_b = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
motor_drivetrain_left = MotorGroup(motor_1_motor_a, motor_1_motor_b)
motor_2_motor_a = Motor(Ports.PORT19, GearSetting.RATIO_18_1, True)
motor_2_motor_b = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
motor_drivetrain_right = MotorGroup(motor_2_motor_a, motor_2_motor_b)

motor_puncher = Motor(Ports.PORT15,GearSetting.RATIO_18_1)

brain_inertial.calibrate()

# wait for rotation sensor to fully initialize
wait(30, MSEC)


#endregion Robot Configuration
autopilot = False
class DataPoint:
    """DataPoint for Logger
    """
    def __init__(self,f,*a) -> None:
        self.f = f
        self.a = a
    def __call__(self):
        return self.f(*self.a)  

class Logger:
    def __init__(self,items,keys) -> None:
        """_summary_

        Args:
            items (dict[str,DataPoint]): headders and DataPoints for logs
            keys (list[str]): organised keys of items
        """
        self.items = items
        self.keys = keys
        self.id = 0
        self.reset()
    def reset(self):
        """resets logs
        """        
        self.lastPoi = -1
        self.data = "time,"
        self.line(self.keys)
        
    def line(self,items,time=0):
        """logs a line

        Args:
            items (list[DataPoint]): list of data points
            time (int, optional): timestamp. Defaults to 0.
        """
        line = ''
        for i in items:
            line += str(i) + ","
        self.data += line[0:-1] + "\n"
        if len(self.data) > 5000:
            self.save()

    def __call__(self):
        timestamp = brain.timer.value()
        if self.lastPoi+0.05 <= timestamp:
            self.lastPoi=timestamp
            data = [timestamp]
            for k in self.keys:
                v = self.items[k]
                data.append(v())
            self.line(data,timestamp)
    def save(self):
        """saves logs then resets
        """
        if brain.sdcard.savefile("matchData%s.csv" % (self.id),bytearray(self.data,'utf-8')) == 0:
            brain.screen.print('Save Faled')
        else:
            brain.screen.print('Saved')
        self.reset()
        self.id +=1

log = Logger({
    "X":DataPoint(brain_inertial.acceleration,XAXIS),
    "Y":DataPoint(brain_inertial.acceleration,YAXIS),
    "Z":DataPoint(brain_inertial.acceleration,ZAXIS),

    "DFL Temp": DataPoint(motor_1_motor_a.temperature),
    "DFL Current": DataPoint(motor_1_motor_a.current),
    "DFL Torque": DataPoint(motor_1_motor_a.torque),
    "DFL Velocity": DataPoint(motor_1_motor_a.velocity),

    "DAL Temp": DataPoint(motor_1_motor_b.temperature),
    "DAL Current": DataPoint(motor_1_motor_b.current),
    "DAL Torque": DataPoint(motor_1_motor_b.torque),
    "DAL Velocity": DataPoint(motor_1_motor_b.velocity),

    "DFR Temp": DataPoint(motor_2_motor_a.temperature),
    "DFR Current": DataPoint(motor_2_motor_a.current),
    "DFR Torque": DataPoint(motor_2_motor_a.torque),
    "DFR Velocity": DataPoint(motor_2_motor_a.velocity),

    "DAR Temp": DataPoint(motor_2_motor_b.temperature),
    "DAR Current": DataPoint(motor_2_motor_b.current),
    "DAR Torque": DataPoint(motor_2_motor_b.torque),
    "DAR Velocity": DataPoint(motor_2_motor_b.velocity),
    
    "Pchr Temp": DataPoint(motor_puncher.temperature),
    "Pchr Velocity": DataPoint(motor_puncher.velocity)

},[
    "X",
    "Y",
    "Z",

    "DFL Temp",
    "DFL Current",
    "DFL Torque",
    "DFL Velocity",

    "DAL Temp",
    "DAL Current",
    "DAL Torque",
    "DAL Velocity",

    "DFR Temp",
    "DFR Current",
    "DFR Torque",
    "DFR Velocity",

    "DAR Temp",
    "DAR Current",
    "DAR Torque",
    "DAR Velocity",

    "Pchr Temp",
    "Pchr Velocity",
])

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
        'M':4,
        'S':5
    }
    statz = ["R","T","G",'r','M',"S"]
    def __init__(self) -> None:
        self.stat = [False for i in self.statz]
        for i in self.statz:
            self.draw(i)
    def draw(self,c):
        """draws char to screen

        Args:
            c (str): the charicter, must be registered to status and statz
        """
        controller_1.screen.set_cursor(1,self.status[c]+1)
        if self.stat[self.status[c]]:
            controller_1.screen.print(c)
        else:
            controller_1.screen.print("-")
    def tgl(self,c):
        """toggles char on screen

        Args:
            c (str): the charicter, must be registered to status and statz
        """
        self.stat[self.status[c]] = not self.stat[self.status[c]]
        self.draw(c)
    def disable(self,c):
        """disables char on screen

        Args:
            c (str): the charicter, must be registered to status and statz
        """
        self.stat[self.status[c]] = False
        self.draw(c)
    def warn(self,c):
        """toggles char on screen and indicates a warn

        Args:
            c (str): the charicter, must be registered to status and statz
        """
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

    def temps(self,val):
        """triggers a motor temp warning if val > 40

        Args:
            val (int): max motor temp
        """
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

    def driverNeeded(self,func):
        def wrapper(*args, **kwargs):
            if self.mode != modes.stop and self.mode != modes.ap:
                func(*args, **kwargs)
        return wrapper

    def autopilotOnly(self,func):
        def wrapper(*args, **kwargs):
            if self.mode == modes.ap:
                func(*args, **kwargs)
        return wrapper

#max speeds

steer_speed_mult = 1 #0.5
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

    #region Arcade Controls
    def calcSpeed(self,inv):
        if inv:
            spdDiff = -self.diff
        else:
            spdDiff = self.diff
        return clamp(self.speed - spdDiff,-self.max_speed,self.max_speed)*self.speed_mult

    def calcMotors(self):
        motor_drivetrain_left.set_velocity(self.calcSpeed(False), PERCENT)
        motor_drivetrain_right.set_velocity(self.calcSpeed(True), PERCENT)
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
    #endregion Arcade Controls
    
    @state.driverNeeded
    def drive(self):
        """robot drive controls
        """
        log()
        pos = controller_1.axis2.position()
        L = clamp(pos,-self.max_speed,self.max_speed)*self.speed_mult
        pos = controller_1.axis3.position()
        R = clamp(pos,-self.max_speed,self.max_speed)*self.speed_mult
        motor_drivetrain_left.set_velocity(L, PERCENT)
        motor_drivetrain_right.set_velocity(R, PERCENT)
        status.temps(max(motor_1_motor_a.temperature(),motor_1_motor_b.temperature(),motor_2_motor_a.temperature(),motor_2_motor_b.temperature()))
    
    @state.autopilotOnly
    def driveSequence(self):
        """Autopilot driveSequence
        """
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

#region buttons
    
modeSwitch = ButtonBinding("down",modes.mode1)

@modeSwitch.Press
def press():
    state.mode = modes.mode2
    controller_1.rumble('.')
    anunciator.tgl('M')

modeSwitch2 = ButtonBinding("down",modes.mode2)

@modeSwitch2.Press
def press():
    state.mode = modes.mode1
    controller_1.rumble('.')
    anunciator.tgl('M')

puncher = ButtonBinding('R2',modes.mode1)

@puncher.Press
def press():
    motor_puncher.set_velocity(200,RPM)

@puncher.Release
def release():
    motor_puncher.set_velocity(0,RPM)

save = ButtonBinding('b',modes.mode1)
@save.Press
def press():
    log.save()

#endregion

INITD = False

def init():
    global INITD
    log()
    if not INITD and competition.is_enabled():
        INITD = True
        anunciator.tgl('R')

        motor_puncher.set_velocity(0,RPM)

        anunciator.warn('R')
        if brain.sdcard.is_inserted():
            pass
        else:
            anunciator.tgl("S")    

competition=Competition(driver,autonomous_start)
init()
#brain_inertial.collision()

#region Arcade
#controller_1.axis3.changed(speed.mspeed)
#controller_1.axis4.changed(speed.dspeed)
#speed.calcMotors()
#endregion

controller_1.axis3.changed(speed.drive)
controller_1.axis2.changed(speed.drive)

motor_drivetrain_left.spin(FORWARD)
motor_drivetrain_right.spin(FORWARD)
motor_puncher.spin(FORWARD)
speed.drive()