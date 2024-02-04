#Code By Ben H
#region Robot Configuration
from vex import *
import math
CODE_VER = "DEV"
MOTOR_OVERHEAT = 40

A_SIDE =1

# Brain should be defined by default
brain=Brain()
#m = brain.sdcard.load_to_string("mat.ch")
#if m:
#    mtch = int(m)+1
#    
#else:
#    mtch = 1
#brain.sdcard.savefile("mat.ch",str(mtch))
mtch = 1
inertial = Inertial(Ports.PORT1)


# Robot connections



DRIVE_GEAR_RATIO = 5/9
WHEEL_D = 0.104

controller_1 = Controller(PRIMARY)
motor_1_motor_a = Motor(Ports.PORT19, GearSetting.RATIO_18_1, True)
motor_1_motor_b = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
motor_drivetrain_left = MotorGroup(motor_1_motor_a, motor_1_motor_b)
motor_2_motor_a = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
motor_2_motor_b = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)
motor_drivetrain_right = MotorGroup(motor_2_motor_a, motor_2_motor_b)

DRVmotors = {
    0b10 :motor_1_motor_a,
    0b11 :motor_1_motor_b,
    0b00 :motor_2_motor_a,
    0b01 :motor_2_motor_b
}
DRVmotorsNAME = {
    0b10 :"motor_1_motor_a (left forward)",
    0b11 :"motor_1_motor_b (left rear)",
    0b00 :"motor_2_motor_a (right forward)",
    0b01 :"motor_2_motor_b (right rear)"
}

motor_puncher = Motor(Ports.PORT15,GearSetting.RATIO_18_1,True)

led_tlem_r_1 = Led(brain.three_wire_port.a)
led_tlem_r_2 = Led(brain.three_wire_port.b)

led_tlem_y_1 = Led(brain.three_wire_port.c)
led_tlem_y_2 = Led(brain.three_wire_port.d)

inertial.calibrate()

# wait for rotation sensor to fully initialize
wait(30, MSEC)


#endregion Robot Configuration
autopilot = False

def NoFunc(*args):
    pass

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
    def log(self,t,l):
        timestamp = str(brain.timer.value())
        T = ("{:<7} - [{:<7}] {}\n").format(
            l,
            str(timestamp),
            t)
        self.logData += T
        print(T,end="")
    def debug(self,t):
        self.log(t,"debug")
    def WARNING(self,t):
        self.log(t,"warn")
    def reset(self):
        """resets logs
        """        
        self.lastPoi = -1
        self.data = "time,"
        self.logData = ""
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
        if len(self.data) > 50000:
            print('saver')
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
        if brain.sdcard.savefile("matchData%s-%s.csv" % (mtch,self.id),bytearray(self.data,'utf-8')) == 0:
            brain.screen.print('Save Faled')
            self.WARNING("fs: save failed matchData")
        else:
            print('save')
        if brain.sdcard.savefile("log%s-%s.log" % (mtch,self.id),bytearray(self.logData,'utf-8')) == 0:
            brain.screen.print('Save Faled')
            self.WARNING("fs: save failed log")
        else:
            print('save')
        self.reset()
        self.id +=1

def drive_TO_ms(rpm):
    return ((rpm * (DRIVE_GEAR_RATIO))* math.pi * WHEEL_D)/60

def LDRPM():
    return drive_TO_ms(motor_drivetrain_left.velocity())

def RDRPM():
    return drive_TO_ms(motor_drivetrain_right.velocity())

log = Logger({
    "X":DataPoint(inertial.acceleration,XAXIS),
    "Y":DataPoint(inertial.acceleration,YAXIS),
    "Z":DataPoint(inertial.acceleration,ZAXIS),

    "L Drive M/S":DataPoint(LDRPM),
    "R Drive M/S":DataPoint(RDRPM),

    "DFL Temp": DataPoint(motor_1_motor_a.temperature),
    "DFL Torque": DataPoint(motor_1_motor_a.torque),
    "DFL Velocity": DataPoint(motor_1_motor_a.velocity),

    "DAL Temp": DataPoint(motor_1_motor_b.temperature),
    "DAL Torque": DataPoint(motor_1_motor_b.torque),
    "DAL Velocity": DataPoint(motor_1_motor_b.velocity),

    "DFR Temp": DataPoint(motor_2_motor_a.temperature),
    "DFR Torque": DataPoint(motor_2_motor_a.torque),
    "DFR Velocity": DataPoint(motor_2_motor_a.velocity),

    "DAR Temp": DataPoint(motor_2_motor_b.temperature),
    "DAR Torque": DataPoint(motor_2_motor_b.torque),
    "DAR Velocity": DataPoint(motor_2_motor_b.velocity),
    
    "PCHR Temp": DataPoint(motor_puncher.temperature),
    "PCHR Velocity": DataPoint(motor_puncher.velocity),

},[
    "X",
    "Y",
    "Z",

    "L Drive M/S",
    "R Drive M/S",

    "DFL Temp",
    "DFL Torque",
    "DFL Velocity",

    "DAL Temp",
    "DAL Torque",
    "DAL Velocity",

    "DFR Temp",
    "DFR Torque",
    "DFR Velocity",

    "DAR Temp",
    "DAR Torque",
    "DAR Velocity",

    "PCHR Temp",
    "PCHR Velocity",
])

