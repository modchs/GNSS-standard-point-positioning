# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 10:24:11 2021

@author: chs

OBS_FILE.py:读O文件 多系统:G/C

下一步优化：多系统根据使用要求来读取，不用全部输入
"""
from CONSTANT import PRN,ALL_SYS,VAR,ALL_VAR
from FUNC import XYZ2BLH
from COMMON import TIME

def str2f(s):
#字符转浮点数 因为全空格的字符无法直接使用float()函数 所以加上判断
    s=s.strip()
    #去掉空格 如果缺省 那么应该是空字符串
    if(len(s)==0):return 0.0
    else:return float(s)

class OBS:
#OBS类 包含O文件的大部分数据
    
    def __init__(self,filename='null'):
    #如果没有初始化 多次执行会导致时间序列重复 变长
        self.version='null'
        #O文件版本
        self.name='null'
        #测站名称->4位字符
        self.x0,self.y0,self.z0=0,0,0
        self.B0,self.L0=0,0
        #参考站坐标纬度经度,可以从O文件中读取: APPROX POSITION XYZ
        #self.C1C=[[] for i in range(GPS_num)]
        #self.C1C={}
        for v in ALL_VAR:
        #遍历所有频点初始化 *注意存在系统之间频点名称相同的情况如C1C
            exec('self.'+v+'={}')
            
        for s in ALL_SYS:#遍历系统
            for prn in PRN[s]:#遍历卫星                
                for v in VAR[s]:#遍历频点
                    exec('self.'+v+'[prn]=[]')
        #GPS频点段 二维数组 第一下标为卫星编号 第二下标为时序
        self.T=TIME()
        #观测文件的时间序列参数
        self.epoch_num=0
        #观测文件历元个数/读入文件遍历时更新
        if(filename=='null'):
        #不允许空的实例出现
            print('lack of OBS filename')
            return
        self.Read_obs_file(filename)
        #初始化的同时就选择O文件 合并两行命令
        
    def Read_approx_XYZ(self,data):
    #读取测站近似坐标xyz
        for line in data:
            if ('APPROX POSITION XYZ') in line:
                #近似坐标所在的行
                self.x0=float(line[1:14])
                self.y0=float(line[15:28])
                self.z0=float(line[29:42])
                break
        
        self.B0,self.L0=XYZ2BLH(self.x0,self.y0,self.z0)
        #求参考站经纬度
    def Read_name(self,data):
    #读测站名
        for line in data:
            if('MARKER NAME' in line):
                self.name=line.split()[0]
                break
                #测站名称:第一行第一个字符串/以防万一还是遍历
    def Get_begin(self,data):
    #找到表头结束位置 返回index
        for line in data:
            if ('END OF HEADER') in line:
                return data.index(line)+1
            
    def Check_type(self,line):
    #文件类型检查
        Type=line.split()[1]
        assert Type=='OBSERVATION','wrong file for OBS'
    
    def Var_init(self):
    #新历元频点初始化/此处代码运行较慢
    #为了时间对齐 默认此历元所有卫星都没有观测到 若观测到则修改最后一位 [-1]
    #默认值可以是 np.nan 也可以是0或-1
     for s in ALL_SYS:#遍历系统
        for prn in PRN[s]:#遍历卫星          
            for v in VAR[s]:#遍历频点
            #这样写好处是减少代码量 缺点是不直观 频点名没有在类中体现
                exec('self.'+v+'[prn].append(0)')
    
    def Read_obs_file(self,filename):
    #读O文件 filename:O文件名 只对rinex3+有效
        obs_file=open(filename,'r')
        data=obs_file.readlines()
        #打开O文件 每一行作为一个元素 读入字符串
        obs_file.close()
        #文件关闭
        self.version=data[0].split()[0]
        #读取版本号
        self.Check_type(data[0])
        #文件类型判断->必须是O文件
        self.Read_approx_XYZ(data)
        #读取测站近似坐标xyz
        self.Read_name(data)
        #读测站名
        obs_begin=self.Get_begin(data)
        #找到表头结束位置 下一行就是O文件数据第一行
        for i in range(obs_begin,len(data)):
        #对所有行遍历 找到历元
            
            if '>' in data[i]:
            #历元时间行 rinex3格式特点 >
                if(len(data[i].split())<6):break
                #有些O文件出现的情况 文件结尾会出现'>'但是并不是新历元
                
                self.epoch_num+=1
                #总历元数+1
                self.T.Read_Line(data[i],'O')
                #时间读入->O文件
                self.Var_init()
                #变量初始化/append
                num=int(data[i][33:36].strip())
                #num表示此历元观测到的卫星个数
                for j in range(1,num+1):
                #接下来的num行 不可能所有卫星都能包含 所以有空缺 np.nan
                #python中()左闭右开s
                    prn=data[i+j][0:3]
                    #卫星编号
                    if(prn[1]==' '):prn[1]='0'
                    #可能还有中间不是0占位的情况
                    
                    if(prn[0]=='G'):
                    #GPS
                        self.L1C[prn][-1]=str2f(data[i+j][20:35])
                        #L1C位置相同
                        #下标[-1]覆盖默认值0或np.nan
                        if(self.version=='3.02'):
                            self.C1C[prn][-1]=str2f(data[i+j][5:19])
                            self.C2W[prn][-1]=str2f(data[i+j][53:67])
                            #读取L1 数字相比C1多1位 14/15
                            #3.02版本貌似没有C1W...
                            self.L2W[prn][-1]=str2f(data[i+j][68:83])
                        elif(self.version=='3.03'):
                            self.C1C[prn][-1]=str2f(data[i+j][5:19])
                            self.C1W[prn][-1]=str2f(data[i+j][53:67])
                            self.C2W[prn][-1]=str2f(data[i+j][85:99])
                            self.L2W[prn][-1]=str2f(data[i+j][101:115])
                        elif(self.version=='3.04'):
                            self.C1C[prn][-1]=str2f(data[i+j][5:17])
                            self.C1W[prn][-1]=str2f(data[i+j][69:81])
                            self.C2W[prn][-1]=str2f(data[i+j][101:113])
                            self.L2W[prn][-1]=str2f(data[i+j][116:131])
                    
                    if(prn[0]=='C'):
                    #北斗
                        if(self.version=='3.02'):
                            self.C1I[prn][-1]=str2f(data[i+j][5:19])
                            self.C7I[prn][-1]=str2f(data[i+j][69:81])
                            #3.02版本没有C2I和C6I..
                        elif(self.version=='3.03'):
                            self.C2I[prn][-1]=str2f(data[i+j][5:19])
                            self.L2I[prn][-1]=str2f(data[i+j][20:35])
                            self.C6I[prn][-1]=str2f(data[i+j][101:115])
                            self.L6I[prn][-1]=str2f(data[i+j][116:131])
                        elif(self.version=='3.04'):
                            self.C2I[prn][-1]=str2f(data[i+j][5:17])
                            self.L2I[prn][-1]=str2f(data[i+j][20:35])
                            self.C6I[prn][-1]=str2f(data[i+j][133:145])
                            self.L6I[prn][-1]=str2f(data[i+j][148:163])
                    
                    if(prn[0]=='E'):
                    #Galileo
                        if(self.version=='3.03'):
                            self.C1C[prn][-1]=str2f(data[i+j][5:19])
        print('obs finished')
        
if __name__=="__main__":
    
    #print(ALL_SYS,PRN,NUM)
    
    obs=OBS('./input/falk1840.20o')
    #print(obs.year[-1],obs.month[-1],obs.day[-1],obs.hour[-1],obs.minu[-1],obs.sec[-1])
    #for i in PRN['C']:print(obs.C2I[i][0])
    print('obs ok')
    