import binascii
import codecs
import re

import pdu
import serial
import push

import platform

ser = serial.Serial('/dev/cu.usbserial-1430')
# ser = serial.Serial('/dev/ttyUSB0')
# Text mode
# ser.write('AT+CMGF="1"\n'.encode())

# AT+CMGF=0
ser.write('AT+CMGF=0\n'.encode())

ser.write('AT+CSCS="UCS2"\n'.encode())

print("start read /dev/cu.usbserial-1430")
# print("start read /dev/ttyUSB0")
while 1:
    read = ser.readline()
    u_read = read.decode('utf-8')
    print("--->> " + u_read)
    match = re.match(r'\+CMTI: "ME",(\d+)', u_read)
    if match:
        u_ME_id = match.group(1)
        print("match: --->> True")
        ser.write(('AT+CMGR=' + u_ME_id + '\n').encode())
        tmp = ser.readline()
        print("tmp: --->> " + tmp.decode('utf-8'))
        info = ser.readline()
        print("info: --->> " + info.decode('utf-8'))
        msg = ser.readline()
        print(msg)

        # {'smsc': '+8613800100500', 'tpdu_length': 26, 'type': 'SMS-DELIVER', 'number': '+8615313726078',
        # 'protocol_id': 0, 'time': datetime.datetime(2021, 1, 7, 23, 24, 17, tzinfo=<pdu.SmsPduTzInfo object at 0x7fab73146550>), 'text': '你好呀'}

        result = pdu.decodeSmsPdu(msg.strip())

        # message = ('%s\n%s\n%s' % (result['text'], result['time'], result['number'])).encode('unicode-escape').decode(
        #     'utf-8')

        message = result['text'] + '\n' + str(result['time']) + '\n' + result['number']
        print(message.encode('utf-16', 'surrogatepass').decode('utf-16'))

        push.push_to(message)
        # u_msg = str(msg.strip(), 'utf-8')
        #
        # print("msg: --->> " + u_msg)
        # ser.write(('AT+CMGD=' + u_ME_id + '\n').encode())
        #
        # infomatch = re.match(r'\+CMGR: "REC.*READ","(.*)",*"(.*)"', info.decode('utf-8'))
        #
        # if infomatch:
        #     srcphone = infomatch.group(1)
        #     srctime = infomatch.group(2)
        #     srcphone = str(srcphone.decode("hex_codec"), "utf-16-be").encode("utf8")
        #
        # print("?????" + msg.decode(codecs.BOM_UTF16_BE))
        # u_msg = u_msg.strip('\r\n')
        # print("unhexlify before---> " + str(u_msg))
        # u_msg = binascii.unhexlify(u_msg)
        # print("unhexlify---> " + str(u_msg))
        # u_msg = u_msg.decode('utf-16-be')
        # print("unhexlify end ---> " + str(u_msg))

        # finalmsg = {'text': srcphone + ":" + u_msg + " [" + srctime + "]"}
        # mydata = {'value1': srcphone, 'value2': srctime, 'value3': u_msg}
        # print(mydata)
        # requests.post('IFTTT API地址', json=mydata)