class Elem:
    def __init__(self,x,y,t) -> None:
        self.x = x
        self.y = y
        self.t = t
    def draw(self):
        brain.screen.set_cursor(self.x,self.y)
        brain.screen.print(self.t)
    def click(self,x,y):
        pass

class Button(Elem):
    def __init__(self, x, y,w,h,c, t,cb) -> None:
        super().__init__(x, y, t)
        self.w = w
        self.h = h
        self.cb = cb
        self.c = c
    def draw(self):
        brain.screen.set_pen_color(Color.WHITE)
        brain.screen.draw_rectangle((self.x-1)*10,(self.y+1)*20,self.w*10,self.h*20,self.c)
        brain.screen.print_at(self.t,x=(self.x-1)*10,y=(self.y+1.75)*20,opaque=False)
    def click(self, x, y):
        if (x>= (self.x-1)*10 and y >= (self.y+1)*20):
            if (x<= (self.w+self.x)*10 and y <= (self.h+self.y)*20):
                self.cb()

class Rect(Elem):
    def __init__(self, x, y,w,h,c) -> None:
        super().__init__(x, y, "")
        self.w = w
        self.h = h
        self.c = c
    def draw(self):
        brain.screen.set_pen_color(self.c)
        brain.screen.draw_rectangle((self.x-1)*10,(self.y+1)*20,self.w*10,self.h*20,Color.TRANSPARENT)
    
class UI:
    def __init__(self) -> None:
        self.e = []
        self.EN = True
    def add(self,e):
        self.e.append(e)
    def draw(self):
        brain.screen.clear_screen()
        for i in self.e:
            i.draw()
    def click(self):
        if self.EN:
            x,y = brain.screen.x_position(),brain.screen.y_position()
            print(x,y)
            for i in self.e:
                i.click(x,y)
            #self.draw()

ui = UI()
def SEL_ATTON(sd):
    def w():
        global A_SIDE
        log.debug("ATTON: Selected "+str(sd))
        A_SIDE = sd
        ui.EN = False
        state.preSETUP = False
        brain.screen.clear_screen()
        DMui.draw()
    return w
def skills():
    state.mode = modes.skill
    log.debug("COMP: skills")
    speed.skills_drive()
    

mtrx = [
    [1,-1],
    [1,-1]
]    

ui.add(Elem(1,1,"Robot Atton Sel"))

ui.add(Rect(2.5,0.5,8,8,Color.RED))
ui.add(Rect(11.5,0.5,8,8,Color.BLUE))

ui.add(Button(3,1,7,3,Color.RED  ," DEFNC ",SEL_ATTON(1)))

ui.add(Button(3,5,7,3,Color.BLUE ," OFFNC ",SEL_ATTON(-1)))

ui.add(Button(12,1,7,3,Color.RED  ," OFFNC ",SEL_ATTON(-1)))

ui.add(Button(12,5,7,3,Color.BLUE ," DEFNC ",SEL_ATTON(1)))

ui.add(Button(23,1,7,3,Color.ORANGE," skill ",skills))

class modes:
    stop  = 0
    ap    = 1 #atton
    mode1 = 2 #tank
    mode2 = 3 #arcade
    skill = 4

DMui = UI()

def dmode(m):
    def w():
        log.debug('dmode: disabled')
        #if state.dm != m:
        #    log.debug("DM: "+str(m)+" - mode switched")
        #    state.dm = m
        #    controller_1.rumble('.')
        #    anunciator.tgl('M')
        #    if state.mode != modes.ap:
        #        state.mode = m
    return w


DMui.add(Elem(1,1,"Robot Drive Sel"))

