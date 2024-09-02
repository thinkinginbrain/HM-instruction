
import requests
import json
import time
import hashlib
import base64
import websocket
import socket
import ssl
import threading
from pydub import AudioSegment
from pydub.playback import play
import hmac
import os
import urllib
from En2Cn import get_result
from ipdb import set_trace
import websocket
import pyaudio
import wave
import datetime
import hashlib
import base64
import hmac
from test_audi import main_fun
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from time import mktime
import _thread as thread
import os
import time
from prompt_example import get_instructions
import sys
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient
from unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.go2.sport.sport_client import (
    SportClient,
    PathPoint,
    SPORT_PATH_POINT_SIZE,
)
import math
import nltk
from scipy.io.wavfile import write
from nltk.tokenize import word_tokenize
from nltk import pos_tag, RegexpParser
import numpy as np
import speech_utils as tool
#import pyttsx3


# Recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "recorded.wav"
TTS_OUTPUT_FILENAME = "result_audio.mp3"
wsParam = 0
# API parameterstext_result= get_instructions("前进五十米再右转六十度，再前进二十米")
# print(text_result)
API_KEY = "6a7c2610ac213fd66e2217213ffef7f1"
API_SECRET = "YWUyNjliMzZhY2VjYWY1ZThhZjgyMjRh"
ASR_API_URL = "wss://iat-api.xfyun.cn/v2/iat"
TTS_API_URL = "wss://tts-api.xfyun.cn/v2/tts"
APP_ID = "d4e7815d"
lfasr_host = 'https://raasr.xfyun.cn/v2/api'
api_upload = '/upload'
api_get_result = '/getResult'




# 定义模式
patterns = {
    "停止": "停止|停下来|别动|不要|不",
    "前进": "向前|前进|往前|走前面|前",
    "后退": "向后|后退|往后|走后面|后",
    "向左": "向左|往左|走左边|左",
    "向右": "向右|往右|走右边|右",
    "右转": "转右圈|右转一圈|右旋转|右绕圈|右转",
    "左转": "转左圈|左转一圈|左旋转|左绕圈|左转",
    "坐下": "坐下|坐下来|坐着|坐下去|趴下|坐|趴",
    "站起来": "站起来|起立|站起|站起来|站",
    "伸懒腰": "伸懒腰|伸展|拉伸|舒展|懒"
}

def map_sentence_to_command(sentence):
    words = word_tokenize(sentence)
    tagged_words = pos_tag(words)

    for command, pattern in patterns.items():
        for keyword in pattern.split("|"):
            if keyword in sentence:
                return command

    return "未识别的指令"

#def tts(text='testing'):
#    engine=pyttsx3.init()
#    engine.say(text)
#    engine.runAndWait()

