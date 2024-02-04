#do atton code here!
time = int((60*1000)/((1500*2)+2000))+1
for i in range(time):
    wait(2000)
    Adrive(100,0)
    wait(1500)
    
    Adrive(-100,0)
    wait(1500)

    log('cycle '+str(i))