DMui.add(Button(1,1,6,3,Color.ORANGE," TANK ",dmode(modes.mode2)))
DMui.add(Button(23,1,5,3,Color.ORANGE," TMP ",dmode(modes.mode1)))



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
        self.LEDCODE = 0
        self.Old_LEDCODE = 0
        #i = 0
        for I in (self.statz):
            #status[I] = i
            self.draw(I)
            #i += 0
    def setLED(self,led:Led,b):
        if b:
            led.on()
        else:
            led.off()
    def code(self,i):
        self.Old_LEDCODE = self.LEDCODE # alows for restoring 
        self.LEDCODE = i
        log.debug('anunc: led 0b'+bin(i))
        self.setLED(led_tlem_r_1,bool(i & 8))# RED 
        self.setLED(led_tlem_r_2,bool(i & 4))# RED
        self.setLED(led_tlem_y_1,bool(i & 2))# Yellow
        self.setLED(led_tlem_y_2,bool(i & 1))# Yellow
    def codeRestore(self):
        old = self.Old_LEDCODE
        self.Old_LEDCODE = self.LEDCODE
        self.LEDCODE = old
        self.code(old)
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
            log.WARNING("ANUNC: WARNING")
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

    def tempCheck(self,func):
        def wrapper(*args,**kwargs):
            self.temps(max(motor_1_motor_a.temperature(),motor_1_motor_b.temperature(),motor_2_motor_a.temperature(),motor_2_motor_b.temperature()))
            return func(*args,**kwargs)
        return wrapper
    
    def temps(self,val):
        """triggers a motor temp warning if val > MOTOR_OVERHEAT

        Args:
            val (int): max motor temp
        """
        self.Temps = val
        if val > MOTOR_OVERHEAT and (not self.states['T']):
            self.states['T'] = True
            self.restrict = True
            anunciator.warn('T')
            for i,m in DRVmotors.items():
                temp = m.temperature()
                if temp > MOTOR_OVERHEAT:
                    anunciator.code(0b1100+i)
                    log.debug("MOTOR "+DRVmotorsNAME[i]+": OVERHEAT - "+str(temp))
            controller_1.screen.set_cursor(2,1)
            controller_1.screen.print(val)
            

        elif self.states['T']:
            self.states['T'] = False
            anunciator.code(0b0000)
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
        self.preSETUP = True
        self.errors = 0    
        self.dm = modes.mode1

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
        self.diff = diff*A_SIDE
        self.calcMotors()
        log()
    
    def stop(self):
        self.Adrive(0,0)

    #region Arcade Controls
    def calcSpeed(self,inv):
        if inv:
            spdDiff = -self.diff
        else:
            spdDiff = self.diff
        return clamp(self.speed - spdDiff,-self.max_speed,self.max_speed)*self.speed_mult

    @status.tempCheck
    def calcMotors(self):
        motor_drivetrain_left.set_velocity(self.calcSpeed(False), PERCENT)
        motor_drivetrain_right.set_velocity(self.calcSpeed(True), PERCENT)
        status.temps(max(motor_1_motor_a.temperature(),motor_1_motor_b.temperature(),motor_2_motor_a.temperature(),motor_2_motor_b.temperature()))

    @state.driverNeeded
    def mspeed(self):
        pos = controller_1.axis3.position()*0.5
        self.speed = pos
        self.calcMotors()

    @state.driverNeeded
    def Mspeed(self):
        pos = controller_1.axis2.position()*1
        self.speed = pos
        self.calcMotors()

    @state.driverNeeded
    def dspeed(self):
        pos = controller_1.axis4.position()*0.5
        self.diff = -pos
        self.calcMotors()

    @state.driverNeeded
    def Dspeed(self):
        pos = controller_1.axis1.position()*1
        self.diff = -pos
        self.calcMotors()
    #endregion Arcade Controls
    #region Tank Controls
    @state.driverNeeded
    @status.tempCheck
    def drive(self):
        """robot drive controls
        """
        log()
        pos = controller_1.axis2.position()
        R = clamp(pos,-self.max_speed,self.max_speed)*self.speed_mult
        pos = controller_1.axis3.position()
        L = clamp(pos,-self.max_speed,self.max_speed)*self.speed_mult
        motor_drivetrain_left.set_velocity(L, PERCENT)
        motor_drivetrain_right.set_velocity(R, PERCENT)

    #endregion Tank Controls
    
    @status.tempCheck
    def ATONdrive(self,L,R):
        """robot Autopilot drive controls
        """
        log()
        motor_drivetrain_left.set_velocity(L, PERCENT)
        motor_drivetrain_right.set_velocity(R, PERCENT)

    @state.autopilotOnly
    def driveSequence(self):
        """Autopilot driveSequence
        """
        def logn(t):
            log.debug("atton: "+t)
        glbls = {
            "Adrive":self.Adrive,
            "wait":wait,
            "print":print,
            "ATONdrive":self.ATONdrive,
            "log":logn
        }
        try:
            if brain.sdcard.is_inserted() and brain.sdcard.exists('atton.py') :
                log.debug("ATTON: SD CARD")
                a = bytes(brain.sdcard.loadfile("atton.py")).decode('ascii')
                print(str(a))
                exec(str(a),glbls)
                self.Adrive(0,0)
            else:
                log.debug("ATTON: Backup\n\tRunning non-SD card code")
                a = '' #atton
                exec(str(a),glbls)
                
                self.Adrive(0,0)
                #Arm()
                #self.Adrive(10,0)
                #wait(100)
                #self.stop()
            log.debug("ATTON: DONE")
            anunciator.code(0b0101)
        except BaseException as e:
            log.WARNING("ATTON: ERROR - "+str(e))
            anunciator.code(0b0110)
            self.Adrive(0,0)
            
    def skills_drive(self):
        def logn(t):
            log.debug("atton skills: "+t)
        glbls = {
            "Adrive":self.Adrive,
            "wait":wait,
            "print":print,
            "ATONdrive":self.ATONdrive,
            "log":logn
        }
        try:
            log.debug("ATTON: Skills")
            a = '' #skills
            exec(str(a),glbls)
            
            self.Adrive(0,0)
            #Arm()
            #self.Adrive(10,0)
            #wait(100)
            #self.stop()
            log.debug("ATTON-S: DONE")
            anunciator.code(0b0101)
        except BaseException as e:
            log.WARNING("ATTON-S: ERROR - "+str(e))
            anunciator.code(0b0110)
            self.Adrive(0,0)
        