#robot control
class SportModeTest:
    def __init__(self) -> None:
        # Time count
        self.t = 0
        self.dt = 0.01

        # Initial poition and yaw
        self.px0 = 0
        self.py0 = 0
        self.yaw0 = 0

        self.client = SportClient()  # Create a sport client
        self.client.SetTimeout(10.0)
        self.client.Init()

        # 全局事件，用于控制函数执行
        self.execution_event = threading.Event()

        # 当前执行的函数
        self.current_function = None

    def GetInitState(self, robot_state: SportModeState_):
        self.px0 = robot_state.position[0]
        self.py0 = robot_state.position[1]
        self.yaw0 = robot_state.imu_state.rpy[2]

    def StandUpDown(self,measurement,velocity=1):
        self.client.StandDown()
        print("Stand down !!!")
        time.sleep(1)

        self.client.StandUp()
        print("Stand up !!!")
        time.sleep(1)

        self.client.StandDown()
        print("Stand down !!!")
        time.sleep(1)

        self.client.Damp()

    def VelocityMove(self,measurement,velocity=1):
        elapsed_time = 1
        for i in range(int(elapsed_time / self.dt)):
            self.client.Move(0.3, 0, 0)  # vx, vy vyaw
            time.sleep(self.dt)
        self.client.StopMove()

    def Move_forward(self,measurement,velocity=1):
        elapsed_time = measurement*4/velocity*1
        v=velocity/1*0.24
        while True:
            for i in range(int(elapsed_time / self.dt)):
                self.client.Move(v, 0, 0)  # vx, vy vyaw
                if self.execution_event.is_set():
                    break
                time.sleep(self.dt)
            self.client.StopMove()
            break

    def StopMove(self,measurement,velocity=1):
    	self.client.StopMove()

    def Move_backward(self,measurement,velocity=1):
        elapsed_time = measurement*5.5/velocity*1
        v = velocity / 1 * 0.24
        while True:
            for i in range(int(elapsed_time / self.dt)):
                self.client.Move(-v, 0, 0)  # vx, vy vyaw
                if self.execution_event.is_set():
                    break
                time.sleep(self.dt)
            self.client.StopMove()
            break

    def Move_left(self,measurement,velocity=1):
        elapsed_time = measurement*5.5/velocity*1
        v = velocity / 1 * 0.24
        while True:
            for i in range(int(elapsed_time / self.dt)):
                self.client.Move(0, v, 0)  # vx, vy vyaw
                if self.execution_event.is_set():
                    break
                time.sleep(self.dt)
            self.client.StopMove()
            break
        
    def Move_right(self,measurement,velocity=1):
        elapsed_time = measurement*5.5/velocity*1
        v = velocity / 1 * 0.24
        while True:
            for i in range(int(elapsed_time / self.dt)):
                self.client.Move(0, -v, 0)  # vx, vy vyaw
                if self.execution_event.is_set():
                    break
                time.sleep(self.dt)
            self.client.StopMove()
            break
    
    def Move_cycle_right(self,measurement,velocity=1):
        elapsed_time = (float(measurement)/90.0)*2
        # v = velocity / 5 * 1
        while True:
            for i in range(int(elapsed_time / self.dt)):
                self.client.Move(0.1, 0, -v)  # vx, vy vyaw
                if self.execution_event.is_set():
                    break
                time.sleep(self.dt)
            self.client.StopMove()
            break

    def Move_cycle_left(self,measurement,velocity=1):
        elapsed_time = (float(measurement)/90.0)*2
        # v = velocity / 5 * 1
        while True:
            for i in range(int(elapsed_time / self.dt)):
                self.client.Move(0.1, 0, v)  # vx, vy vyaw
                if self.execution_event.is_set():
                    break
                time.sleep(self.dt)
            self.client.StopMove()
            break

    def BalanceAttitude(self,measurement,velocity=1):
        self.client.Euler(0.1, 0.2, 0.3)  # roll, pitch, yaw
        self.client.BalanceStand()

    def TrajectoryFollow(self,measurement=1,velocity=1):
        time_seg = 0.2
        time_temp = self.t - time_seg
        path = []
        for i in range(SPORT_PATH_POINT_SIZE):
            time_temp += time_seg

            px_local = 0.5 * math.sin(0.5 * time_temp)
            py_local = 0
            yaw_local = 0
            vx_local = 0.25 * math.cos(0.5 * time_temp)
            vy_local = 0
            vyaw_local = 0

            path_point_tmp = PathPoint(0, 0, 0, 0, 0, 0, 0)

            path_point_tmp.timeFromStart = i * time_seg
            path_point_tmp.x = (
                px_local * math.cos(self.yaw0)
                - py_local * math.sin(self.yaw0)
                + self.px0
            )
            path_point_tmp.y = (
                px_local * math.sin(self.yaw0)
                + py_local * math.cos(self.yaw0)
                + self.py0
            )
            path_point_tmp.yaw = yaw_local + self.yaw0
            path_point_tmp.vx = vx_local * math.cos(self.yaw0) - vy_local * math.sin(
                self.yaw0
            )
            path_point_tmp.vy = vx_local * math.sin(self.yaw0) + vy_local * math.cos(
                self.yaw0
            )
            path_point_tmp.vyaw = vyaw_local

            path.append(path_point_tmp)

            self.client.TrajectoryFollow(path)
    
    def Stretch(self,measurement=1,velocity=1):
        
        self.client.Stretch()
        print("Stretch !!!")
        time.sleep(1)  
        
    def Stand(self,measurement=1,velocity=1):
        self.client.RecoveryStand()
        print("RecoveryStand !!!")
        time.sleep(1)
       
    def Sit(self,measurement=1,velocity=1):   
        self.client.StandDown()
        print("Stand down !!!")
        time.sleep(1)
       
            
    def SpecialMotions(self,measurement=1,velocity=1):
        self.client.RecoveryStand()
        print("RecoveryStand !!!")
        time.sleep(1)
        
        self.client.Stretch()
        print("Sit !!!")
        time.sleep(1)  
        
        self.client.RecoveryStand()
        print("RecoveryStand !!!")
        time.sleep(1)
 
    def execute_function(self,func,measurement=1,velocity=1):
        self.current_function = func.__name__
        func(measurement)

    def start_execution(self,func,measurement,velocity=1):
        self.execution_thread = threading.Thread(target=self.execute_function, args=(func,measurement))
        self.execution_thread.start()

    def stop_execution(self):
        if self.current_function:
            self.execution_event.set()
            self.execution_thread.join()
            self.execution_event.clear()

