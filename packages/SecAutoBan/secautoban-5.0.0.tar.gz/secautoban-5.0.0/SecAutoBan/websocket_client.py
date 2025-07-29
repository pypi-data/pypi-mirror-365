import json
import time
import ipaddress
import websocket
from . import util
from multiprocessing.pool import ThreadPool

class WebSocketClient:
    init = False
    is_login = False
    sync_flag = False
    enable_cidr = False
    send_alarm_ip_list = []
    pool = ThreadPool(processes=2)
    
    def __init__(self, server_ip: str, server_port: int, sk: str, client_type: str, enable_cidr=False, block_ip=None, unblock_ip=None, get_all_block_ip=None, login_success_callback=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sk = sk
        self.enable_cidr = enable_cidr
        if client_type not in ["alarm", "block"]:
            util.print("[-] 初始化失败: 未知的模块类型" + client_type)
            return
        if client_type == "block":
            if block_ip is None or unblock_ip is None:
                util.print("[-] 初始化失败: 未实现封禁函数")
                return
            self.block_ip = block_ip
            self.unblock_ip = unblock_ip
            self.get_all_block_ip = get_all_block_ip
        self.client_type = client_type
        self.login_success_callback = login_success_callback
        self.ws = websocket.WebSocketApp(
            "ws://" + server_ip + ":" + str(server_port) + "/device",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.init =True

    def sync_block_ip(self, cidr_list):
        self.sync_flag = True
        if self.enable_cidr is False:
            cidr_list = [str(ip) for cidr in cidr_list for ip in ipaddress.ip_network(cidr).hosts()]
        util.print("[+] 同步全量封禁IP库: " + str(len(cidr_list)) + "个")
        device_all_block_ip = self.get_all_block_ip()
        for deviceIp in device_all_block_ip:
            if deviceIp not in cidr_list:
                self.unblock_ip(deviceIp)
        for cidr in cidr_list:
            if cidr not in device_all_block_ip:
                self.block_ip(cidr)
        util.print("[+] 同步全量封禁IP库完成")
        self.sync_flag = False

    def on_message(self, w, message):
        if len(message) <= 16:
            return
        message = json.loads(util.aes_cfb_decrypt(self.sk[3:].encode(), message[0:16], message[16:]).decode())
        if message["method"] == "login":
            self.is_login = True
            util.print("[+] 登录成功，设备名称: " + message["data"]["deviceName"])
            if self.login_success_callback is not None:
                self.login_success_callback()
        if self.client_type == "block":
            if message["method"] == "blockCidr":
                util.print("[+] 封禁IP: " + message["data"]["cidr"])
                if self.enable_cidr:
                    self.block_ip(message["data"]["cidr"])
                else:
                    for ip in ipaddress.ip_network(message["data"]["cidr"]).hosts():
                        self.block_ip(str(ip))
                return
            if message["method"] == "unblockCidr":
                util.print("[+] 解禁IP: " + message["data"]["cidr"])
                if self.enable_cidr:
                    self.unblock_ip(message["data"]["cidr"])
                else:
                    for ip in ipaddress.ip_network(message["data"]["cidr"]).hosts():
                        self.unblock_ip(str(ip))
                return
            if message["method"] == "sync":
                if self.get_all_block_ip is None:
                    util.print("[-] 全量封禁IP同步失败：未实现获取全部封禁IP函数，跳过本次请求")
                    return
                if self.sync_flag:
                    util.print("[-] 全量封禁IP同步失败：已有线程进行全量封禁IP库同步，跳过本次请求")
                    return
                self.pool.apply_async(self.sync_block_ip, (message["data"]["cidrList"],))
                return    

    def on_error(self, w, error):
        util.print("Error: " + str(error))
        self.ws.close()

    def on_close(self, w, code, message):
        util.print("[-] 服务器连接断开")
        self.is_login = False

    def on_open(self, w):
        util.print("[+] 连接服务器")
        key = util.random_bytes()
        iv = util.random_bytes()
        send_data = {
            "method": "login",
            "data": {
                "key": self.sk,
            }
        }
        if self.client_type == "alarm":
            send_data["data"]["type"] = "alarmDevice"
        elif self.client_type == "block":
            send_data["data"]["type"] = "blockDevice"
        self.ws.send(key + iv + util.aes_cfb_encrypt(key, iv, json.dumps(send_data).encode()))

    def web_socket_d(self):
        self.ws.run_forever(skip_utf8_validation=True)
        while True:
            util.print("[*] 5秒后自动重连")
            time.sleep(5)
            self.ws.run_forever(skip_utf8_validation=True)

    def connect(self):
        if not self.init:
            util.print("[-] 未初始化")
            return
        self.pool.apply_async(self.web_socket_d)

    def send_alarm(self, ip: str, attack_asset: str, attack_method: str):
        if self.client_type != "alarm":
            util.print("[-] 非告警模块无法发送告警数据")
            return
        if not self.is_login:
            util.print("[-] 未登录成功，无法发送数据")
            return
        if ip in self.send_alarm_ip_list:
            return
        if len(self.send_alarm_ip_list) > 20:
            self.send_alarm_ip_list.pop(0)
        self.send_alarm_ip_list.append(ip)
        send_data = {
            "method": "alarmIp",
            "data": {
                "ip": ip,
                "attackAsset": attack_asset,
                "attackMethod": attack_method
            }
        }
        iv = util.random_bytes()
        util.print("[+] 发送告警IP: " + ip + "->" + attack_asset + "\t" + attack_method)
        self.ws.send(iv + util.aes_cfb_encrypt(self.sk[3:].encode(), iv, json.dumps(send_data).encode()))
    def send_notify(self, title: str, content: str):
        if not self.is_login:
            util.print("[-] 未登录成功，无法发送数据")
            return
        send_data = {
            "method": "notify",
            "data": {
                "title": title,
                "content": content
            }
        }
        iv = util.random_bytes()
        self.ws.send(iv + util.aes_cfb_encrypt(self.sk[3:].encode(), iv, json.dumps(send_data).encode()))
    def send_sync(self):
        if self.client_type != "block":
            util.print("[-] 非封禁模块无法请求封禁IP")
            return
        if not self.is_login:
            util.print("[-] 未登录成功，无法发送数据")
            return
        send_data = {
            "method": "syncBlockIp"
        }
        iv = util.random_bytes()
        self.ws.send(iv + util.aes_cfb_encrypt(self.sk[3:].encode(), iv, json.dumps(send_data).encode()))