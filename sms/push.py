# //下面的三个变量值需要修改
# var ID = "wwc367de248887ebad";
# var SECRET = "KNgBbhHiTo66VSVzqLv0vYCadXE0ndrn5o41xxxB2o4";
# var AGENTID = "1000002";
#
# //定义post方法
# function posthttp(url, data) {
#     var xhr = new XMLHttpRequest();
#     xhr.addEventListener("readystatechange", function () {
#         if (this.readyState === 4) {
#             flash(this.responseText); //显示返回消息,可删除本行
#         }
#     });
#     xhr.open("POST", url, false);
#     xhr.send(data);
#     return xhr.responseText;
# }
#
# //定义get方法
# function gethttp(url) {
#     var xhr = new XMLHttpRequest();
#     xhr.addEventListener("readystatechange", function () {
#         if (this.readyState === 4) {
#             flash(this.responseText); //显示返回消息,可删除本行
#         }
#     });
#     xhr.open("GET", url, false);
#     xhr.send();
#     return xhr.responseText;
# }
#
# //获取token
# var gettoken = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + ID + "&corpsecret=" + SECRET;
# var ACCESS_TOKEN = JSON.parse(gethttp(gettoken)).access_token;
#
# //发送消息(文本)
# var SMSRF = global('SMSRF');
# var SMSRB = global('SMSRB');
# var SMSRT = global('SMSRT');
# var SMSRD = global('SMSRD');
# var CONTENT = "发件人: " + SMSRF + "\n时间: " + SMSRT + ",  日期: " + SMSRD + "\n短信内容: " + SMSRB;
# var message = JSON.stringify({
#     "touser": "@all",
#     "msgtype": "text",
#     "agentid": AGENTID,
#     "text": {
#         "content": CONTENT
#     },
#     "safe": 0
# });
# var send = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + ACCESS_TOKEN;
# posthttp(send, message);


# https://blog.csdn.net/haijiege/article/details/86529460
# https://daliuzi.cn/tasker-forward-sms-wechat/

import json
import requests


def push_to(msg):
    secret = 'DA1WdrFoOUx5RQ5eXfDlOQv9XVw4C9vWzKyD0YoVGcc'
    qiye_id = 'ww0832e4b0cd472375'
    agent_id = '1000002'

    gettoken = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + qiye_id + "&corpsecret=" + secret

    response = requests.get(gettoken)
    get_result = json.loads(response.text)
    ACCESS_TOKEN = str(get_result['access_token'])
    print("ACCESS_TOKEN:" + ACCESS_TOKEN)

    # //发送消息(文本)
    SMSRF = 'SMSRF'
    SMSRB = 'SMSRB'
    SMSRT = 'SMSRT'
    SMSRD = 'SMSRD'
    # CONTENT = "发件人: " + SMSRF + "\n时间: " + SMSRT + ",  日期: " + SMSRD + "\n短信内容: " + SMSRB

    message = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": agent_id,
        "text": {
            "content": msg
        },
        "safe": 0
    }

    json_msg = json.dumps(message)
    print('message:' + str(json_msg))
    send = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + ACCESS_TOKEN

    post_result = requests.post(url=send, data=str(json_msg))
    print(post_result.text)


if __name__ == '__main__':
    push_to('测试')
