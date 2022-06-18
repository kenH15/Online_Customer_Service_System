# coding=utf8
# !/usr/bin/python

import struct, socket, sys
import hashlib
import threading, random
import time
import os
import requests
import shutil
from base64 import b64encode, b64decode
from app.models import *
from OnlineCustomerService.settings import SERVER_HOST, chatbot
from chatterbot import ChatBot
from app.chatbot import *
from email.mime.text import MIMEText
from django.utils import timezone
from django.db.models import Q

connectionlist = {}


# python3k 版本recv返回字节数组
def parse_recv_data(msg):
    en_bytes = b''
    cn_bytes = []
    if len(msg) < 6:
        return ''
    v = msg[1] & 0x7f
    if v == 0x7e:
        p = 4
    elif v == 0x7f:
        p = 10
    else:
        p = 2
    mask = msg[p:p + 4]
    data = msg[p + 4:]
    for k, v in enumerate(data):
        nv = chr(v ^ mask[k % 4])
        nv_bytes = nv.encode()
        nv_len = len(nv_bytes)
        if nv_len == 1:
            en_bytes += nv_bytes
        else:
            en_bytes += b'%s'
            cn_bytes.append(ord(nv_bytes.decode()))
    if len(cn_bytes) > 2:
        # 字节数组转汉字
        cn_str = ''
        clen = len(cn_bytes)
        count = int(clen / 3)
        for x in range(0, count):
            i = x * 3
            b = bytes([cn_bytes[i], cn_bytes[i + 1], cn_bytes[i + 2]])
            cn_str += b.decode()
        new = en_bytes.replace(b'%s%s%s', b'%s')
        new = new.decode()
        res = (new % tuple(list(cn_str)))
    else:
        res = en_bytes.decode()
    return res


def encode(data):
    data = str.encode(data)
    head = b'\x81'

    if len(data) < 126:
        head += struct.pack('B', len(data))
    elif len(data) <= 0xFFFF:
        head += struct.pack('!BH', 126, len(data))
    else:
        head += struct.pack('!BQ', 127, len(data))
    return head + data


def send_message(remote, message):
    conn_lists = ChatConnection.objects.filter(userIP=str(remote[0]), userPort=str(remote[1]))
    if len(conn_lists) != 0:
        for conn_list in conn_lists:
            conn = connectionlist['connection' + conn_list.staffIP + conn_list.staffPort]
            chat_data = ChatData.objects.create(staff=MyUser.objects.get(staffIP=conn_list.staffIP, staffPort=conn_list.staffPort),
                                                is_send=False,userIP=str(remote[0]), userPort=str(remote[1]), Data=message)
            chat_data.save()
            msg = '{' + str(conn_list.index) + '}' + message
            conn.send(encode(msg))
            return
    elif len(ChatConnection.objects.filter(staffIP=str(remote[0]), staffPort=str(remote[1]))) != 0:
        num_str = ""
        check_flag = 0

        if str(remote[0]) in message and 'Logout' in message:
            conn_lists = ChatConnection.objects.filter(staffIP=str(remote[0]), staffPort=str(remote[1]))
            for conn_list in conn_lists:
                try:
                    conn = connectionlist['connection' + conn_list.userIP + conn_list.userPort]
                    chat_data = ChatData.objects.create(
                        staff=MyUser.objects.get(staffIP=str(remote[0]), staffPort=str(remote[1]))
                        , userIP=conn_list.userIP, userPort=conn_list.userPort, Data=message)
                    chat_data.save()
                    msg = '{' + str(conn_list.index) + '}' + message
                    conn.send(encode(msg))
                except:
                    return
            return

        for i in range(len(message)):
                if message[check_flag] != '{':
                    conn_lists = ChatConnection.objects.filter(staffIP=str(remote[0]), staffPort=str(remote[1]))
                    break
                elif message[i] == '{':
                    num_str = ""
                elif message[i] == '}':
                    conn_lists = ChatConnection.objects.filter(staffIP=str(remote[0]), staffPort=str(remote[1])
                                                               , index=int(num_str))
                    print(num_str)
                    break
                else:
                    num_str += message[i]

        for conn_list in conn_lists:
            try:
                conn = connectionlist['connection' + conn_list.userIP + conn_list.userPort]
                chat_data = ChatData.objects.create(staff=MyUser.objects.get(staffIP=str(remote[0]), staffPort=str(remote[1]))
                                     , userIP=conn_list.userIP, userPort=conn_list.userPort, Data=message)
                chat_data.save()
                msg = '{' + str(conn_list.index) + '}' + message
                conn.send(encode(msg))
            except:
                return
        return
    else:
        if len(MyUser.objects.filter(staffIP=str(remote[0]), staffPort=str(remote[1]))) != 0:
            return

        conn = connectionlist['connection' + str(remote[0]) + str(remote[1])]

        company_code = '00000'
        if message[:22] == 'asdasdasdasvmvjvjnjvsd':
            if len(MyUser.objects.filter(staffIP=str(remote[0]), staffPort=str(remote[1]))) != 0:
                return
            company_code = message[22:]
            conn.send(encode(str('您好！很高兴为您服务~')))
            responses = chatterbot_order(chatbot[company_code], company_code)
            if len(responses) > 0:
                html = '<p>你是否想了解以下热门问题</p>'
                for title, text in responses:
                    html += '<p><a onclick="send_question(' + "'" + text + "'" + ')">' + str(title) + '</a></p>'
                conn.send(encode(html))
            return

        new_message = ""
        check_flag = 0
        if message[check_flag] == '{':
            while message[check_flag] != '}':
                check_flag += 1
            check_flag += 1

        while True:
            if check_flag == len(message):
                break
            else:
                new_message += message[check_flag]
            check_flag += 1

        message = new_message
        tt = chatterbot_get_response(chatbot[company_code], message)
        conn.send(encode(str(tt)))
        return