# 翻译的工具
class get_result(object):
    def __init__(self,host,text):
        # 应用ID（到控制台获取）
        self.APPID = "d4e7815d"
        # 接口APISercet（到控制台机器翻译服务页面获取）
        self.Secret = "YWUyNjliMzZhY2VjYWY1ZThhZjgyMjRh"
        # 接口APIKey（到控制台机器翻译服务页面获取）
        self.APIKey= "6a7c2610ac213fd66e2217213ffef7f1"

        self.APPID = "ca2af9b3"
        # 接口APISercet（到控制台机器翻译服务页面获取）
        self.Secret = "Y2IzMTc4YzU4Mjk4MDkzMTRkMWNlM2I0"
        # 接口APIKey（到控制台机器翻译服务页面获取）
        self.APIKey= "1ec414e887cae842209fe2035a862832"
        
        
        # 以下为POST请求
        self.Host = host
        self.RequestUri = "/v2/its"
        # 设置url
        # print(host)
        self.url="https://"+host+self.RequestUri
        self.HttpMethod = "POST"
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"
        self.data = 0
        # 设置当前时间
        curTime_utc = datetime.datetime.utcnow()
        self.Date = self.httpdate(curTime_utc)
        # 设置业务参数
        # 语种列表参数值请参照接口文档：https://www.xfyun.cn/doc/nlp/xftrans/API.html
        self.Text=text
        self.BusinessArgs={
                "from": "en",
                "to": "cn",
            }

    def hashlib_256(self, res):
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        result = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return result

    def httpdate(self, dt):
        """
        Return a string representation of a date according to RFC 1123
        (HTTP/1.1).

        The supplied date must be in UTC.

        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)

    def generateSignature(self, digest):
        signatureStr = "host: " + self.Host + "\n"
        signatureStr += "date: " + self.Date + "\n"
        signatureStr += self.HttpMethod + " " + self.RequestUri \
                        + " " + self.HttpProto + "\n"
        signatureStr += "digest: " + digest
        signature = hmac.new(bytes(self.Secret.encode(encoding='utf-8')),
                             bytes(signatureStr.encode(encoding='utf-8')),
                             digestmod=hashlib.sha256).digest()
        result = base64.b64encode(signature)
        return result.decode(encoding='utf-8')

    def init_header(self, data):
        digest = self.hashlib_256(data)
        #print(digest)
        sign = self.generateSignature(digest)
        authHeader = 'api_key="%s", algorithm="%s", ' \
                     'headers="host date request-line digest", ' \
                     'signature="%s"' \
                     % (self.APIKey, self.Algorithm, sign)
        #print(authHeader)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self.Date,
            "Digest": digest,
            "Authorization": authHeader
        }
        return headers

    def get_body(self):
        content = str(base64.b64encode(self.Text.encode('utf-8')), 'utf-8')
        postdata = {
            "common": {"app_id": self.APPID},
            "business": self.BusinessArgs,
            "data": {
                "text": content,
            }
        }
        body = json.dumps(postdata)
        #print(body)
        return body

    def call_url(self):
        if self.APPID == '' or self.APIKey == '' or self.Secret == '':
            print('Appid 或APIKey 或APISecret 为空！请打开demo代码，填写相关信息。')
        else:
            code = 0
            body=self.get_body()
            headers=self.init_header(body)
            #print(self.url)
            response = requests.post(self.url, data=body, headers=headers,timeout=8)
            status_code = response.status_code
            #print(response.content)
            if status_code!=200:
                # 鉴权失败
                print("Http请求失败，状态码：" + str(status_code) + "，错误信息：" + response.text)
                print("请根据错误信息检查代码，接口文档：https://www.xfyun.cn/doc/nlp/xftrans/API.html")
            else:
                # 鉴权成功
                respData = json.loads(response.text)
                self.data=respData
                # 以下仅用于调试
                code = str(respData["code"])
                if code!='0':
                    print("请前往https://www.xfyun.cn/document/error-code?code=" + code + "查询解决办法")
class get_result_CtoE(object):
    def __init__(self,host,text):
        # 应用ID（到控制台获取）
        self.APPID = "d4e7815d"
        # 接口APISercet（到控制台机器翻译服务页面获取）
        self.Secret = "YWUyNjliMzZhY2VjYWY1ZThhZjgyMjRh"
        # 接口APIKey（到控制台机器翻译服务页面获取）
        self.APIKey= "6a7c2610ac213fd66e2217213ffef7f1"

        self.APPID = "ca2af9b3"
        # 接口APISercet（到控制台机器翻译服务页面获取）
        self.Secret = "Y2IzMTc4YzU4Mjk4MDkzMTRkMWNlM2I0"
        # 接口APIKey（到控制台机器翻译服务页面获取）
        self.APIKey= "1ec414e887cae842209fe2035a862832"
        
        
        # 以下为POST请求
        self.Host = host
        self.RequestUri = "/v2/its"
        # 设置url
        # print(host)
        self.url="https://"+host+self.RequestUri
        self.HttpMethod = "POST"
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"
        self.data = 0
        # 设置当前时间
        curTime_utc = datetime.datetime.utcnow()
        self.Date = self.httpdate(curTime_utc)
        # 设置业务参数
        # 语种列表参数值请参照接口文档：https://www.xfyun.cn/doc/nlp/xftrans/API.html
        self.Text=text
        self.BusinessArgs={
                "from": "cn",
                "to": "en",
            }

    def hashlib_256(self, res):
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        result = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return result

    def httpdate(self, dt):
        """
        Return a string representation of a date according to RFC 1123
        (HTTP/1.1).

        The supplied date must be in UTC.

        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)

    def generateSignature(self, digest):
        signatureStr = "host: " + self.Host + "\n"
        signatureStr += "date: " + self.Date + "\n"
        signatureStr += self.HttpMethod + " " + self.RequestUri \
                        + " " + self.HttpProto + "\n"
        signatureStr += "digest: " + digest
        signature = hmac.new(bytes(self.Secret.encode(encoding='utf-8')),
                             bytes(signatureStr.encode(encoding='utf-8')),
                             digestmod=hashlib.sha256).digest()
        result = base64.b64encode(signature)
        return result.decode(encoding='utf-8')

    def init_header(self, data):
        digest = self.hashlib_256(data)
        #print(digest)
        sign = self.generateSignature(digest)
        authHeader = 'api_key="%s", algorithm="%s", ' \
                     'headers="host date request-line digest", ' \
                     'signature="%s"' \
                     % (self.APIKey, self.Algorithm, sign)
        #print(authHeader)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self.Date,
            "Digest": digest,
            "Authorization": authHeader
        }
        return headers

    def get_body(self):
        content = str(base64.b64encode(self.Text.encode('utf-8')), 'utf-8')
        postdata = {
            "common": {"app_id": self.APPID},
            "business": self.BusinessArgs,
            "data": {
                "text": content,
            }
        }
        body = json.dumps(postdata)
        #print(body)
        return body

    def call_url(self):
        if self.APPID == '' or self.APIKey == '' or self.Secret == '':
            print('Appid 或APIKey 或APISecret 为空！请打开demo代码，填写相关信息。')
        else:
            code = 0
            body=self.get_body()
            headers=self.init_header(body)
            #print(self.url)
            response = requests.post(self.url, data=body, headers=headers,timeout=8)
            status_code = response.status_code
            #print(response.content)
            if status_code!=200:
                # 鉴权失败
                print("Http请求失败，状态码：" + str(status_code) + "，错误信息：" + response.text)
                print("请根据错误信息检查代码，接口文档：https://www.xfyun.cn/doc/nlp/xftrans/API.html")
            else:
                # 鉴权成功
                respData = json.loads(response.text)
                self.data=respData
                # 以下仅用于调试
                code = str(respData["code"])
                if code!='0':
                    print("请前往https://www.xfyun.cn/document/error-code?code=" + code + "查询解决办法")



