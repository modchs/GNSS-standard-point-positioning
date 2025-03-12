# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 14:35:42 2021

@author: chs

CONTROL.py:控制文件 包括文件名、标签
"""
import os
from CONSTANT import ALL_VAR,PRN,ALL_SYS

def Check_Tag(x):
#检查TAG中是否符合输入要求
    
    assert os.path.exists(x['obs_file_path']),'no such file or dir of obs'
    assert os.path.exists(x['nav_file_path']),'no such file or dir of nav'
    assert os.path.exists(x['sp3_file_path']),'no such file or dir of sp3'
    assert os.path.exists(x['clk_file_path']),'no such file or dir of clk'
    #检查文件路径是否存在
    
    for s in x['sys']:
    #检查系统名称
        assert s in ALL_SYS,'unknown system %s'%(s)
    
    assert x['combination'] in ['std','ionofree'],'unknown combination'
    #检查组合方式
    assert x['power'] in ['equal','sin2','piecewise'],'unknown power'
    #检查定权方式
    assert x['eph'] in ['nav','sp3'],'unknown eph/clk'
    #检查轨道钟差
    for s in x['sys']:
    #检查频点
        for f in x['var'][s]:
            assert f in ALL_VAR,'unknown var %s'%f
    
    if(x['combination']=='ionofree'):
    #无电离层组合频段不够
        assert len(x['var'])==2,'wrong number of var for ionofree'

TAG={
#标签
     'obs_file_path':'./input/falk1840.20o',
     #O文件名
     'nav_file_path':'./input/brdm1840.20p',
     #N文件名
     'sp3_file_path':'./input/wum21124.sp3',
     #精密星历文件名
     'clk_file_path':'./input/wum21124.clk',
     #精密钟差文件名
     'sys':['G','C','E'],
     #多系统 -> 'G','C','E'
     's2n':{},
     #为了多系统钟差X和索引转换将GREC转为数字/根据选取的系统排列 
     'PRN':[],
     #以sys为准，列出多系统下所有可能的卫星
     'combination':'std',
     #combination 组合 -> std/ionofree
     'power':'piecewise',
     #power 卫星加权方式 -> equal/sin2/piecewise
     'var':{},
     #var 必要频段 -> ['C1C']/['C1C','C2W']
     'eph':'nav',
     #eph 轨道/钟差选择 -> nav/(sp3/clk)
     'relative_corr':True,
     #relative_corr -> 是否进行相对论改正
     'earth_rot_corr':True,
     #earth_rot_corr -> 是否进行地球自转改正
     'tropo_corr':True,
     #tropo_corr -> 是否进行对流层改正
     'iono_corr':True,
     #iono_corr -> 是否进行电离层单频改正
     'tgd_corr':True,
     #tgd_corr -> 是否进行群延差改正
     'plot_realtime':False,
     #是否实时画图
     'plot_realtime_interval':42
     #实时画图历元间隔
     }

for i,s in enumerate(TAG['sys']):
#enumerte枚举->同时列出下标和值
    TAG['s2n'][s]=i

if(TAG['combination']=='std'):
    TAG['var']['G']=['C2W']
    TAG['var']['C']=['C2I']
    TAG['var']['E']=['C1C']
#选择非组合所使用的频点
elif(TAG['combination']=='ionofree'):
    TAG['var']['G']=['C1W','C2W']
    TAG['var']['C']=['C2I','C6I']

for s in TAG['sys']:
#选取的系统中所有可能的卫星-> 经测试'+'对列表可行
    TAG['PRN']+=PRN[s]
    
