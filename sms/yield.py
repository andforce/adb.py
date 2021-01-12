import re

import pdu
import push
import serial

import time
import platform


# 消费者
def sms_reader():  # 生成器
    print("等待接受短信...")
    while True:
        ser, sms_index = yield  # 暂停，记录位置，返回跳出
        print("start read sms index: %s" % sms_index)
        ser.write(('AT+CMGR=%s\n' % sms_index).encode())
        time.sleep(1)
        at_cmgr_msg = ser.readline()
        print("at_cmgr_msg: --->> " + str(at_cmgr_msg))
        cmgr_info = ser.readline()
        print("cmgr_info: --->> " + str(cmgr_info))
        msg = ser.readline()
        print('pdu: ' + str(msg))

        # {'smsc': '+8613800100500', 'tpdu_length': 26, 'type': 'SMS-DELIVER', 'number': '+8615313726078',
        # 'protocol_id': 0, 'time': datetime.datetime(2021, 1, 7, 23, 24, 17,
        # tzinfo=<pdu.SmsPduTzInfo object at 0x7fab73146550>), 'text': '你好呀'}

        try:
            result = pdu.decodeSmsPdu(msg.strip())
            message = result['text'] + '\n' + str(result['time']) + '\n' + result['number']
            print('text:' + message.encode('utf-16', 'surrogatepass').decode('utf-16'))

            push.push_to(message)
            time.sleep(3)
            print("Delete Message:" + message)
            ser.write(('AT+CMGD=%s\n' % sms_index).encode())
            time.sleep(0.5)
        except Exception:
            print("收到短信，解析出错了")
            print(msg)


def want_call_number():
    print("电话消费等待中...")
    while True:
        ser = yield  # 暂停，记录位置，返回跳出
        print("有电话打进来了，开始查询点好号码...")
        ser.write('AT+CLCC\n'.encode())
        time.sleep(1)
        read = ser.readline()
        print("phone_call: " + str(read))
        match = re.match(b"\+CLCC: \d,\d,\d,\d,\d,\"(\d+)\",\d+,\".*\"\r\n", read)
        if match:
            _number = match.group(1)
            empty_line = ser.readline()
            print(empty_line)
            want_ok = ser.readline()
            if re.match(b'OK\r\n', want_ok):
                print("get call info success")
                message = _number.decode() + " 正在打你的电话。"
                print(message)
                push.push_to(message)
                time.sleep(3)
            else:
                print("get call info failed")
            print(want_ok)


def send_call_number():
    print("电话消费等待中...")
    while True:
        ser, _number = yield  # 暂停，记录位置，返回跳出
        print("电话号码得到了，准备发送...")
        print("send_call_number: " + str(_number))
        empty_line = ser.readline()
        print(empty_line)
        want_ok = ser.readline()
        if re.match(b'OK\r\n', want_ok):
            print("get call info success")
            message = _number.decode() + " 正在打你的电话。"
            print(message)
            push.push_to(message)
            time.sleep(3)
        else:
            print("get call info failed")
        print(want_ok)


def dev_serial_reader():
    dev_serial = '/dev/cu.usbserial-1430' if platform.system() == 'Darwin' else '/dev/ttyUSB0'

    ser = serial.Serial(dev_serial, rtscts=True, dsrdtr=True)

    # Text mode
    # ser.write('AT+CMGF="1"\n'.encode())

    # PDU mode
    ser.write('AT+CMGF=0\n'.encode())
    time.sleep(1)

    ser.write('AT+CSCS="UCS2"\n'.encode())
    time.sleep(1)

    print("start read: " + dev_serial)

    _sms_reader = sms_reader()  # 只是变成一个生成器
    _sms_reader.__next__()  # next 只唤醒yiedl不传递值

    _want_call_number = want_call_number()
    _want_call_number.__next__()

    _send_call_number = send_call_number()
    _send_call_number.__next__()

    while True:
        read = ser.readline()
        print('dev_serial_reader: ' + str(read))
        match = re.match(b"\+CMTI: \"ME\",(\d+)\r\n", read)
        if match:
            sms_index = match.group(1).decode()
            _sms_reader.send((ser, sms_index))

        match = re.match(b'RING\r\n', read)
        if match:
            _want_call_number.send(ser)

        match = re.match(b"\+CLCC: \d,\d,\d,\d,\d,\"(\d+)\",\d+,\".*\"\r\n", read)
        if match:
            _send_call_number.send((ser, match.group(1)))

        match = re.match(b'NO CARRIER\r\n', read)
        if match:
            print("对方挂断电话了")

        match = re.match(b"AT\+CMGR=\d+\r\r\n", read)
        if match:
            _lines = [read]
            while True:
                read = ser.readline()
                print(read)
                _lines.append(read)
                if read == b'OK\r\n':
                    print(_lines)
                    _lines.clear()
                    break
                elif read == b'ERROR\r\n':
                    _lines.clear()
                    break

        match = re.match(b"AT\+CMGD=\d+\r\r\n", read)
        if match:
            _lines = [read]
            while True:
                read = ser.readline()
                print(read)
                _lines.append(read)
                if read == b'OK\r\n':
                    print(_lines)
                    _lines.clear()
                    break
                elif read == b'ERROR\r\n':
                    _lines.clear()
                    break

        match = re.match(b"\+CMGL: \d+,\d+,.*,\d+\r\n", read)
        if match:
            """
            https://www.developershome.com/sms/cmglCommand4.asp
    
            +CMGL: index,message_status,[address_text],TPDU_length<CR><LF>SMSC_number_and_TPDU[<CR><LF>+CMGL: ...]
            message_status:
            0. It refers to the message status "received unread".
            1. It refers to the message status "received read".
            2. It refers to the message status "stored unsent".
            3. It refers to the message status "stored sent".
            """
            _lines = [read]
            while True:
                read = ser.readline()
                _lines.append(read)
                if read == b'OK\r\n':
                    print(_lines)
                    _lines.clear()
                    break
                elif read == b'ERROR\r\n':
                    _lines.clear()
                    break


dev_serial_reader()