# Robot state
robot_state = unitree_go_msg_dds__SportModeState_()
def HighStateHandler(msg: SportModeState_):
    global robot_state
    robot_state = msg






class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # url='https://api-dx.xf-yun.com/v1/private/dts_create'
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

def on_message(ws, message):
    try:
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        print(message)
        if status == 2:
            print("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:

            with open('./demo.pcm', 'ab') as f:
                f.write(audio)

    except Exception as e:
        print("receive msg,but parse exception:", e)



# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws,A1,A2):
    print("### closed ###",A1,A2)

def play_pcm(file_path, channels=1, rate=16000, width=2):
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=p.get_format_from_width(width),
                    channels=channels,
                    rate=rate,
                    output=True)

    with open(file_path, 'rb') as pcmfile:
        data = pcmfile.read(1024)
        while data:
            stream.write(data)
            data = pcmfile.read(1024)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()
# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        print("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./demo.pcm'):
            os.remove('./demo.pcm')

    thread.start_new_thread(run, ())


def send_image_and_text(image_path, text, server_host='10.50.0.37', server_port=8050):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))

    with open(image_path, 'rb') as f:
        image_data = f.read()

    text_data = text.encode('utf-8')

    try:
        # 发送图片数据长度
        client.send(len(image_data).to_bytes(4, byteorder='big'))
        # 发送图片数据
        client.send(image_data)

        # 发送文本数据长度
        client.send(len(text_data).to_bytes(4, byteorder='big'))
        # 发送文本数据
        client.send(text_data)

        # 接收结果长度
        length_data = client.recv(4)
        if not length_data:
            print("No response from server")
            return
        length = int.from_bytes(length_data, byteorder='big')

        # 接收结果
        result_data = client.recv(length).decode('utf-8')
        return result_data

    except Exception as e:
        print(f"Error: {e}")

    client.close()
