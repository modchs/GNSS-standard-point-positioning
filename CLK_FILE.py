# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 20:03:51 2021

@author: chs
"""
from CONSTANT import GPS_num
from FUNC import Calc_GPS_time

from scipy.interpolate import interp1d
from copy import deepcopy

class CLK:
    
    def __init__(self,filename='null'):
        
        self.t=[[] for i in range(GPS_num)]
        
        self.year=[]
        self.month=[]
        self.day=[]
        self.hour=[]
        self.minu=[]
        self.sec=[]
        
        self.GPS_week=[]
        self.GPS_sec=[]
        #所有卫星钟差钟差对应的的时间序列应该是相同的
        
        self.f=deepcopy(self.t)
        #内插函数
        assert filename!='null','lack of clk filename'
        
        self.Read_clk_file(filename)
        #初始化同时读文件
        self.Kind=7
        #内插阶数
        self.Intetrpolate()
        #内插
        
    def Calc_t(self,prn,sec):
    #通过内插函数求时间
        assert sec<=self.GPS_sec[-1] and sec>=self.GPS_sec[0],'date not match for obs&clk'
        #超出内插范围 可能是文件日期和观测文件不匹配
        return self.f[prn](sec)
    
    def Intetrpolate(self):
    #内插    
        for prn in range(1,GPS_num):
        #对每一颗卫星
            if(self.t[prn]==[]):continue
            #GPS23 信息缺失?
            #self.fx[prn]=lagrange(self.GPS_sec,self.x[prn])
            self.f[prn]=interp1d(self.GPS_sec,self.t[prn],kind=self.Kind)
        
    def Read_clk_file(self,filename):
    #读clk文件
        
        #output=open('clk_test.txt','w')
        clk_file=open(filename,'r')
        clk_data=clk_file.readlines()
        clk_file.close()
        
        for line in clk_data:
            if ('END OF HEADER') in line:
                clk_begin=clk_data.index(line)+1
                break
        #找到clk文件表头结束位置 同O文件

        for i in range(clk_begin,len(clk_data)):
        #遍历所有行    
            if('AS' in clk_data[i] and 'G' in clk_data[i]):
            #之后每一行...行标志为'AS'
            #且是GPS卫星
                prn=int(clk_data[i][4:6])
                #卫星号 取两位                
                if(prn==1):
                #时间轴只用计算一次 虽然时间项在每行都出现 但是有大量重复
                    self.year.append(int(clk_data[i][8:12]))
                    self.month.append(int(clk_data[i][13:15]))
                    self.day.append(int(clk_data[i][16:18]))
                    self.hour.append(int(clk_data[i][19:21]))
                    self.minu.append(int(clk_data[i][22:24]))
                    self.sec.append(float(clk_data[i][25:34]))
                    
                    tmp1,tmp2=Calc_GPS_time(self.year[-1],self.month[-1],self.day[-1],
                                           self.hour[-1],self.minu[-1],self.sec[-1])
                    self.GPS_week.append(tmp1)
                    self.GPS_sec.append(tmp2)
                    #计算对应UTC的GPS时
                
                #output.write(str(self.year[-1])+' '+str(self.month[-1])+' '+str(self.day[-1])+' '+
                #            str(self.hour[-1])+' '+str(self.minu[-1])+' '+str(self.sec[-1])+'\n')
                
                self.t[prn].append(float(clk_data[i][40:59].strip()))
                #钟差
                
                #output.write(str(self.t[prn][-1])+'\n')
        
if __name__=='__main__':
    
    '''
    clk=CLK()
    clk.Read_clk_file('wum21124.clk')
    '''
    
    print('clk ok')
    