# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 19:28:25 2021

@author: chs
"""
from CONSTANT import GPS_num
from FUNC import Calc_GPS_time
from copy import deepcopy
from scipy.interpolate import interp1d


class SP3:
    
    def __init__(self,filename='null'):
        
        tmp=[[] for i in range(GPS_num)]
        
        self.year=[]
        self.month=[]
        self.day=[]
        self.hour=[]
        self.minu=[]
        self.sec=[]
        
        self.GPS_week=[]
        self.GPS_sec=[]
        
        self.x=deepcopy(tmp)
        self.y=deepcopy(tmp)
        self.z=deepcopy(tmp)
        
        self.fx=deepcopy(tmp)
        self.fy=deepcopy(tmp)
        self.fz=deepcopy(tmp)
        #xyz插值函数
        assert filename!='null','lack of sp3 filename'
        #断言 文件名存在
        self.Read_sp3_file(filename)
        #调用内部函数 读文件
        self.Kind=7
        #内插阶数
        self.Interpolate()
    
    def Interpolate(self):
    #内插
        for prn in range(1,GPS_num):
        #对每一颗卫星
            if(self.x[prn]==[]):continue
            #GPS23 信息缺失?
            #self.fx[prn]=lagrange(self.GPS_sec,self.x[prn])
            self.fx[prn]=interp1d(self.GPS_sec,self.x[prn],kind=self.Kind)
            self.fy[prn]=interp1d(self.GPS_sec,self.y[prn],kind=self.Kind)
            self.fz[prn]=interp1d(self.GPS_sec,self.z[prn],kind=self.Kind)
            print('%s sp3 ok'%prn)
            #暂时只用GPS秒插值 可用于一周内的解
            #拉格朗日插值 存在问题 
            #根据实验 kind=7 能达到比较好的效果
    
    def Calc_sate_pos_sp3(self,prn,sec):
    #返回卫星坐标
        assert sec<=self.GPS_sec[-1] and sec>=self.GPS_sec[0],'date not match for obs&sp3'
        #超出内插范围 可能是文件日期和观测文件不匹配
        return self.fx[prn](sec),self.fy[prn](sec),self.fz[prn](sec)
    
    def Read_sp3_file(self,filename):
    #读sp3文件 xyz
    
        #output=open('sp3_test.txt','w')
        sp3_file=open(filename,'r')
        sp3_data=sp3_file.readlines()
        sp3_file.close()

        for i in range(len(sp3_data)):
        #遍历所有行    
            if('*  ' in sp3_data[i]):
            #时间行 标志为'*  ' 两个空格
                j=1
                #j:当前时间行下的第几行
                self.year.append(int(sp3_data[i][3:7]))
                self.month.append(int(sp3_data[i][8:10]))
                self.day.append(int(sp3_data[i][11:13]))
                self.hour.append(int(sp3_data[i][14:16]))
                self.minu.append(int(sp3_data[i][17:19]))
                self.sec.append(float(sp3_data[i][20:31]))
                
                tmp1,tmp2=Calc_GPS_time(self.year[-1],self.month[-1],self.day[-1],
                                       self.hour[-1],self.minu[-1],self.sec[-1])
                self.GPS_week.append(tmp1)
                self.GPS_sec.append(tmp2)
                #计算对应UTC的GPS时
                
                #output.write(str(self.year[-1])+' '+str(self.month[-1])+' '+str(self.day[-1])+' '+
                #            str(self.hour[-1])+' '+str(self.minu[-1])+' '+str(self.sec[-1])+'\n')
                
                while('G' in sp3_data[i+j]):
                #依旧是卫星行 没有到下一个时间行
                    prn=int(sp3_data[i+j][2:4])
                    #卫星号 取两位
                    self.x[prn].append(float(sp3_data[i+j][5:18].strip())*1000.0)
                    self.y[prn].append(float(sp3_data[i+j][19:32].strip())*1000.0)
                    self.z[prn].append(float(sp3_data[i+j][33:46].strip())*1000.0)
                    #xyz 单位km 改成m
                    #output.write(str(prn)+' '+str(self.x[prn][-1])+' '+str(self.y[prn][-1])
                    #            +' '+str(self.z[prn][-1])+'\n')
                    j+=1
                    #下一个卫星

if __name__=='__main__':
    
    '''
    sp3=SP3()
    sp3.Read_sp3_file('wum21124.sp3')
    '''
    print('sp3 ok all')
    
    