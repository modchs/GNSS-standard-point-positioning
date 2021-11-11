# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 09:28:58 2021

@author: chs
FUNC.py:常用函数
"""
from math import atan2,atan,sqrt,sin,cos
from CONSTANT import a,e2,JD0,ALL_SYS

def XYZ2BLH(X,Y,Z):
#直角坐标转大地坐标 暂时不用输出H
    L=atan2(Y,X)
    B0=atan(Z/sqrt(X*X+Y*Y))
    while(1):
        N=a/sqrt(1-e2*sin(B0)*sin(B0))
        H=Z/sin(B0)-N*(1-e2)
        B=atan(Z*(N+H)/(sqrt(X*X+Y*Y)*(N*(1-e2)+H)))
        if(abs(B-B0)<1e-12):
            break
        B0=B
        
    return B,L

def XYZ2ENU(X,Y,Z,X0,Y0,Z0):
#直角坐标转站心坐标 XYZ 目标点 X0 Y0 Z0原点
    dx=X-X0
    dy=Y-Y0
    dz=Z-Z0
    
    B0,L0=XYZ2BLH(X0,Y0,Z0)#参考站坐标
    
    E=-dx*sin(L0)+dy*cos(L0)
    N=-dx*sin(B0)*cos(L0)-dy*sin(B0)*sin(L0)+dz*cos(B0)
    U=dx*cos(B0)*cos(L0)+dy*cos(B0)*sin(L0)+dz*sin(B0)
    
    return E,N,U
    
def ENU2POL(E,N,U):
#站心坐标转极坐标
    Ele=atan(U/sqrt(E**2+N**2))
    #高度角 弧度制
    Azi=atan2(E,N)
    #方位角 弧度制
    return Ele,Azi

def Calc_GPS_time(year,month,day,hour,minute,sec):
#年月日时分秒转GPS周和GPS秒
    if (month<=2):
        year=year-1
        month=month+12
    #特判
    JD=int(365.25*year)+int(30.6001*(month+1))+day+(hour+minute/60.0+sec/3600.0)/24.0+1720981.5
    #hour=hour+minute/60.0+sec/3600.0
    #JD=1721013.5+year*367-int(7.0/4.0*(year+int((month+9.0)/12.0)))+day+hour/24.0+int(275*month/9.0)
    #儒略历计算 两种计算方式
    
    GPS_week=int((JD-JD0)/7)
    GPS_sec=(JD-JD0-7*GPS_week)*24.0*3600.0
    #GPS周 GPS秒
    return GPS_week,GPS_sec

def Calc_BDS_time(year,month,day,hour,minute,sec):
#计算北斗时
    week,sec=Calc_GPS_time(year,month,day,hour,minute,sec)
    BDS_week=week-1356
    BDS_sec=sec-14
    #BDT和GPST的差值为定值
    return BDS_week,BDS_sec

def Calc_GREC_time(S,year,month,day,hour,minute,sec):
#计算不同系统时间基准下的周秒
    if (month<=2):
        year=year-1
        month=month+12
    #特判
    JD=int(365.25*year)+int(30.6001*(month+1))+day+(hour+minute/60.0+sec/3600.0)/24.0+1720981.5
    #hour=hour+minute/60.0+sec/3600.0
    #JD=1721013.5+year*367-int(7.0/4.0*(year+int((month+9.0)/12.0)))+day+hour/24.0+int(275*month/9.0)
    #儒略历计算 两种计算方式
    GPS_week=int((JD-JD0)/7)
    GPS_sec=(JD-JD0-7*GPS_week)*24.0*3600.0
    
    if(S=='G' or S=='E'):return GPS_week,GPS_sec
    #GPST
    elif(S=='C'):
    #BDT
        BDS_week=GPS_week-1356
        BDS_sec=GPS_sec-14
        #BDT和GPST的差值为定值
        return BDS_week,BDS_sec

def GREC_exist(line):
#判断一行中GREC是否出现过
    for s in ALL_SYS:
        if s in line:return True
    return False
        