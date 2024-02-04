#do atton code here!
for i in range(20):
    Adrive(100,0)
    wait(1500)
    
    Adrive(-100,0)
    wait(1500)

    log('cycle '+str(i))
