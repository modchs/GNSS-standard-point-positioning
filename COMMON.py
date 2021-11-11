# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:10:46 2021

@author: chs

COMMON.py:时间类/结果类
sp3/clk尚改进 RES时间未改进
"""
from CONSTANT import ALL_SYS
from math import sqrt
from FUNC import Calc_GREC_time,XYZ2ENU

import matplotlib.pyplot as plt
from copy import deepcopy

class TIME:
#时间类 obs/nav/clk/sp3/res都用到了大量重复时间项 可以单独写成一个时间类
    
    def __init__(self):
    #初始化 无参数 空实例
    #所有内部变量均为列表->obs和res只用一个实例即可 nav/sp3/clk需要多个实例:按卫星索引->需要字典
        self.year,self.month,self.day,self.hour,self.minute,self.sec=[],[],[],[],[],[]
        #年月日时分秒
        
        self.Week={}
        for s in ALL_SYS:self.Week[s]=[]
        #self.Week={'G':[],'C':[],'E':[],'R':[]}
        #周初始化->GPS周/北斗周/..
        self.Sec=deepcopy(self.Week)
        #秒初始化
    
    def Get_timing(self,i,system):
    #获取下标为i处的时间 生成新的时间类
        T=TIME()
        for v in ['year','month','day','hour','minute','sec']:
        #对年月日时分秒赋值
            exec('T.'+v+'.append(self.'+v+'[i])')
        for s in system:
        #对周秒赋值
            T.Week[s].append(self.Week[s][i])
            T.Sec[s].append(self.Sec[s][i])
        
        return T
        #生成了一个长度为1的时刻
    
    def Read_Line(self,line,filetype):
    #从文件的一行(line)里读时间 filetype->文件类型
        if(filetype=='O'):
        #O文件的一行
            self.year.append(int(line[2:6].strip()))
            self.month.append(int(line[7:10].strip()))
            self.day.append(int(line[10:13].strip()))
            self.hour.append(int(line[13:16].strip()))
            self.minute.append(int(line[16:19].strip()))
            self.sec.append(float(line[19:30].strip()))
            #strip 似乎可加可不加
        elif(filetype=='N'):
            self.year.append(int(line[4:9].strip()))
            self.month.append(int(line[9:11].strip()))
            self.day.append(int(line[11:14].strip()))
            self.hour.append(int(line[14:17].strip()))
            self.minute.append(int(line[17:20].strip()))
            self.sec.append(int(line[21:23].strip()))
            #导航电文年月日时分秒(TOC) 第一行 下标i
        elif(filetype=='sp3'):
            print('not finished yet')
        elif(filetype=='clk'):
            print('not finished yet')
        
        self.Update()
        
    def Update(self):
    #年月日时分秒转换为四系统时间
        for S in ALL_SYS:
            if(S=='R'):continue
            #暂时不支持GLONASS
            tmp1,tmp2=Calc_GREC_time(S,self.year[-1],self.month[-1],self.day[-1],
                                    self.hour[-1],self.minute[-1],self.sec[-1])
            self.Week[S].append(tmp1)
            self.Sec[S].append(tmp2)
        
class RES:
#单点定位输出结果类 包含XYZ/ENU/卫星数/DOP值
#增加了中间结果 每个历元的可视卫星/坐标/高度角/方位角
#所有对res实例的改动被限制在 Standard_point_positioning中
    def add_sate(self,all_sate):
    #添加每个历元的可见卫星
        self.sate.append(all_sate)
        self.all_sate_num.append(len(all_sate))
        
        for s in ALL_SYS:
            self.sate_num[s].append(0)
        
        for prn in all_sate:
            self.sate_num[prn[0]][-1]+=1
        
    def add_station_xyz(self,a,b,c):
    #添加测站坐标
        self.x.append(a)
        self.y.append(b)
        self.z.append(c)
    
    def add_ENU(self):
    #添加enu
        tmp1,tmp2,tmp3=XYZ2ENU(self.x[-1],self.y[-1],self.z[-1],self.x0,self.y0,self.z0)
        self.e.append(tmp1)
        self.n.append(tmp2)
        self.u.append(tmp3)
    
    def add_DOP(self,Q):
    #添加DOP值
        #n=Q.shape[0]
        #Q的行数 shape[1]表示列数 Q是方阵
        qxx,qyy,qzz=Q[0,0],Q[1,1],Q[2,2]
        qtt=Q[3,3]
        #多系统?
        
        self.PDOP.append(sqrt(qxx+qyy+qzz))
        self.TDOP.append(sqrt(qtt))
        self.GDOP.append(sqrt(qxx+qyy+qzz+qtt))
    
    def update_sate_xyz(self,a,b,c):
    #更新卫星坐标 a/b/c都是元组
        self.sx[-1],self.sy[-1],self.sz[-1]=a,b,c
        
    def update_Ele_Azi(self,E,A):
    #更新高度角
        self.Ele[-1],self.Azi[-1]=E,A
        
    def init(self):
    #初始化卫星坐标和高度角 这些变量都会随迭代自行更新 只需要append即可 增加的元素无所谓
        for v in ['sx','sy','sz','Ele','Azi']:
            exec('self.'+v+'.append([])')
    
    def __init__(self,obs):
    #初始化
        self.name=obs.name
        #测站名
        self.x0,self.y0,self.z0=obs.x0,obs.y0,obs.z0
        #测站坐标近似值传递
        self.x,self.y,self.z=[],[],[]
        #测站坐标解算序列
        self.e,self.n,self.u=[],[],[]
        #站心坐标
        self.sate,self.Ele,self.Azi=[],[],[]
        #各历元的可见卫星编号->2维 / 卫星高度角->2维 / 卫星方位角角->2维
        #下标1是历元 下标2无特殊含义->序号
        self.sate_num={}
        #见卫星数->字典多系统
        self.all_sate_num=[]
        #总卫星数
        for s in ALL_SYS:
            self.sate_num[s]=[]
        
        self.sx,self.sy,self.sz=[],[],[]
        #卫星坐标(sate->xyz) -> 2维
        self.T=deepcopy(obs.T)
        #时间类 保险起见还是复制一份
        self.h=[]
        #单天解 只考虑时分秒项
        for i in range(len(self.T.year)):
            self.h.append(self.T.hour[i]+self.T.minute[i]/60.0+self.T.sec[i]/3600.0)
        
        self.PDOP,self.TDOP,self.GDOP=[],[],[]
        #卫星数 DOP值
        #考虑HDOP和VDOP?
        
    def Print_Console(self,obj):
    #输出精度    
        if(obj=='RMS' or obj=='rms'):
            RMS=[0,0,0]
            #ENU三方向
            for i in range(len(self.e)):
            #求和
                RMS[0]+=(self.e[i])**2
                RMS[1]+=(self.n[i])**2
                RMS[2]+=(self.u[i])**2
            
            for i in range(3):
            #取平均 开根号
                RMS[i]/=len(self.e)
                RMS[i]=sqrt(RMS[i])
            
            print('RMS(ENU):',RMS)
            
    def Plot(self,obj,TAG):
    #画图 obj指定对象 -> ENU 卫星数 DOP值
        if(obj=='enu' or obj=='ENU'):plt_num=1
        elif(obj=='sate' or obj=='SATE'):plt_num=2
        elif(obj=='dop' or obj=='DOP'):plt_num=3
        #不同对象 不同编号
        
        if(TAG['plot_realtime']):
            ax=plt.figure(plt_num,(10, 6))
            #实时画图暂时只能单图
            plt.pause(0.01)
            #暂停才能看到图
            ax.clear()
            #实时画图 clear清除之前的结果
        else:
            plt.figure(plt_num,(10, 6))
        
        ax=plt.figure(plt_num,(10, 6))
        
        plt.title(self.name)
        plt.xlabel('time/h')
        plt.xlim(0,24)
        #x轴 24小时
        x_major_locator=plt.MultipleLocator(2)  
        ax=plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        #坐标轴2h间隔
        n=len(self.e)
        #数据长度
        
        if(obj=='enu' or obj=='ENU'):
        #绘制ENU图表
            
            plt.ylabel('ENU/m')
            plt.ylim(-20,20)
            
            plt.plot(self.h[0:n],self.e,color='m',label='E',linewidth=1)
            plt.plot(self.h[0:n],self.n,color='c',label='N',linewidth=1)
            plt.plot(self.h[0:n],self.u,color='r',label='U',linewidth=1)
            #控制t的长度 可以显示任意长度的结果
            
        if(obj=='sate' or obj=='SATE'): 
        #绘制卫星数图表
        
            plt.ylabel('number of sate')
            plt.ylim(0,40)
            
            plt.plot(self.h[0:n],self.all_sate_num,color='r',label='sate',linewidth=1)
            
            if('G'in TAG['sys']):
                plt.plot(self.h[0:n],self.sate_num['G'],color='b',label='G',linewidth=1)
            if('C'in TAG['sys']):
                plt.plot(self.h[0:n],self.sate_num['C'],color='y',label='C',linewidth=1)
            if('E'in TAG['sys']):
                plt.plot(self.h[0:n],self.sate_num['E'],color='c',label='E',linewidth=1)
            
            plt.legend()
            
        if(obj=='DOP' or obj=='dop'):
        #DOP
            plt.ylabel('DOP')
            plt.ylim(0,5)
            
            plt.plot(self.h[0:n],self.PDOP,color='m',label='PDOP',linewidth=1)
            plt.plot(self.h[0:n],self.TDOP,color='c',label='TDOP',linewidth=1)
            plt.plot(self.h[0:n],self.GDOP,color='r',label='GDOP',linewidth=1)
            #控制t的长度 可以显示任意长度的结果
            
        plt.legend()
        #图例   