def delete_connection(remote):
    global connectionlist
    del connectionlist['connection' + str(remote[0]) + str(remote[1])]


class WebSocket(threading.Thread):
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, conn, index, name, remote, code='00000', path="/"):
        threading.Thread.__init__(self)
        self.conn = conn
        self.index = index
        self.name = name
        self.remote = remote
        self.path = path
        self.buffer = ""
        self.company_code = code

    def run(self):
        print('Socket%s Start!' % self.index)
        headers = {}
        self.handshaken = False

        while True:
            if self.handshaken == False:
                print('Socket%s Start Handshaken with %s!' % (self.index, self.remote))
                self.buffer += bytes.decode(self.conn.recv(1024))

                if self.buffer.find('\r\n\r\n') != -1:
                    header, data = self.buffer.split('\r\n\r\n', 1)
                    for line in header.split("\r\n")[1:]:
                        key, value = line.split(": ", 1)
                        headers[key] = value

                    headers["Location"] = ("ws://%s%s" % (headers["Host"], self.path))
                    key = headers['Sec-WebSocket-Key']
                    token = b64encode(hashlib.sha1(str.encode(str(key + self.GUID))).digest())

                    handshake = "HTTP/1.1 101 Switching Protocols\r\n" \
                                "Upgrade: websocket\r\n" \
                                "Connection: Upgrade\r\n" \
                                "Sec-WebSocket-Accept: " + bytes.decode(token) + "\r\n" \
                                                                                 "WebSocket-Origin: " + str(
                        headers["Origin"]) + "\r\n" \
                                             "WebSocket-Location: " + str(headers["Location"]) + "\r\n\r\n"

                    self.conn.send(str.encode(str(handshake)))
                    self.handshaken = True
                    print('Socket%s Handshaken with %s success!' % (self.index, self.remote))
                    send_message(self.remote, 'asdasdasdasvmvjvjnjvsd' + self.company_code)

            else:
                msg = parse_recv_data(self.conn.recv(1024))
                if msg == 'quit':
                    print('Socket%s Logout!' % (self.index))
                    send_message(self.remote, self.name + ' Logout')
                    delete_connection(self.remote)
                    delete_chat_connection(str(self.remote[0]), str(self.remote[1]))
                    self.conn.close()
                    break
                elif '*create image data*' in msg:
                    check_index = ''
                    if msg[0] == '{':
                        for i in range(len(msg)):
                            if msg[i] == '}':
                                break
                            elif msg[i] == '{':
                                check_index = ''
                            else:
                                check_index += msg[i]
                        new_image_data = ImageData.objects.create(user_IP=str(self.remote[0]), user_port=str(self.remote[1])
                                                              , chat_index=int(check_index))
                        new_image_data.save()
                    else:
                        new_image_data = ImageData.objects.create(user_IP=str(self.remote[0]),
                                                                  user_port=str(self.remote[1]))
                        new_image_data.save()
                elif msg == '*connect_staff*':

                    if len(ChatConnection.objects.filter(userIP=str(self.remote[0]),userPort=str(self.remote[1]))) != 0:
                        msg = '您已经在跟客服人员对话中'
                        conn = connectionlist['connection' + str(self.remote[0]) + str(self.remote[1])]
                        conn.send(encode(msg))
                        continue

                    staff = arrange_staff(self.company_code)
                    if staff != None:
                        for n in range(staff.process_num + 1):
                            print(n)
                            if n == 0:
                                continue
                            else:
                                if len(ChatConnection.objects.filter(staff=staff, index=n, staffIP=staff.staffIP
                                        , staffPort=staff.staffPort)) == 0:
                                    newConnection = ChatConnection(staff=staff, userIP=str(self.remote[0])
                                                                   , userPort=str(self.remote[1]),
                                                                   staffName=staff.username, staffIP=staff.staffIP
                                                                   , staffPort=staff.staffPort, index=n)
                                    newConnection.save()

                                    msg = "连接成功/IP=" + str(staff.staffIP) + '/Nickname=' + str(
                                        staff.nickname) + '/image=' + staff.get_image_url()
                                    conn = connectionlist['connection' + str(self.remote[0]) + str(self.remote[1])]
                                    conn.send(encode(msg))

                                    msg2 = '{' + str(newConnection.index) + '}' + "连接成功/IP=" + str(self.remote[0])
                                    conn2 = connectionlist[
                                        'connection' + str(newConnection.staffIP) + str(newConnection.staffPort)]
                                    conn2.send(encode(msg2))
                                    break
                    else:
                        msg = '没有等待的客服人员'
                        conn = connectionlist['connection' + str(self.remote[0]) + str(self.remote[1])]
                        conn.send(encode(msg))

                elif msg != '':
                    print('Socket%s Got msg:%s from %s!' % (self.index, msg, self.remote))
                    send_message(self.remote, msg)

            self.buffer = ""


