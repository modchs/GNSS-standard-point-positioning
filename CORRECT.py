# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 10:37:01 2021

@author: chs
CORRECT.py:包含其他改正如地球自转、相对论等
"""
from CONSTANT import w_e,GM
from math import sin,sqrt

def Earth_rot_corr(x,y,t):
#地球自转改正  课本p129
#xy地固坐标 t传播时间
    newx=x+w_e*t*y
    newy=y-w_e*t*x
    return newx,newy


def Relative_eff_corr(nav,prn,index,GPS_week,GPS_sec):
#相对论效应 非圆轨道误差 课本p83/84
    dt=GPS_sec-nav.toe[prn][index]
    #如果要处理长时间序列应该加上week项
    n_v=sqrt(GM)/(nav.sqrtA[prn][index]**3)+nav.dn[prn][index]
    #卫星运动的平均角速度
    M=nav.M0[prn][index]+n_v*dt
    #平近点角
    E=M
    while(1):
        tmp=M+nav.e[prn][index]*sin(E)
        if(abs(tmp-E)<1e-12):
            break
        E=tmp
    #偏近点角
    dt_corr=-2290.0*(1e-9)*nav.e[prn][index]*sin(E)
    #钟差非圆轨道改正
    return dt_corr
    