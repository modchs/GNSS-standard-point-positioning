# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 11:04:52 2021

@author: chs

NAV_FILE.py:读N文件 计算卫星坐标
"""
from copy import deepcopy
#deepcopy函数可以复制包含列表的变量的副本 python默认复制方式是浅拷贝
#使用后可简化初始化的代码量

from CONSTANT import GM,w_e,NUM,ALL_PRN
from math import sqrt,sin,cos,atan2
from COMMON import TIME
from FUNC import GREC_exist

class NAV:
    
    def __init__(self,filename='null'):
    #同OBS 必须初始化
        
        self.T={}
        for prn in ALL_PRN:self.T[prn]=TIME()
        #times为一个字典 下标为卫星号 每个键值对应一个时间实例
        tmp={}
        for prn in ALL_PRN:tmp[prn]=[]
        #tmp起模板作用
        self.a0,self.a1,self.a2=deepcopy(tmp),deepcopy(tmp),deepcopy(tmp)
        self.Crs,self.dn,self.M0=deepcopy(tmp),deepcopy(tmp),deepcopy(tmp)
        self.Cuc,self.e,self.Cus,self.sqrtA=deepcopy(tmp),deepcopy(tmp),deepcopy(tmp),deepcopy(tmp)
        self.toe,self.Cic,self.Omega,self.Cis=deepcopy(tmp),deepcopy(tmp),deepcopy(tmp),deepcopy(tmp)
        self.i0,self.Crc,self.w,self.Omega_v=deepcopy(tmp),deepcopy(tmp),deepcopy(tmp),deepcopy(tmp)
        self.i_v=deepcopy(tmp)
        self.TGD=deepcopy(tmp)
        #导航星历参数 第一下标为卫星编号 第二下标为时序 下标和O文件并不一致 采样率不同
        
        self.alpha=[0,0,0,0]
        self.beta=[0,0,0,0]
        #单频电离层改正四参数
        
        assert filename!='null','lack of NAV filename'
        #初始化时需要声明路径
        self.Read_nav_file(filename)
        #初始化时就调用读文件函数
    def Check_type(self,line):
    #文件类型检查
        Type=line.split()[1]
        assert Type=='NAVIGATION','wrong file for NAV'
        
    def Read_iono(self,data):
    #读取电离层改正参数
        for line in data:
            if('IONOSPHERIC CORR' in line):
                #如果找不到就不读 没有影响
                v=line.split()
                if('GPSA' in line):
                    for i in range(4):
                        self.alpha[i]=float(v[i+1])
                elif('GPSB' in line):
                    for i in range(4):
                        self.beta[i]=float(v[i+1])
    
    def Get_begin(self,data):
    #找到表头结束位置 返回index
        for line in data:
            if ('END OF HEADER') in line:
                return data.index(line)+1
    
    def Read_nav_file(self,filename):
    #读取导航电文(N(P)文件) 获取一系列导航电文参数
        
        nav_file=open(filename,'r')
        data=nav_file.readlines()
        nav_file.close()
        #关闭文件
        self.Check_type(data[0])
        #检查文件类型
        self.version=data[0].split()[0]
        #读取版本号
        for i in range(len(data)):
            if 'D+' in data[i] or 'D-' in data[i]:
                data[i]=data[i].replace('D+','e+')
                data[i]=data[i].replace('D-','e-')
        #把D替换为e 否则科学计数法无法读入
        self.Read_iono(data)
        #读电离层参数
        nav_begin=self.Get_begin(data)
        #找到N文件表头结束位置 同O文件
        
        for i in range(nav_begin,len(data)):
        #遍历导航电文 寻找G
            if GREC_exist(data[i]):
            #当前行有GREC
                if('R' in data[i]):continue
                #暂时不支持R
                prn=data[i][0:3]
                #卫星编号
                if(prn[1]==' '):prn[1]='0'
                #可能还有中间不是0占位的情况
                self.T[prn].Read_Line(data[i],'N')
                #使用时间类输入
                
                self.a0[prn].append(float(data[i][23:42].strip()))
                self.a1[prn].append(float(data[i][42:61].strip()))
                self.a2[prn].append(float(data[i][61:80].strip()))
                #钟差三参数
                
                self.Crs[prn].append(float(data[i+1][23:42].strip()))
                self.dn[prn].append(float(data[i+1][42:61].strip()))
                self.M0[prn].append(float(data[i+1][61:80].strip()))
                #第二行 IODE不需要
                
                self.Cuc[prn].append(float(data[i+2][4:23].strip()))
                self.e[prn].append(float(data[i+2][23:42].strip()))
                self.Cus[prn].append(float(data[i+2][42:61].strip()))
                self.sqrtA[prn].append(float(data[i+2][61:80].strip()))
                #第三行
                
                self.toe[prn].append(float(data[i+3][4:23].strip()))
                self.Cic[prn].append(float(data[i+3][23:42].strip()))
                self.Omega[prn].append(float(data[i+3][42:61].strip()))
                self.Cis[prn].append(float(data[i+3][61:80].strip()))
                #第四行
                
                self.i0[prn].append(float(data[i+4][4:23].strip()))
                self.Crc[prn].append(float(data[i+4][23:42].strip()))
                self.w[prn].append(float(data[i+4][42:61].strip()))
                self.Omega_v[prn].append(float(data[i+4][61:80].strip()))
                #第四行
                
                self.i_v[prn].append(float(data[i+5][4:23].strip()))
                #第五行
                
                self.TGD[prn].append(float(data[i+6][42:61].strip()))
                #第六行
        
        print('nav finished')
        
    def find_nav_index(self,prn,week,sec):
    #**************************************week和sec可以改为时间实例?
    #寻找合适的导航星历 返回下标
    #prn卫星编号 week,sec为对应prn所属的系统的周秒
    #遍历所有时间 求差值绝对值 选最小的 不能直接判断<1h 有个别情况第一个历元从2h开始 0h无法得出结果
        S=prn[0]
        #卫星所属的系统
        now_time=week*7*24.0+sec/3600.0
        #转换成小时更方便
        dt=24.0
        #最小时间差差绝对值 (小时) 初值给一个较大值
        index=-1
        #下标 初值为-1
        
        for i in range(len(self.T[prn].year)):
        #len(.)表示有几个导航电文历元需要查询->使用GPS周/GPS秒/BDS等均可
        #哪种系统似乎并不影响查询结果因为时间基准是平移关系
                obs_time=self.T[prn].Week[S][i]*7*24.0+self.T[prn].Sec[S][i]/3600.0
                if abs(obs_time-now_time)<dt:
                    dt=abs(obs_time-now_time)
                    index=i
        assert index!=-1,f'find nav index failed prn={prn} time={sec}'
        #查找失败
        return index
    
    def Calc_sate_pos_nav(self,p,I,week,sec):
    #计算卫星三维坐标
    #prn卫星编号 index导航星历第二下标(要使用哪个时刻的导航星历)
    #注意I和i要区别
        dt=sec-self.toe[p][I]
        #如果想要长时间序列解算 dt必须考虑周#********************************************************
        #dt=t_GPS_sec-nav_GPS_sec+(t_GPS_week-nav_GPS_week)*7.0*24.0*3600.0
        #dt时间差 导航星历中也有参考时刻的周和秒 toe
        n_v=sqrt(GM)/(self.sqrtA[p][I]**3)+self.dn[p][I]
        #卫星运动的平均角速度
        M=self.M0[p][I]+n_v*dt
        #平近点角
        E=M
        while(1):
            tmp=M+self.e[p][I]*sin(E)
            if(abs(tmp-E)<1e-12):
                E=tmp
                break
            E=tmp
        #偏近点角
        up=sqrt(1-self.e[p][I]**2)*sin(E)
        down=cos(E)-self.e[p][I]
        f=atan2(up,down)
        #真近点角
        u=self.w[p][I]+f
        #升交角距
        du=self.Cuc[p][I]*cos(2*u)+self.Cus[p][I]*sin(2*u)
        dr=self.Crc[p][I]*cos(2*u)+self.Crs[p][I]*sin(2*u)
        di=self.Cic[p][I]*cos(2*u)+self.Cis[p][I]*sin(2*u)
        #摄动改正项
        u=u+du
        r=(self.sqrtA[p][I]**2)*(1-self.e[p][I]*cos(E))+dr
        i=self.i0[p][I]+di+self.i_v[p][I]*dt
        #摄动改正
        x=r*cos(u)
        y=r*sin(u)
        #卫星在轨道面坐标系中的位置
        L=self.Omega[p][I]+(self.Omega_v[p][I]-w_e)*sec-self.Omega_v[p][I]*self.toe[p][I]
        #瞬间升交点的经度
        sx=x*cos(L)-y*cos(i)*sin(L)
        sy=x*sin(L)+y*cos(i)*cos(L)
        sz=y*sin(i)
        #三维坐标
        return sx,sy,sz

def test():
    
    nav=NAV('./input/brdm1840.20p')
    
    #output=open('nav_test.txt','w')
    
    prn='C01'
    
    for i in range(len(nav.T[prn].year)):
        
        print(nav.T[prn].year[i],nav.T[prn].month[i],nav.T[prn].day[i],
              nav.T[prn].hour[i],nav.T[prn].minute[i],nav.T[prn].sec[i])
    
    t=nav.T[prn].Get_timing(1,['G','C','E'])
    index=nav.find_nav_index(prn,t)
    print(index)
    
    
    '''
    output.write(str(nav.year[prn][0])+' '+str(nav.month[prn][0])+' '+str(nav.day[prn][0])+'\n')
    output.write(str(nav.hour[prn][0])+' '+str(nav.minu[prn][0])+' '+str(nav.sec[prn][0])+'\n')
    output.write(str(nav.a0[prn][0])+' '+str(nav.a1[prn][0])+' '+str(nav.a2[prn][0])+'\n')
    output.write(str(nav.Crs[prn][0])+' '+str(nav.dn[prn][0])+' '+str(nav.M0[prn][0])+'\n')
    output.write(str(nav.Cuc[prn][0])+' '+str(nav.e[prn][0])+' '+str(nav.Cus[prn][0])+' '+str(nav.sqrtA[prn][0])+'\n')
    output.write(str(nav.toe[prn][0])+' '+str(nav.Cic[prn][0])+' '+str(nav.Omega[prn][0])+' '+str(nav.Cis[prn][0])+'\n')
    output.write(str(nav.i0[prn][0])+' '+str(nav.Crc[prn][0])+' '+str(nav.w[prn][0])+' '+str(nav.Omega_v[prn][0])+'\n')
    output.write(str(nav.i_v[prn][0])+'\n')
    output.write('EOF\n')
    '''
    #输出测试 输出prn号卫星的轨道坐标 x
    '''
    ww=nav.GPS_week[prn][0]
    #print(nav.GPS_week)
    for i in range(0,24*60*60):
        ss=i+nav.GPS_sec[prn][0]
        index=nav.find_nav_index(prn,ww,ss)
        
        x,y,z=nav.Calc_sate_pos_nav(prn,index,ww,ss)
        output.write(str(i)+' '+str(x)+'\n')
    '''
    
    #print(nav.alpha,nav.beta)
    #电离层参数测试
   
if __name__=='__main__':
    
    test()
    
    print(NUM)
    