class WebSocketServer(threading.Thread):
    def __init__(self, code='00000'):
        threading.Thread.__init__(self)
        self.socket = None
        self.company_code = code

        if code not in chatbot:
            chatbot[code] = ChatBot(
                'chatbot',
                database=self.company_code,
                read_only=True
            )

    def run(self):
        print('WebSocketServer Start!')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER_HOST, int(self.company_code)))
        self.socket.listen(3000)

        global connectionlist

        i = 0
        while True:
            connection, address = self.socket.accept()

            username = address[0]
            newSocket = WebSocket(connection, i, username, address, self.company_code)
            newSocket.start()
            connectionlist['connection' + str(address[0]) + str(address[1])] = connection
            i = i + 1

            staffs = MyUser.objects.filter(~Q(status=0), is_admin=False, is_company=False, staffIP=str(address[0])
                                           , staffPort='0')
            if len(staffs) != 0:
                for staff in staffs:
                    if staff.staffPort == '0':
                        staff.staffPort = address[1]
                        staff.save()
                continue


def arrange_staff(company_code):
    #connect user with staff
    staffs = MyUser.objects.filter(is_admin=False, is_company=False, company_code=company_code).order_by(
        'chatting_score')
    for my_staff in staffs:
        if my_staff.status == 1 or my_staff.status == 2:
            # choose this one
            my_staff.cur_process += 1
            if my_staff.cur_process > 0 and my_staff.cur_process < my_staff.process_num:
                my_staff.status = 2
            elif my_staff.cur_process == my_staff.process_num:
                my_staff.status = 3
            my_staff.save()
            return my_staff

    #no staff can go to work
    #please wait
    print('please wait')
    return None


