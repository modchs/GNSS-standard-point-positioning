# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 16:06:37 2021

@author: chs
"""

from scipy import interpolate

import matplotlib.pyplot as plt
from CONSTANT import c
from CORRECT import Relative_eff_corr as REC

def Compare_sp3_nav(prn,nav,sp3,interval):
#比较精密星历和导航星历的差异 卫星编号prn
#nav 导航电文 sp3 精密星历 interval 间隔
    
    dx,dy,dz=[],[],[]
    #两者插值 
    GPS_time,hour_time=[],[]
    #GPS时用于内插 单天小时计时用于画图
    KIND=7
    #内插阶数
    fx=interpolate.interp1d(sp3.GPS_sec,sp3.x[prn],kind=KIND)
    fy=interpolate.interp1d(sp3.GPS_sec,sp3.y[prn],kind=KIND)
    fz=interpolate.interp1d(sp3.GPS_sec,sp3.z[prn],kind=KIND)
    
    #指定内插阶数 内插函数
    #kind 次数的选择？ 越大越好? 7 9 11 区别不明显 >3时偶数不行?
    
    week=sp3.GPS_week[0]
    #单天解 可以不考虑GPS周的影响
    
    for i in range(int(sp3.GPS_sec[0]),int(sp3.GPS_sec[-1]),int(interval)):
    #以精密星历范围为准
    #interval 为间隔 比较序列
        GPS_time.append(i)
        hour_time.append((i-sp3.GPS_sec[0])/3600.0)
        
        index=nav.find_nav_index(prn,week,i)
        tmpx,tmpy,tmpz=nav.Calc_sate_pos_nav(prn,index,week,i)
        
        dx.append(tmpx-fx(i))
        dy.append(tmpy-fy(i))
        dz.append(tmpz-fz(i))
    
    plt.figure(1, (10, 6))
    plt.scatter(hour_time,dx,color='r',s=2)
    plt.scatter(hour_time,dy,color='g',s=2)
    plt.scatter(hour_time,dz,color='c',s=2)
    
    plt.title('prn:'+str(prn)+' sp3 vs nav')
    plt.ylabel('delta/m')
    plt.xlabel('time/h')
    
    plt.xlim(0,24)
    #设置横轴范围
    x_major_locator=plt.MultipleLocator(2)  
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    #坐标轴2h间隔
    
    #plt.scatter(sp3_time_series,sp3_X[prn],color='r',label='x',s=20);
    #plt.scatter(insert_time_series,f(insert_time_series),color='k',label='x',s=1);
    

def compare_eph_new(prn,nav,sp3):
#只画 15min间隔点 不内插    
    dx,dy,dz=[],[],[]
    hour_time=[]
    #GPS时用于内插 单天小时计时用于画图
    week=sp3.GPS_week[0]
    #单天解 可以不考虑GPS周的影响
    
    for i in range(len(sp3.GPS_sec)):
        hour_time.append((sp3.GPS_sec[i]-sp3.GPS_sec[0])/3600.0)
        
        index=nav.find_nav_index(prn,week,sp3.GPS_sec[i])
        tmpx,tmpy,tmpz=nav.Calc_sate_pos_nav(prn,index,week,sp3.GPS_sec[i])

        dx.append(tmpx-sp3.x[prn][i])
        dy.append(tmpy-sp3.y[prn][i])
        dz.append(tmpz-sp3.z[prn][i])
    
    plt.figure(1, (10, 6))
    plt.scatter(hour_time,dx,color='g',s=20)
    plt.scatter(hour_time,dy,color='c',s=20)
    plt.scatter(hour_time,dz,color='r',s=20)
    
    plt.title('prn:'+str(prn)+' sp3 vs nav')
    plt.ylabel('delta/m')
    plt.xlabel('time/h')
    
    plt.xlim(0,24)
    #设置横轴范围
    x_major_locator=plt.MultipleLocator(2)  
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    #坐标轴2h间隔
    
    #plt.scatter(sp3_time_series,sp3_X[prn],color='r',label='x',s=20);
    #plt.scatter(insert_time_series,f(insert_time_series),color='k',label='x',s=1);


def Compare_clk_nav(prn,nav,clk):
#不内插 只画30sec间隔    
    delta=[]
    hour_time=[]
    #GPS时用于内插 单天小时计时用于画图
    week=clk.GPS_week[0]
    #单天解 可以不考虑GPS周的影响
    
    for i in range(len(clk.GPS_sec)):
        hour_time.append((clk.GPS_sec[i]-clk.GPS_sec[0])/3600.0)
        
        index=nav.find_nav_index(prn,week,clk.GPS_sec[i])
        dt=clk.GPS_sec[i]-nav.GPS_sec[prn][index]
        
        nav_t=nav.a0[prn][index]+nav.a1[prn][index]*dt+nav.a2[prn][index]*(dt**2)
        #nav_t+=REC(nav,prn,index,week,clk.GPS_sec[i])
        #print(nav_t-clk.t[prn][i])
        delta.append((nav_t-clk.t[prn][i])*c)
    
    plt.figure(2, (10, 6))
    plt.scatter(hour_time,delta,color='r',s=2);
    plt.title('clk vs nav')
    plt.ylabel('delta/m')
    plt.xlabel('time/h')
    
    plt.ylim(-1,1)
    plt.xlim(0,24)
    #设置横轴范围
    x_major_locator=plt.MultipleLocator(2)  
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    #坐标轴2h间隔
    