speed = speedControlls(driver_pilot_max_speed)

def autonomous_start():
    log.debug("COMP: atton")
    state.mode = modes.ap
    init()
    speed.driveSequence()
    state.mode = modes.mode1

def driver():
    log.debug("COMP: driver")
    anunciator.code(0b0000)
    
    init()
    state.mode = state.dm

#competition.autonomous = autonomous_start

#region buttons
    
modeSwitch = ButtonBinding("down",modes.mode1)

@modeSwitch.Press
def press():
    if not competition.is_competition_switch():
        state.mode = modes.mode2
        state.dm = modes.mode2
        controller_1.rumble('.')
        anunciator.tgl('M')

modeSwitch2 = ButtonBinding("down",modes.mode2)

@modeSwitch2.Press
def press():
    if not competition.is_competition_switch():
        state.mode = modes.mode1
        state.dm = modes.mode1
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
    anunciator.code(0b1010)
    log.save()
    sleep(2,SECONDS)
    anunciator.codeRestore()

#endregion

INITD = False

def init():
    global INITD
    log()
    if not INITD and competition.is_enabled():
        log.debug("INIT: started")
        log.debug("INIT: running code ver: "+CODE_VER)
        INITD = True
        anunciator.tgl('R')

        motor_puncher.set_velocity(0,RPM)

        anunciator.warn('R')
        if brain.sdcard.is_inserted():
            pass
        else:
            log.WARNING("FS: No SD Card")
            anunciator.tgl("S")
        anunciator.code(0b0000)

def collision():
    log.debug("inertial: collision")

competition=Competition(driver,autonomous_start)
init()
inertial.collision(collision)

#region Arcade
#controller_1.axis3.changed(speed.mspeed)
#controller_1.axis4.changed(speed.dspeed)
#controller_1.axis2.changed(speed.Mspeed)
#controller_1.axis1.changed(speed.Dspeed)
#speed.calcMotors()
#endregion

ui.draw()

def ax1():
    if state.mode == modes.mode2:
        speed.Dspeed()

def ax2():
    if state.mode == modes.mode2:
        speed.Mspeed()
    elif state.mode == modes.mode1:
        speed.drive()

def ax3():
    if state.mode == modes.mode2:
        speed.mspeed()
    elif state.mode == modes.mode1:
        speed.drive()

def ax4():
    if state.mode == modes.mode2:
        speed.dspeed()

controller_1.axis3.changed(ax3)
controller_1.axis4.changed(ax4)
controller_1.axis2.changed(ax2)
controller_1.axis1.changed(ax1)

def touch():
    if state.preSETUP:
        ui.click()
    else:
        DMui.click()

brain.screen.pressed(touch)

#controller_1.axis3.changed(speed.drive)
#controller_1.axis2.changed(speed.drive)

motor_drivetrain_left.spin(FORWARD)
motor_drivetrain_right.spin(FORWARD)
motor_puncher.spin(FORWARD)
speed.drive()