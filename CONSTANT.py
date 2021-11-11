# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 16:33:30 2021

@author: chs
CONSTANT.py:保存常量
"""
c=299792458.0
#光速 m/s
a=6378137
#地球长半轴 m
e2=0.0066943799013
#e(扁率)平方
GM=3.986004415e14
#万有引力常数*地球质量 
w_e=7.2921151467e-5
#地球自传角速度 rad/s
JD0=2444244.5
#GPS时起点的儒略历日期

GPS_num=33#GPS卫星个数+1 (更新完成后就删除)

ALL_SYS=['G','C','E','R']
#四系统
NUM={'G':33,'C':61,'E':37,'R':27}
#多系统卫星数目(GCER)(最大索引下标 +1)取值可略大 防止越界
PRN={'G':[],'C':[],'E':[],'R':[]}
#多系统全部卫星号 单个系统遍历用
ALL_PRN=[]
#所有系统的所有卫星 全体遍历用
for s in ALL_SYS:
#四系统遍历 NUM.keys()返回NUM字典中所有的索引值
    for i in range(1,NUM[s]):
    #每个系统的卫星数 没有0号卫星
        if(i<10):number='0'+str(i)
        else:number=str(i)
        prn=s+number
        #组成新的字符串下标 添加中间占位的0
        PRN[s].append(prn)
        ALL_PRN.append(prn)

VAR={
     'G':['C1C','L1C','C1W','L2W','C2W'],
     #GPS频点 此处介绍暂不展开 参照rinex305标准文件
     'C':['C2I','L2I','C6I','L6I','C1I','C7I'],
     #BDS频点 B1:C2I B3:C6I
     #北斗频点的问题尚未完全搞清楚 频点在所有文件中并不统一
     #FALK中貌似没有北斗2 HKT430中貌似没有北斗3..
     #暂时先不使用B2的载波..
     'E':['C1C'],
     #Galileo 暂时不添加
     'R':[]
     #GLONASS:
     }
#多系统频点索引
ALL_VAR=[]
#所有频点
for s in ALL_SYS:
    for v in VAR[s]:
        if(v not in ALL_VAR):
            ALL_VAR.append(v)
#为了避免频点名重复,如C1C在GRE中都有

freq,Lambda={},{}
#频率索引(Hz) 波长索引(m)
freq['C1C']=freq['C1W']=freq['L1W']=1575420000.0
freq['C2W']=freq['L2W']=1227600000.0

