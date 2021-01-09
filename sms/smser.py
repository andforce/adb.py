import re

import pdu
import push
import serial

import time

# https://wenku.baidu.com/view/74c49356ad02de80d4d84091.html
# https://blog.csdn.net/hbk320/article/details/50145373/

# ser = serial.Serial('/dev/cu.usbserial-1420')
# ser = serial.Serial('/dev/cu.usbserial-1420', rtscts=True, dsrdtr=True)
ser = serial.Serial('/dev/ttyUSB0', rtscts=True, dsrdtr=True)
# Text mode
# ser.write('AT+CMGF="1"\n'.encode())

# AT+CMGF=0
ser.write('AT+CMGF=0\n'.encode())
time.sleep(1)

ser.write('AT+CSCS="UCS2"\n'.encode())
time.sleep(1)

print("start read /dev/cu.usbserial-1420")
# print("start read /dev/ttyUSB0")
while 1:
    read = ser.readline()
    # print(read)
    print(str(read))
    match = re.match(b"\+CMTI: \"ME\",(\d+)\r\n", read)
    if match:
        sms_index = match.group(1).decode()
        print("match: receive index: " + sms_index)
        ser.write(('AT+CMGR=%s\n' % sms_index).encode())
        time.sleep(1)
        tmp = ser.readline()
        print("tmp: --->> " + str(tmp))
        info = ser.readline()
        print("info: --->> " + str(info))
        msg = ser.readline()
        print('CONTENT, pdu:' + str(msg))

        # {'smsc': '+8613800100500', 'tpdu_length': 26, 'type': 'SMS-DELIVER', 'number': '+8615313726078',
        # 'protocol_id': 0, 'time': datetime.datetime(2021, 1, 7, 23, 24, 17,
        # tzinfo=<pdu.SmsPduTzInfo object at 0x7fab73146550>), 'text': '你好呀'}

        try:
            result = pdu.decodeSmsPdu(msg.strip())
            message = result['text'] + '\n' + str(result['time']) + '\n' + result['number']
            print('CONTENT, text:' + message.encode('utf-16', 'surrogatepass').decode('utf-16'))

            push.push_to(message)
            time.sleep(3)
            print("Delete Message:" + message)
            ser.write(('AT+CMGD=%s\n' % sms_index).encode())
            time.sleep(0.5)
        except Exception:
            print("收到短信，解析出错了")
            print(msg)
        continue

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
        print("CMGL List SMS")
        continue

    match = re.match(b"AT\+CMGD=\d+\r\r\n", read)
    if match:
        read = ser.readline()
        print(read)
        if re.match(b'OK\r\n', read):
            print("delete sms, success")
        else:
            print("delete sms, failed")
        continue

    match = re.match(b"AT\+CMGR=(\d+)\r\r\n", read)
    if match:
        read = ser.readline()
        print(read)
        match = re.match(b"\+CMGR: \d+,.*,\d+\r\n", read)
        if match:
            content = ser.readline()
            try:
                result = pdu.decodeSmsPdu(content.strip())
                message = result['text'] + '\n' + str(result['time']) + '\n' + result['number']
                print('>>>>> >>>>>>')
                print('CONTENT, text:' + message.encode('utf-16', 'surrogatepass').decode('utf-16'))
                print('<<<<< <<<<<<')
                empty_line = ser.readline()
                print(empty_line)
                want_ok = ser.readline()
                if re.match(b'OK\r\n', want_ok):
                    print("read success")
                else:
                    print("read failed")
                print(want_ok)
            except Exception:
                print("解析又出错了")
                print(content)
        continue
    match = re.match(b'RING\r\n', read)
    if match:
        print("RIMG")
        ser.write('AT+CLCC\n'.encode())
        time.sleep(1)
        continue

    match = re.match(b'NO CARRIER\r\n', read)
    if match:
        print("NO CARRIER")
        continue

    match = re.match(b'AT\+CLCC\r\r\n', read)
    if match:
        print("有电话打进来了")
        read = ser.readline()
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
        continue
