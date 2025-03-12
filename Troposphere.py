# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 11:29:30 2021

@author: chs
"""

from math import exp,sin,pi,tan

#暂使用标准气象元素法
def Saastamoinen(E):
#对流程改正 Saastamoinen模型
#E高度角 Ps/es/Ts 大气压(mbar)/水汽压(mbar)/气温(K)
    Ps=1013.25
    Ts=273.15+20
    RH=0.5
    #RH->相对湿度
    es=RH*exp(-37.2465 + 0.213166*Ts - 0.000256908*Ts*Ts)
    
    dE=16/Ts*(Ps+4810/Ts*es)/tan(E)
    dE=dE*pi/180/60
    #弧度制
    
    ds=0.002277/sin(E+dE)*(Ps+(1255/Ts+0.05)*es-1.16/(tan(E)**2))
    
    return ds


print(Saastamoinen(pi/2.0))