def delete_chat_connection(IP, PORT):
    st_ip = None
    st_port = None
    delete_num = 0

    if MyUser.objects.filter(staffIP=IP, staffPort=PORT):
        if os.path.exists('app/static/staff_image/' + IP):
            shutil.rmtree('app/static/staff_image/' + IP)
            os.mkdir('app/static/staff_image/' + IP)
    else:
        if os.path.exists('app/static/user_image/' + IP):
            shutil.rmtree('app/static/user_image/' + IP)
            os.mkdir('app/static/user_image/' + IP)

    conns = ChatConnection.objects.filter(userIP=IP, userPort=PORT)
    if len(conns) != 0:
        for conn in conns:
            st_ip = conn.staffIP
            st_port = conn.staffPort
            delete_num += 1
            # 计算并保存聊天时间
            conn.endTime = timezone.now()
            staff = MyUser.objects.get(staffIP=conn.staffIP, staffPort=conn.staffPort)
            conn_start_time = conn.startTime
            conn_end_time = conn.endTime
            staff.chatting_time += int((conn_end_time - conn_start_time).seconds) # 服务器异常结束时会有出现BUG
            staff.save()
            data = ChatRecord.objects.create(staff=staff, user_IP=conn.userIP, user_Port=conn.userPort, start_time= conn_start_time, end_time= conn_end_time)
            data.chatting_time = str(int((data.end_time - data.start_time).seconds / 60)) + "' " + str(
                (data.end_time - data.start_time).seconds % 60) + "''"
            user_add = ''
            address = check_ip(data.user_IP)
            for add in address:
                if add not in user_add:
                    if len(user_add) > 0:
                        user_add += ' '
                    user_add += add
            data.address = user_add
            data.save()
            break
        conns.delete()
    elif len(ChatConnection.objects.filter(staffIP=IP, staffPort=PORT)) != 0:
        conns = ChatConnection.objects.filter(staffIP=IP, staffPort=PORT)
        for conn in conns:
            st_ip = conn.staffIP
            st_port = conn.staffPort
            delete_num += 1
            # 计算并保存聊天时间
            conn.endTime = timezone.now()
            staff = MyUser.objects.get(staffIP=conn.staffIP, staffPort=conn.staffPort)
            conn_start_time = conn.startTime
            conn_end_time = conn.endTime
            staff.chatting_time += int((conn_end_time - conn_start_time).seconds)  # 服务器异常结束时会有出现BUG
            staff.save()
            data = ChatRecord.objects.create(staff=staff, user_IP=conn.userIP, user_Port=conn.userPort,
                                             start_time=conn_start_time, end_time=conn_end_time)
            data.chatting_time = str(int((data.end_time - data.start_time).seconds / 60)) + "' " + str(
                (data.end_time - data.start_time).seconds % 60) + "''"
            user_add = ''
            address = check_ip(data.user_IP)
            for add in address:
                if add not in user_add:
                    if len(user_add) > 0:
                        user_add += ' '
                    user_add += add
            data.address = user_add
            data.save()
            conn.delete()
    else:
        if len(MyUser.objects.filter(is_admin=False, is_company=False, staffIP=IP, staffPort=PORT)) != 0:
            staff = MyUser.objects.filter(is_admin=False, is_company=False, staffIP=IP, staffPort=PORT)
            for st in staff:
                st.cur_process = 0
                st.save()
        print('There is no connection. Can not delete chat connection. ')
        return

    staff = MyUser.objects.get(is_admin=False, is_company=False, staffIP=st_ip, staffPort=st_port)
    staff.cur_process -= delete_num
    if staff.cur_process == 0:
        staff.status = 1
    elif staff.cur_process > 0 and staff.cur_process < staff.process_num:
        staff.status = 2
    staff.save()
    # 计算平均对话时间并给客服人员分数
    staffs = MyUser.objects.filter(is_admin=False, is_company=False, company_code=staff.company_code)
    if len(staffs) == 0:
        return
    average_time = 0
    chatting_num = 0
    for my_staff in staffs:
        chatting_num += my_staff.chatting_num
        average_time += my_staff.chatting_time
    if chatting_num == 0:
        return
    average_time /= float(chatting_num)
    for my_staff in staffs:
        my_staff.chatting_score = float(my_staff.chatting_time)
        my_staff.chatting_score /= average_time
        my_staff.save()


def check_ip(user_IP):
    IP = {'ip': user_IP}
    URL = 'http://ip.taobao.com/service/getIpInfo.php'
    address = []
    try:
        r = requests.get(URL, params=IP, timeout=10)
    except requests.RequestException as e:
        return address
    else:
        json_data = r.json()
        if json_data[u'code'] == 0:
            if len(str(json_data[u'data'][u'country'])) > 0:
                address.append(str(json_data[u'data'][u'country']))
            if len(str(json_data[u'data'][u'area'])) > 0:
                address.append(str(json_data[u'data'][u'area']))
            if len(str(json_data[u'data'][u'region'])) > 0:
                address.append(str(json_data[u'data'][u'region']))
            if len(str(json_data[u'data'][u'city'])) > 0:
                address.append(str(json_data[u'data'][u'city']))
        return address