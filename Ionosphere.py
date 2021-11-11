# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 20:46:20 2021

@author: chs

Ionosphere.py:单频电离层改正
"""

from math import pi,sin,cos
from CONSTANT import c

def Klobuchar(a,b,Ele,Azi,B0,L0,UT):
#a,b广播星历中的改正参数 Ele高度角 Azi方位角
#B,L测站纬度经度(弧度) UT世界时(小时)
#课本 p105
    #print(a,b)
    if(a==[0,0,0,0] or b==[0,0,0,0]):
    #无参数 无法改正
        return 0
    
    EA=(445/(Ele+20))-4
    EA=EA*pi/180
    #测站交点和P'在地心的夹角EA
    Bi=B0+EA*cos(Azi)
    Li=L0+EA*sin(Azi)/cos(B0)
    #P'的地心纬度和经度
    t=UT+Li/15
    #瞬间交P'点处的地方时t
    Bmag=79.93*pi/180
    Lmag=288.04*pi/180
    #地球磁北极
    Bm=Bi+(pi/2-Bmag)*cos(Li-Lmag)
    #计算P'的地磁纬度
    A,P=0,0
    for i in range(0,4):
        A=A+a[i]*(Bm)**i
        P=P+b[i]*(Bm)**i
    #振幅A和周期P
    Tg=5e-9+A*cos(2*pi/P*(t-14))
    #调制在L1载波上的测距码的电离层改正时延Tg(天顶方向)
    secZ=1+2*((96-Ele*180/pi)/90)**3
    #投影函数近似公式
    return Tg*secZ*c
