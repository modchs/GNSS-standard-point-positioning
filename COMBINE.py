# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 11:46:25 2021

@author: chs
COMBINE.py:观测值组合单点定位：无电离层组合
"""
import numpy as np

from math import sqrt
from COMMON import RES
from CONSTANT import c,freq
from Troposphere import Saastamoinen
from Ionosphere import Klobuchar
from CORRECT import Earth_rot_corr,Relative_eff_corr
from SPP import Calc_all_sate,Calc_sate_pos,Calc_weight,Calc_Ele_Azi,Show_schedule

def Calc_sate_pos_2(ep,obs,nav,sp3,clk,res,rec_clk,TAG):
#精密星历计算卫星位置
#ep 当前历元号 all_sate 所有可见卫星 obs 观测文件 nav 导航电文文件
    all_sate=res.sate[ep]
    
    if(ep<=2 or obs.GPS_sec[ep]>=sp3.GPS_sec[-1]):
    #最后15min 无法内插 改用广播星历
    #前几个历元由于传播时间的原因 可能也内插不了
        #print('sp3 not available @COMBIN.py')
        tmp1,tmp2,tmp3=Calc_sate_pos(ep,obs,nav,res,rec_clk,TAG)
        return tmp1,tmp2,tmp3
    
    sx,sy,sz=[],[],[]
    x1,y1,z1=obs.x0,obs.y0,obs.z0
    
    for prn in all_sate:
    #确定所有卫星的坐标 考虑信号传播时间
        S=prn[0]
        #多系统
        time_in_space=eval('obs.'+TAG['var'][S][0]+'[prn][ep]/c')
        #传播时间粗略值
        now_sec=obs.T.Sec[S][ep]
        #obs在读入时已经计算好了GPS时
        
        while(1):
        #内部迭代 计算信号传播时间 有吸收作用
            tx,ty,tz=sp3.Calc_sate_pos_sp3(prn,now_sec+rec_clk-time_in_space)
            #显然要想考虑长时间序列解算 必须考虑周项**************************************
            #暂时先使用第一个历元的星历 减去信号传播时间
            r=sqrt((x1-tx)**2+(y1-ty)**2+(z1-tz)**2)
            tmp_t=r/c
            #计算欧氏距离 和 传播时间
            if(abs(tmp_t-time_in_space)<1e-14):
                break
            
            time_in_space=tmp_t
        
        tx,ty,tz=sp3.Calc_sate_pos_sp3(prn,now_sec+rec_clk-time_in_space)
        #迭代后的信号发射时刻的卫星位置
        
        if(TAG['earth_rot_corr']):
            tx,ty=Earth_rot_corr(tx,ty,time_in_space)
        #地球自转改正 课本p129
        
        sx.append(tx)
        sy.append(ty)
        sz.append(tz)
        #第prn个卫星的坐标
        #output_file.write(str(prn)+' '+str(tmp_x)+' '+str(tmp_y)+' '+str(tmp_z)+'\n')
    
    return sx,sy,sz

def Calc_Bl_2(ep,obs,nav,clk,res,X,TAG):
#列立系数矩阵 B和l 无电离层组合
#ep 当前历元号 all_sate 所有可见卫星 obs 观测文件 nav 导航电文
    
    all_sate=res.sate[-1]
    #可见卫星
    sx,sy,sz=res.sx[-1],res.sy[-1],res.sz[-1]
    #卫星坐标
    B=np.mat(np.zeros((len(all_sate),4)),dtype=float)
    l=np.mat(np.zeros((len(all_sate),1)),dtype=float)
    #B,l矩阵初始化
    Ele,Azi=res.Ele[-1],res.Azi[-1]
    #高度角方位角
    v1=TAG['var'][0]
    if(len(TAG['combination'])>1):v2=TAG['var'][1]
    #使用的频点名
    
    n=freq[v1]**2/(freq[v1]**2-freq[v2]**2)
    
    for i in range(len(all_sate)):
    #组建法方程:每次循环构建B矩阵的一行
        prn=all_sate[i]
        #卫星号
        tmpC=eval('obs.'+v1+'[prn][ep]')
        
        r=sqrt((X[0,0]-sx[i])**2+(X[1,0]-sy[i])**2+(X[2,0]-sz[i])**2)
        
        B[i,0]=(X[0,0]-sx[i])/r
        B[i,1]=(X[1,0]-sy[i])/r
        B[i,2]=(X[2,0]-sz[i])/r
        B[i,3]=-1
        
        new_GPS_week=obs.GPS_week[ep]
        new_GPS_sec=obs.GPS_sec[ep]

        if(TAG['eph']=='sp3' and new_GPS_sec<=clk.GPS_sec[-1]):
        #使用精密钟差
            t_sate=clk.Calc_t(prn,new_GPS_sec)
            
        else:
        #使用导航星历
            index=nav.find_nav_index(prn,new_GPS_week,new_GPS_sec)
            #搜索最近的导航星历下标index
            week,sec=nav.GPS_week[prn][index],nav.GPS_sec[prn][index]
            #获取导航星历时刻的GPS时
            dt=new_GPS_sec-sec+(new_GPS_week-week)*7*24*3600.0
            #考虑GPS周项 不过对单天解无影响
            t_sate=nav.a0[prn][index]+nav.a1[prn][index]*dt+nav.a2[prn][index]*(dt**2)
            #卫星钟差 三参数拟合 用于l矩阵
            if(TAG['relative_corr']):
            #钟差非圆轨道改正
                t_sate+=Relative_eff_corr(nav,prn,index,week,sec)
        
        if(TAG['tropo_corr']):Vtrop=Saastamoinen(Ele[i])
        else:Vtrop=0
        #对流层改正
        
        if(TAG['iono_corr']):
        #电离层改正
            if(TAG['combination']=='std'):
            #单频电离层改正
                UT=obs.hour[ep]+obs.minu[ep]/60+obs.sec[ep]/3600
                Vion=Klobuchar(nav.alpha,nav.beta,Ele[i],Azi[i],obs.B0,obs.L0,UT)
                #print(Vion)
            elif(TAG['combination']=='ionofree'):
            #双频电离层改正
                dr=obs.C1W[prn][ep]-obs.C2W[prn][ep]
                Vion=-n*dr
        else:Vion=0
        
        l[i,0]=tmpC-r+t_sate*c-Vtrop-Vion
        #X中接收机钟差以距离形式表示 卫星钟差以时间形式表示
        
    return B,l

def Single_point_positioning(obs,nav,sp3,clk,TAG):
#单点定位 输入:一个观测类和一个导航电文类
    
    res=RES(obs)
    #res 结果类
    for ep in range(obs.epoch_num):
    #对每一个历元单独平差解坐标和钟差
        Show_schedule(ep,obs.epoch_num)
        #进度条
        all_sate=Calc_all_sate(ep,obs,var=TAG['var'])
        res.add_sate(all_sate)
        #本历元所有可用卫星
        if(res.sate_num[-1]<4):
        #卫星数不够
            print(f'not enough sate at epoch {ep}')
            #f->{}中内容字符转变量输出
            res.add_station_xyz(np.nan,np.nan,np.nan)
            #测站坐标解不出来
            #由于无法迭代 卫星发射信号时刻的位置也无法解算
            continue
        
        X=np.mat([obs.x0,obs.y0,obs.z0,0],dtype=float)
        #若xyz初值赋0 计算权阵时会报错 XYZ2BLH
        X=X.T
        #参数矩阵-> X,Y,Z,钟差
        #python numpy下标引用是逗号分隔 c++是多个[]
        #下标从0开始 和matlab有区别
        res.init()
        #卫星坐标初值/高度角等在下一循环中需要迭代的量 进入循环后马上就会被更新
        while(1):
        #迭代计算四参数
            if(TAG['eph']=='nav'):
                sx,sy,sz=Calc_sate_pos(ep,obs,nav,res,X[3,0]/c,TAG)
            elif(TAG['eph']=='sp3'):
                sx,sy,sz=Calc_sate_pos_2(ep,obs,nav,sp3,clk,res,X[3,0]/c,TAG)
            res.update_sate_xyz(sx,sy,sz)
            #卫星坐标和all_sate顺序一致
            Ele_sate,Azi_sate=Calc_Ele_Azi(ep,res)
            res.update_Ele_Azi(Ele_sate,Azi_sate)
            #高度角计算更新
            P=Calc_weight(res.Ele[ep],TAG['power'])
            #构建权阵对角阵
            B,l=Calc_Bl_2(ep,obs,nav,clk,res,X,TAG)
            #构建B,l系数矩阵
            #选择组合方式
            dX=((B.T*P*B).I)*B.T*P*l
            X=X+dX
            
            if((dX[0,0]**2+dX[1,0]**2+dX[2,0]**2)<0.01):break
        
        res.add_station_xyz(X[0,0],X[1,0],X[2,0])
        res.add_ENU()
        #添加最终测站坐标
        if(TAG['plot_realtime']):res.Plot('enu',TAG)
        #实时绘图
    return res

if __name__=="__main__":
    
    print("combine ok")

