 # -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 18:46:53 2021

@author: chs

Main.py:主函数 调用SPP/画图
"""
from NAV_FILE import NAV
from OBS_FILE import OBS
from SP3_FILE import SP3
from CLK_FILE import CLK
from SPP import Standard_point_positioning
from COMBINE import Single_point_positioning
from COMPARE import Compare_sp3_nav,compare_eph_new,Compare_clk_nav
from CONTROL import TAG,Check_Tag

import time

def Compare(tag):
#比较轨道钟差
    nav=NAV(tag['nav_file_path'])
    sp3=SP3(tag['sp3_file_path'])
    clk=CLK(tag['clk_file_path'])
    
    prn='G32'
    
    Compare_sp3_nav(prn,nav,sp3,30)
    #compare_eph_new(prn,nav,sp3)
    Compare_clk_nav(prn,nav,clk)
    
    print('comparison ok')
    
def SPP(tag):
#基础标准单点定位 仅支持GPS非组合
    t=[]
    t.append(time.time())
    obs=OBS(tag['obs_file_path'])
    t.append(time.time())
    nav=NAV(tag['nav_file_path'])
    t.append(time.time())
    res=Standard_point_positioning(obs,nav,tag)
    res.Plot('ENU',tag)
    res.Plot('sate',tag)
    res.Plot('DOP',tag)
    res.Print_Console('RMS')
    t.append(time.time())
    
    for i in range(1,len(t)):
        t[i]=t[i]-t[0]
        
    print(t)
    
    print('main spp ok')

def SPP2(tag):
#稍微改进的单点定位 将扩展为多系统多组合
    
    obs=OBS(tag['obs_file_path'])
    nav=NAV(tag['nav_file_path'])
    sp3=SP3(tag['sp3_file_path'])
    clk=CLK(tag['clk_file_path'])
    
    res=Single_point_positioning(obs,nav,sp3,clk,tag)
    
    res.Plot('ENU',tag)
    #res.Plot('sate',tag)
    #res.Print('RMS')
    
    print('main spp2 ok')
    
if __name__=="__main__":

    Check_Tag(TAG)
    #print(TAG)
    #SPP2(TAG)
    SPP(TAG)
    #Compare(TAG)
    print('main ok')
