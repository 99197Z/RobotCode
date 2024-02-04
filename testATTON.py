import turtle
from pygame.math import Vector2
import time
m = 0
d=0
T=0
mod=1
Mod=-1
mtrx = [
    [1,-1],
    [1,-1]
]
def tick():
    turtle.left((5*m*d)*T)
    turtle.forward(m*T)
    turtle.dot(4)
   

def Adrive(M,D):
    global m,d
    m=(M*Mod)/1000
    d=(D*mod)/1000


def sleep(t):
    global T
    T = t
    tick()
    T=0
def goto(x,y):
    turtle.penup()
    turtle.goto(x*150,y*200)
    turtle.pendown()
    turtle.right(turtle.heading())
    turtle.left(90)
glbls = {
            "Adrive":Adrive,
            "wait":sleep,
            "print":print
        }

turtle.penup()
turtle.goto(-75,-200)
turtle.pendown()
turtle.left(90)

turtle.forward(400)

turtle.penup()
turtle.goto(200,0)
turtle.pendown()
turtle.left(90)
turtle.forward(500)

with open("atton.py","r") as f:
    turtle.pencolor(1,0,0)
    tx = f.read()
    goto(0,1)
    mod=mtrx[1][0]
    exec(tx,glbls)
    turtle.dot(6)
    
    mod=mtrx[1][1]
    m=0
    d=0
    goto(-1,1)
    exec(tx,glbls)
    turtle.dot(6)

    Mod=1
    mod=mtrx[0][0]
    turtle.pencolor(0,0,1)

    goto(0,-1)
    exec(tx,glbls)
    turtle.dot(6)

    mod=mtrx[0][-1]
    m=0
    d=0
    goto(-1,-1)
    exec(tx,glbls)
    turtle.dot(6)
input()


