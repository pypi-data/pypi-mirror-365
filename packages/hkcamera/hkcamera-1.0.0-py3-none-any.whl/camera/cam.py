# coding=utf-8
import os
import platform
from .HCNetSDK import *
from .PlayCtrl import *
import numpy as np
import logging
import time
import cv2
from ctypes import *

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HKCam(object):
    """
    海康威视摄像头SDK接口类
    
    该类提供了与海康威视摄像头SDK的Python接口，支持实时视频流获取。
    """
    def __init__(self, camIP, username, password, devport=8000):
        """
        初始化HKCam对象
        
        Args:
            camIP (str): 摄像头IP地址
            username (str): 用户名
            password (str): 密码
            devport (int): 设备端口，默认为8000
        """
        # 登录的设备信息
        self.DEV_IP = create_string_buffer(camIP.encode())
        self.DEV_PORT = devport
        self.DEV_USER_NAME = create_string_buffer(username.encode())
        self.DEV_PASSWORD = create_string_buffer(password.encode())
        self.WINDOWS_FLAG = False if platform.system() != "Windows" else True
        self.funcRealDataCallBack_V30 = None
        self.recent_img = None # 最新帧
        self.n_stamp = None # 帧时间戳
        self.last_stamp = None # 上次时间戳
        
        # 保存原始工作目录
        original_cwd = os.getcwd()
        
        try:
            # 加载库,先加载依赖库                                                                   # 1 根据操作系统，加载对应的dll文件
            lib_dir = 'lib/win' if self.WINDOWS_FLAG else 'lib/linux'
            lib_path = os.path.join(os.path.dirname(__file__), lib_dir)
            
            if os.path.exists(lib_path):
                os.chdir(lib_path)
            
            if self.WINDOWS_FLAG:            
                self.Objdll = CDLL(os.path.join(lib_path, 'HCNetSDK.dll'))  # 加载网络库
                self.Playctrldll = CDLL(os.path.join(lib_path, 'PlayCtrl.dll'))  # 加载播放库
            else:
                self.Objdll = cdll.LoadLibrary(os.path.join(lib_path, 'libhcnetsdk.so'))
                self.Playctrldll = cdll.LoadLibrary(os.path.join(lib_path, 'libPlayCtrl.so'))
            
            # 设置组件库和SSL库加载路径                                                              # 2 设置组件库和SSL库加载路径
            self.SetSDKInitCfg(lib_path)
            # 初始化DLL
            init_result = self.Objdll.NET_DVR_Init()
            if init_result == 0:
                error_code = self.Objdll.NET_DVR_GetLastError()
                logger.error(f'SDK初始化失败 错误码: {error_code}')
                raise RuntimeError(f'SDK初始化失败 错误码: {error_code}')
            
            # 启用SDK写日志
            log_dir = os.path.join(original_cwd, 'SdkLog_Python')
            os.makedirs(log_dir, exist_ok=True)
            self.Objdll.NET_DVR_SetLogToFile(3, log_dir.encode('utf-8'), False)
            
        finally:
            # 恢复工作目录
            os.chdir(original_cwd)
        
        # 登录
        (self.lUserId, self.device_info) = self.LoginDev()                                       # 4 登录相机
        self.Playctrldll.PlayM4_ResetBuffer(self.lUserId,1) # 清空指定缓冲区的剩余数据
        
        if self.lUserId < 0: # 登录失败
            err = self.Objdll.NET_DVR_GetLastError()
            logger.error('Login device fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
            # 释放资源
            self.Objdll.NET_DVR_Cleanup()
            raise RuntimeError('摄像头登录失败')
        else:
            logger.info(f'摄像头[{camIP}]登录成功!!')
        
        self.start_play()                                                                         # 5 开始播放
        time.sleep(1)
 
    def start_play(self):
        """
        开始播放视频流
        """
        # global funcRealDataCallBack_V30                                                                        
        self.PlayCtrl_Port = c_long(-1)  # 播放句柄
        # 获取一个播放句柄 # wuzh获取未使用的通道号
        if not self.Playctrldll.PlayM4_GetPort(byref(self.PlayCtrl_Port)):
            logger.error(u'获取播放库句柄失败')
            raise RuntimeError('获取播放库句柄失败')
        
        # 定义码流回调函数       
        self.funcRealDataCallBack_V30 = REALDATACALLBACK(self.RealDataCallBack_V30)
        
        # 开启预览
        self.preview_info = NET_DVR_PREVIEWINFO()
        self.preview_info.hPlayWnd = 0
        self.preview_info.lChannel = 1  # 通道号
        # self.preview_info.dwStreamType = 0  # 主码流
        self.preview_info.dwStreamType = 1  # 副码流
        self.preview_info.dwLinkMode = 0  # TCP
        self.preview_info.bBlocked = 1  # 阻塞取流
        
        # 开始预览并且设置回调函数回调获取实时流数据
        self.lRealPlayHandle = self.Objdll.NET_DVR_RealPlay_V40(self.lUserId, byref(self.preview_info), self.funcRealDataCallBack_V30, None)
        
        if self.lRealPlayHandle < 0:
            logger.error('Open preview fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
            # 登出设备
            self.Objdll.NET_DVR_Logout(self.lUserId)
            # 释放资源
            self.Objdll.NET_DVR_Cleanup()
            raise RuntimeError('开启预览失败')
 
    def SetSDKInitCfg(self, lib_path):
        """
        设置SDK初始化依赖库路径
        
        Args:
            lib_path (str): 库文件路径
        """
        # 设置SDK初始化依赖库路径
        # 设置HCNetSDKCom组件库和SSL库加载路径
        # print(os.getcwd())
        if self.WINDOWS_FLAG:
            strPath = lib_path.encode('gbk')
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
            self.Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll'))
            self.Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'\libssl-1_1-x64.dll'))
        else:
            strPath = lib_path.encode('utf-8')
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
            self.Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'/libcrypto.so.1.1'))
            self.Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'/libssl.so.1.1'))
            
    def LoginDev(self):
        """
        登录注册设备
        
        Returns:
            tuple: (lUserId, device_info)
        """
        # 登录注册设备
        device_info = NET_DVR_DEVICEINFO_V30()
        lUserId = self.Objdll.NET_DVR_Login_V30(self.DEV_IP, self.DEV_PORT, self.DEV_USER_NAME, self.DEV_PASSWORD, byref(device_info))
        return (lUserId, device_info)
        
    def read(self):
        """
        读取最新帧
        
        Returns:
            tuple: (timestamp, image)
        """
        # 添加小延迟减少CPU占用，避免忙等待
        while self.n_stamp == self.last_stamp:
            time.sleep(0.001)
        self.last_stamp = self.n_stamp
        return self.n_stamp, self.recent_img
 
    def DecCBFun(self, nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
        """
        解码回调函数
        """
        if pFrameInfo.contents.nType == 3:
            t0 = time.time()
            # 解码返回视频YUV数据，将YUV数据转成jpg图片保存到本地
            # 如果有耗时处理，需要将解码数据拷贝到回调函数外面的其他线程里面处理，避免阻塞回调导致解码丢帧
            nWidth = pFrameInfo.contents.nWidth
            nHeight = pFrameInfo.contents.nHeight
            # nType = pFrameInfo.contents.nType
            dwFrameNum = pFrameInfo.contents.dwFrameNum
            nStamp = pFrameInfo.contents.nStamp
            # print(nWidth, nHeight, nType, dwFrameNum, nStamp, sFileName)
        try:
            YUV = np.frombuffer(pBuf[:nSize], dtype=np.uint8)
            YUV = np.reshape(YUV, [nHeight+nHeight//2, nWidth])
            img_rgb = cv2.cvtColor(YUV, cv2.COLOR_YUV2BGR_YV12)
            self.recent_img, self.n_stamp = img_rgb.copy(), nStamp
        except Exception as e:
            logger.exception(f'解码错误: {str(e)}')
            # 保留上一帧图像，避免黑屏闪烁
            if not hasattr(self, 'recent_img'):
                self.recent_img = np.zeros((480, 640, 3), dtype=np.uint8)
            # 使用上一帧的时间戳
            self.n_stamp = getattr(self, 'n_stamp', nStamp)
 
    def RealDataCallBack_V30(self, lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
        """
        码流回调函数
        """
        # print(f'收到码流数据 类型:{dwDataType} 大小:{dwBufSize}')
        # 码流回调函数
        if dwDataType == NET_DVR_SYSHEAD:
            # 设置流播放模式
            self.Playctrldll.PlayM4_SetStreamOpenMode(self.PlayCtrl_Port, 0)
            # 打开码流，送入40字节系统头数据
            if self.Playctrldll.PlayM4_OpenStream(self.PlayCtrl_Port, pBuffer, dwBufSize, 1024*1024):
                # 设置解码回调，可以返回解码后YUV视频数据
                # global FuncDecCB
                self.FuncDecCB = DECCBFUNWIN(self.DecCBFun)
                self.Playctrldll.PlayM4_SetDecCallBackExMend(self.PlayCtrl_Port, self.FuncDecCB, None, 0, None)
                # 开始解码播放
                if self.Playctrldll.PlayM4_Play(self.PlayCtrl_Port, None):
                    logger.info(u'播放库播放成功')
                else:
                    logger.error(u'播放库播放失败')
            else:
                logger.error(u'播放库打开流失败')
        elif dwDataType == NET_DVR_STREAMDATA:
            self.Playctrldll.PlayM4_InputData(self.PlayCtrl_Port, pBuffer, dwBufSize)
        else:
            logger.info(u'其他数据,长度: %d', dwBufSize)
            
            
    def release(self):
        """
        释放资源
        """
        try:
            self.Objdll.NET_DVR_StopRealPlay(self.lRealPlayHandle)
        except:
            pass
            
        if self.PlayCtrl_Port.value > -1:
            try:
                self.Playctrldll.PlayM4_Stop(self.PlayCtrl_Port)
                self.Playctrldll.PlayM4_CloseStream(self.PlayCtrl_Port)
                self.Playctrldll.PlayM4_FreePort(self.PlayCtrl_Port)
            except:
                pass
                
            try:
                self.Objdll.NET_DVR_Logout(self.lUserId)
                self.Objdll.NET_DVR_Cleanup()
            except:
                pass
        logger.info('释放资源结束')
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        
    def isOpened(self):
        """
        检查摄像头是否已成功打开
        
        Returns:
            bool: 如果摄像头已成功打开返回True，否则返回False
        """
        return self.lUserId >= 0
 
