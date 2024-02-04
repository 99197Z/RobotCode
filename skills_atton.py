#do atton code here!
time = (60*1000)/(1500*2)
for i in range(time):
    Adrive(100,0)
    wait(1500)
    log('IN')
    
    Adrive(-100,0)
    wait(1500)
    log('OUT')