class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa

    def upload(self):
        print("Uploading file...")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            "fileSize": file_len,
            "fileName": file_name,
            "duration": "200"
        }

        data = open(upload_file_path, 'rb').read(file_len)
        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        result = json.loads(response.text)
        print("Upload response:", result)
        return result

    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'orderId': orderId,
            'resultType': "transfer,predict"
        }
        print("Fetching result...")
        status = 3
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            result = json.loads(response.text)
            status = result['content']['orderInfo']['status']
            if status == 4:
                break
            time.sleep(5)
        set_trace()
        print("Result:", result)
        return result


def record_audio(filename, duration):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def pcm_to_wav(pcm_file_path, wav_file_path):
    sample_rate = 16000  # 例如 16 kHz
    bit_depth = 16       # 例如 16-bit

    # 读取 PCM 数据
    with open(pcm_file_path, 'rb') as f:
        pcm_data = f.read()
    
    # 根据位深度将 PCM 数据转换为 numpy 数组
    dtype = np.int16 if bit_depth == 16 else np.uint8
    audio_data = np.frombuffer(pcm_data, dtype=dtype)

    # 保存为 WAV 文件
    write(wav_file_path, sample_rate, audio_data)



def play_wav_file(file_path):
    # 打开 .wav 文件
    wf = wave.open(file_path, 'rb')

    # 创建 PyAudio 流
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # 读取并播放音频数据
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # 关闭流和 PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()


