# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 09:34:26 2021

@author: chs

SPP.py:标准单点定位/单文件(单天)解/单GPS
"""
import numpy as np

from CONSTANT import c
from FUNC import XYZ2ENU,ENU2POL
from COMMON import RES
from math import sqrt,sin,pi
from Troposphere import Saastamoinen
from Ionosphere import Klobuchar
from CORRECT import Earth_rot_corr,Relative_eff_corr

def Calc_all_sate(ep,obs,TAG):
#返回此历元的所有可见卫星prn
#ep历元号 obs观测文件 var为字符元组内含需要使用的频道如['C1C','L2W']
    all_sate=[]
    #本历元所有可用卫星
    for prn in TAG['PRN']:
    #只选取GPS
        flag=True
        #如果所有变量都检查过 flag依然为真 那么此历元满足要求 加入序列
        for v in TAG['var'][prn[0]]:
            if(eval('obs.'+v+'[prn][ep]==0.0')):
            #eval 字符串转换为语句
                 flag=False
                 break
        if(flag):all_sate.append(prn)
    return all_sate

def Calc_sate_pos(ep,obs,nav,res,X,TAG):
#导航星历计算卫星位置 返回三个一维数组xyz
#ep当前历元号 all_sate所有可见卫星 obs观测文件 nav导航电文文件
#rec_clk 接收机钟差 时间形式而非距离形式 接收机钟差由上次最小二乘迭代给出
    sx,sy,sz=[],[],[]
    x1,y1,z1=obs.x0,obs.y0,obs.z0
    
    for prn in res.sate[-1]:
    #确定所有卫星的坐标 考虑信号传播时间 [-1]当前最后一个 代替ep 这样可以保证spp可以从任意历元开始解算
        #time_in_space=obs.C1C[prn][ep]/
        S=prn[0]
        #系统名
        time_in_space=eval('obs.'+TAG['var'][S][0]+'[prn][ep]/c')
        #传播时间粗略值
        now_week=obs.T.Week[S][ep]
        now_sec=obs.T.Sec[S][ep]
        #obs在读入时已经计算好了GPS时
        index=nav.find_nav_index(prn,now_week,now_sec)
        #print(f'{prn}最近的导航星历下标{index}')
        #寻找最近的导航星历
        
        i=TAG['s2n'][S]
        #TAG中系统对应的序号
        #print(i,X)
        
        rec_clk=X[3+i,0]/c
        #自行选择对应系统的钟差
        
        while(1):
        #内部迭代 计算信号传播时间
        #空间传播时间 要和 接收机钟差 分离开 -> 地球自转改正需要准确的传播时间
            tx,ty,tz=nav.Calc_sate_pos_nav(prn,index,now_week,now_sec+rec_clk-time_in_space)
            #暂时先使用第一个历元的星历 减去信号传播时间
            r=sqrt((x1-tx)**2+(y1-ty)**2+(z1-tz)**2)
            tmp_t=r/c
            #计算欧氏距离和传播时间
            if(abs(tmp_t-time_in_space)<1e-14):break
            time_in_space=tmp_t
        
        tx,ty,tz=nav.Calc_sate_pos_nav(prn,index,now_week,now_sec+rec_clk-time_in_space)
        #迭代后的信号发射时刻的卫星位置
        if(TAG['earth_rot_corr']):tx,ty=Earth_rot_corr(tx,ty,time_in_space)
        #地球自转改正
        sx.append(tx)
        sy.append(ty)
        sz.append(tz)
        #第prn个卫星的坐标 加入序列
        #output_file.write(str(prn)+' '+str(tx)+' '+str(ty)+' '+str(tz)+'\n')
    
    return sx,sy,sz

def Calc_Bl(ep,obs,nav,res,X,TAG):
#列立系数矩阵 B和l
#ep 当前历元号 obs 观测文件 nav 导航电文 res 结果类实例
    all_sate=res.sate[-1]
    #所有可见卫星
    a0,a1,a2=nav.a0,nav.a1,nav.a2
    #钟差三参数
    sx=res.sx[-1]
    sy=res.sy[-1]
    sz=res.sz[-1]
    #卫星坐标
    Ele=res.Ele[-1]
    Azi=res.Azi[-1]
    #卫星高度角方位角 历元号ep基本等价于-1
    n=3+len(TAG['sys'])
    B=np.mat(np.zeros((len(all_sate),n)),dtype=float)
    l=np.mat(np.zeros((len(all_sate),1)),dtype=float)
    #B,l矩阵初始化
    
    for i in range(len(all_sate)):
    #组建法方程->每次循环构建B,l矩阵的一行
        prn=all_sate[i]
        #prn卫星编号
        S=prn[0]
        #系统字符
        j=TAG['s2n'][S]
        #TAG中系统对应的序号
        
        #tmp_C1=obs.C1C[prn][ep]
        tmp_C1=eval('obs.'+TAG['var'][S][0]+'[prn][ep]')
        #使用TAG中标记的频点 std只有一个频点
        
        r=sqrt((X[0,0]-sx[i])**2+(X[1,0]-sy[i])**2+(X[2,0]-sz[i])**2)
        #欧氏距离
        B[i,0]=(X[0,0]-sx[i])/r
        B[i,1]=(X[1,0]-sy[i])/r
        B[i,2]=(X[2,0]-sz[i])/r
        B[i,3+j]=-1
        #课本上的公式p187 接收机钟差系数为-1
        
        now_week=obs.T.Week[S][ep]
        now_sec=obs.T.Sec[S][ep]
        #同上
        index=nav.find_nav_index(prn,now_week,now_sec)
        #搜索最近的导航星历下标index
        week,sec=nav.T[prn].Week[S][index],nav.T[prn].Sec[S][index]
        #获取导航星历时刻的周秒
        dt=now_sec-sec+(now_week-week)*7*24*3600.0
        #考虑周项 不过对单天解无影响
        t_sate=a0[prn][index]+a1[prn][index]*dt+a2[prn][index]*(dt**2)
        #卫星钟差 三参数拟合 用于l矩阵
        if(TAG['relative_corr']):t_sate+=Relative_eff_corr(nav,prn,index,now_week,now_sec)
        #钟差非圆轨道改正
        if(TAG['tgd_corr']):
        #群延迟改正
            if(S=='G'):
                if(TAG['var']['G'][0]=='C1W'):
                    t_sate-=nav.TGD[prn][index]
                #不同频点改正方式不同
                elif(TAG['var']['G'][0]=='C2W'):
                    gamma=1.64694
                    t_sate-=(nav.TGD[prn][index]*gamma)
            #其他系统TGD改正暂未实现
            if(S=='C'):
                if(TAG['var']['C'][0]=='C2I'):
                    t_sate-=nav.TGD[prn][index]
                #不同频点改正方式不同
                elif(TAG['var']['C'][0]=='C6I'):
                    #??????????????????????????????????????????????????????????
                    t_sate-=nav.TGD[prn][index]
            if(S=='E'):
                if(TAG['var']['E'][0]=='C1C'):
                    t_sate-=nav.TGD[prn][index]
                #不同频点改正方式不同
            #******************************************************************
        
        if(TAG['tropo_corr']):Vtrop=Saastamoinen(Ele[i])
        else:Vtrop=0
        #对流层改正
        
        if(TAG['iono_corr']):
        #单频电离层改正
            UT=obs.T.hour[ep]+obs.T.minute[ep]/60+obs.T.sec[ep]/3600
            Vion=Klobuchar(nav.alpha,nav.beta,Ele[i],Azi[i],obs.B0,obs.L0,UT)
            #print(Vion)
        else:Vion=0
        
        l[i,0]=tmp_C1-r+(t_sate)*c-Vtrop-Vion
        #X中接收机钟差以距离形式表示 卫星钟差以时间形式表示
        
    return B,l

def Calc_Ele_Azi(ep,res):
#计算ep历元处的高度角方位角序列 实例res
    Ele_sate,Azi_sate=[],[]
    #高度角方位角序列
    for i in range(len(res.sate[-1])):
        e,n,u=XYZ2ENU(res.sx[-1][i],res.sy[-1][i],res.sz[-1][i],res.x0,res.y0,res.z0)
        Ele,Azi=ENU2POL(e,n,u)
        Ele_sate.append(Ele)
        Azi_sate.append(Azi)
    return Ele_sate,Azi_sate
    
def Calc_weight(Ele,flag='piecewise'):
#计算权阵
    diag_P=[]
    #权阵对角元素
    for i in range(len(Ele)):
        if(flag=='equal'):
            diag_P.append(1.0)
        elif(flag=='sin2'):
                diag_P.append(sin(Ele[i])**2)
        elif(flag=='piecewise'):
        #分段 >30 权为1 否则sin2
            if(Ele[i]<30*pi/180):
                diag_P.append(sin(Ele[i])**2)
            else:
                diag_P.append(1)
        #权阵和高度角有关 p=sin(Ele)^2 可以改为其他形式
    P=np.mat(np.diag(diag_P))
    return P

def Show_schedule(i,n):
#显示进度
    t=round(n/10)
    #总历元数除以10取整 -> t的整数倍对应 10整数百分比
    if(i%t==0):
            print(str(round(i/n*100))+'%')
    
def Standard_point_positioning(obs,nav,TAG):
#标准单点定位
#obs观测类 nav导航电文类 TAG标签 返回res结果类
    
    res=RES(obs)
    #res是结果类的实例 其中大部分成员都是在本函数内计算过程中更新的 更新全部通过内置函数进行
    #print(obs.epoch_num)
    #for ep in range(0,1):
    for ep in range(obs.epoch_num):
    #对每一个O文件历元单独平差解测站坐标和钟差
        
        #print('obstime:',obs.hour[ep],obs.minu[ep],obs.sec[ep])
        Show_schedule(ep,obs.epoch_num)
        #进度条
        all_sate=Calc_all_sate(ep,obs,TAG)
        res.add_sate(all_sate)
        #print(all_sate)
        #本历元所有可用卫星
        if(res.all_sate_num[-1]<4):
        #卫星数不够
            print('not enough sate (%s) at epoch %s'%({res.sate_num[-1]},ep))
            #f->{}中内容字符转变量输出
            res.add_station_xyz(np.nan,np.nan,np.nan)
            #测站坐标解不出来
            #由于无法迭代 卫星发射信号时刻的位置也无法解算
            continue
        
        n=len(TAG['sys'])+3
        X=np.mat(np.zeros((n,1)),dtype=float)
        #三个坐标+n个钟差
        X[0,0],X[1,0],X[2,0]=obs.x0,obs.y0,obs.z0
        #若xyz初值赋0 计算权阵时会报错 XYZ2BLH
        #已有近似坐标 使用近似坐标迭代 加快收敛速度 确保能够正确收敛
        #初值0,0,0->可能会出现负权的问题 负高度角?
        #参数矩阵-> X,Y,Z,钟差
        #python numpy下标引用是逗号分隔 c++是多个[]
        #下标从0开始 和matlab有区别
        res.init()
        #赋初值 卫星坐标初值/高度角等在下一循环中需要迭代的量 进入循环后马上就会被更新
        while(1):
        #迭代计算四参数
            sx,sy,sz=Calc_sate_pos(ep,obs,nav,res,X,TAG)
            res.update_sate_xyz(sx,sy,sz)
            #卫星坐标和all_sate顺序一致
            Ele_sate,Azi_sate=Calc_Ele_Azi(ep,res)
            res.update_Ele_Azi(Ele_sate,Azi_sate)
            #高度角计算更新
            P=Calc_weight(res.Ele[-1],TAG['power'])
            #构建权阵对角阵
            B,l=Calc_Bl(ep,obs,nav,res,X,TAG)
            #构建B,l系数矩阵
            dX=((B.T*P*B).I)*B.T*P*l
            X=X+dX
            if((dX[0,0]**2+dX[1,0]**2+dX[2,0]**2)<0.01):break
            #结果收敛 退出循环
        
        res.add_DOP((B.T*P*B).I)
        res.add_station_xyz(X[0,0],X[1,0],X[2,0])
        res.add_ENU()
        #添加最终测站坐标并计算ENU +DOP
        if(TAG['plot_realtime'] and ep%TAG['plot_realtime_interval']==0 and ep<obs.epoch_num-1):
        #实时绘图最后一个历元不再刷新 以控制文件的间隔实时画图
            res.Plot('enu',TAG)
            res.Plot('sate',TAG)
            
    return res
    
if __name__=="__main__":

    print("spp ok")