def listen_and_wake():
    image_path = '/home/smbu/Desktop/temp.jpg'
    global wsParam
    
    #robot control init
    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)
        
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
    sub.Init(HighStateHandler, 10)
    time.sleep(1)

    test = SportModeTest()
    test.GetInitState(robot_state)

    print("Listening control instruction!!!")
    
    
    
    ##############################
    while True:
        play_wav_file("/media/smbu/handsome_boy/all_for_audio_8_7/all_for_audio_8_4/all_for_audio/1.wav")
        print("Listening for wake word...")
        record_audio(WAVE_OUTPUT_FILENAME, RECORD_SECONDS)
        recognized_text = main_fun(WAVE_OUTPUT_FILENAME)
        print(f"1: {recognized_text}")
        client = VideoClient()
        client.SetTimeout(3.0)
        client.Init()


        if "你好" in recognized_text:
            print("----------Wake word detected, starting recording...")
            while True:


                print("##################GetImageSample###################")
                code, data = client.GetImageSample()

                if code != 0:
                    print("get image sample error. code:", code)
                else:
                    imageName = "/home/smbu/Desktop/temp.jpg"
                imageName = "/home/smbu/Desktop/temp.jpg"
                print("ImageName:", imageName)

                with open(imageName, "+wb") as f:
                    f.write(bytes(data))

                time.sleep(1)
                play_wav_file("2.wav")
                record_audio(WAVE_OUTPUT_FILENAME, RECORD_SECONDS)
                recognized_text = main_fun(WAVE_OUTPUT_FILENAME)
              
                print(f"2: {recognized_text}")
                result_EN = send_image_and_text(image_path, recognized_text)
                print(result_EN)
                
                host = "itrans.xfyun.cn"
                gClass=get_result(host,result_EN)
                gClass.call_url()
                result_cn = gClass.data['data']['result']['trans_result']['dst']
                print(result_cn)
                
                wsParam1 = Ws_Param(APPID='3676e2d5', APISecret='MWVhMTUwZWRiZDhmNzhlNTlhNDdjOWM4',
                       APIKey='ec07d0b6e326d00e50de170f34c43346',
                       Text=result_cn)
                wsParam = wsParam1
                websocket.enableTrace(False)
                wsUrl = wsParam1.create_url()
                ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
                ws.on_open = on_open
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                play_pcm('demo.pcm')
                # Here you can add the text-to-speech and other processing as needed
                # xunfei_tts(recognized_text, TTS_OUTPUT_FILENAME)
                # audio_player(TTS_OUTPUT_FILENAME)
        
                # 我的代码在下面改的
        if "描述" in recognized_text or "看到" in recognized_text:
            print("-----Start look forward------")
            text = '描述一下图片'
            
            host = "itrans.xfyun.cn"
            gClass_CtoE = get_result_CtoE(host,text)
            gClass_CtoE.call_url()
            print(gClass_CtoE.data['data']['result']['trans_result']['dst'])
            
            result_text = gClass_CtoE.data['data']['result']['trans_result']['dst']
            
            # paizhao

            print("##################GetImageSample###################")
            code, data = client.GetImageSample()

            if code != 0:
                print("get image sample error. code:", code)
            else:
                imageName = "/home/smbu/Desktop/temp.jpg"
            imageName = "/home/smbu/Desktop/temp.jpg"
            print("ImageName:", imageName)

            with open(imageName, "+wb") as f:
                f.write(bytes(data))

            t = send_image_and_text(imageName, result_text)
            
            gClass=get_result(host,t)           # 转成汉字
            gClass.call_url()
            result_t = gClass.data['data']['result']['trans_result']['dst']
            # 语音
            wsParam2 = Ws_Param(APPID='d4e7815d', APISecret='YWUyNjliMzZhY2VjYWY1ZThhZjgyMjRh',APIKey='6a7c2610ac213fd66e2217213ffef7f1',Text=result_t)
            wsParam = wsParam2
            websocket.enableTrace(False)
            wsUrl = wsParam.create_url()
            ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
            ws.on_open = on_open
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

            # 转成 wav文件
            pcm_to_wav("demo.pcm",'output.wav')

            wav_file_path = 'output.wav'
            play_wav_file(wav_file_path)


        #=====================================================================



        # 基于规则获取指令
        # command=map_sentence_to_command(recognized_text)

        # 基于大模型获取指令
        # text_from_llm = tool.get_key_instructions(recognized_text)
        print(recognized_text)
        ############################################
        command_from_llm=get_instructions(recognized_text)
        
        command=command_from_llm['action']
        print(command)
        measurement=int(command_from_llm['degrees'])
        # command_velocity=['velocity']

        if command == "未识别的指令" or "无":
            # text_from_llm = command
            respond_text = f'未识别的指令,请重新输入指令.'
        # text_from_llm = '前进'
        else:
            respond_text = f'是要执行{command}指令吗？'
        respond_wav = tool.tts(respond_text, 'speak_by_dog.wav')

        play_wav_file(respond_wav)
        print("Listening for respond word...")
        record_audio(WAVE_OUTPUT_FILENAME, RECORD_SECONDS)
        recognized_text = main_fun(WAVE_OUTPUT_FILENAME)
        print(f"1: {recognized_text}")

        # measurement=1
        command_velocity=1
        keywords = ["是的", "对", "正确"]
        #tts(command)
        if any(keyword in recognized_text for keyword in keywords): # if 
            if command == "停止":
                print("-----Stop moving-----")
                test.stop_execution()
                test.start_execution(test.StopMove,measurement,command_velocity)
                print("-----Stop moving-----")
            if command == "前进":
                print("-----Start moving forward------")
                test.stop_execution()
                test.start_execution(test.Move_forward,measurement,command_velocity)
                print("-----Stop moving forward------")
            if command == "后退":
                print("-----Start moving backward------")
                test.stop_execution()
                test.start_execution(test.Move_backward,measurement,command_velocity)
                print("-----Stop moving backward------")
            if command == "向左":
                print("-----Start moving left------")
                test.stop_execution()
                test.start_execution(test.Move_left,measurement,command_velocity)

                # test.Move_left()
                print("-----Stop moving left------")  
            if command == "向右":
                
                print("-----Start moving right------")
                test.stop_execution()
                test.start_execution(test.Move_right,measurement,command_velocity)

                print("-----Stop moving right------")    
            if command == "右转":
                print("-----Start moving right circle------")
                test.stop_execution()
                test.start_execution(test.Move_cycle_right,measurement,command_velocity)
                print("-----Stop moving circle------")    

            if command == "左转":
                print("-----Start moving left circle------")
                test.stop_execution()
                test.start_execution(test.Move_cycle_left,measurement,command_velocity)
                print("-----Stop moving circle------")




            if command == "伸懒腰":
                print("-----Start Stretching------")
                test.Stretch()
                print("-----Stop Stretching------")


            if command == "坐下":
                print("-----Start sit------")
                test.Sit()
                print("-----Stop sit------")   
            
            if command == "站起来":
                print("-----Start stand------")
                test.Stand()
                print("-----Stop stand------")   
            
            
if __name__ == "__main__":
    listen_and_wake()

#v请重新输入指令