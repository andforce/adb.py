import sys
import re
import math

fblack = "30"
fred = "31"
fgreen = "32"
fyellow = "33"
fblue = "34"
fpurple = "35"
fcyan = "36"
fwhite = "97"
fdefault = "39"

bblack = "40"
bred = "41"
bgreen = "42"
byellow = "43"
bblue = "44"
bpurple = "45"
bcyan = "46"
bwhite = "47"
bdefault = "49"


def _color_log(color, msg):
    return "\033[0;%sm%s\033[0m" % (color, msg)


log_V = r'(^(\d+-\d+ \d+:\d+:\d+.\d+)) +(\d+) +(\d+) +(V) +(.*?)\n'
log_D = r'(^(\d+-\d+ \d+:\d+:\d+.\d+)) +(\d+) +(\d+) +(D) +(.*?)\n'
log_I = r'(^(\d+-\d+ \d+:\d+:\d+.\d+)) +(\d+) +(\d+) +(I) +(.*?)\n'
log_W = r'(^(\d+-\d+ \d+:\d+:\d+.\d+)) +(\d+) +(\d+) +(W) +(.*?)\n'
log_E = r'(^(\d+-\d+ \d+:\d+:\d+.\d+)) +(\d+) +(\d+) +(E) +(.*?)\n'


def cut_long_msg(msg):
    length = 150
    list_of_strings = []
    r = list(range(0, len(msg), length))
    if len(r) == 1:
        list_of_strings.append(msg)
    else:
        for i in r:
            if i == 0:
                list_of_strings.append(msg[i:length + i] + '↩')
            elif i == (len(r) - 1):
                list_of_strings.append('↪' + msg[i:length + i])
            else:
                list_of_strings.append('↪' + msg[i:length + i] + '↩')

    return list_of_strings
    # print(list_of_strings)


def color_log(time, pid, tid, level, tag, msg):
    # print("------>>>>>> " + time + " " + pid + " " + tid + " " + level + " " + tag + " " + msg)

    list_result = []
    list_msg = cut_long_msg(msg)
    i = 0
    for msg_lig in list_msg:
        i = i + 1
        if level == 'V':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag.replace("%", "%%"))
            part2 = msg_lig
        elif level == 'D':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag.replace("%", "%%"))
            part2 = _color_log(fblue, msg_lig.replace("%", "%%"))
        elif level == 'I':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag.replace("%", "%%"))
            part2 = _color_log(fgreen, msg_lig.replace("%", "%%"))
        elif level == 'W':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag.replace("%", "%%"))
            part2 = _color_log(fyellow, msg_lig.replace("%", "%%"))
        elif level == 'E':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag.replace("%", "%%"))
            part2 = _color_log(fred, msg_lig.replace("%", "%%"))
        else:
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag.replace("%", "%%"))
            part2 = msg_lig

        if i == 1:
            list_result.append(part1 + part2 + "\n")
        else:
            list_result.append("".ljust(len(part1)) + part2 + "\n")
    return list_result

    # if level == 'V':
    #     return time + " " + pid + " " + tid + " " + level + " " + tag + " " + msg
    # elif level == 'D':
    #     return time + " " + pid + " " + tid + " " + level + " " + tag + " " + _color_log(fblue, msg)
    # elif level == 'I':
    #     return time + " " + pid + " " + tid + " " + level + " " + tag + " " + _color_log(fgreen, msg)
    # elif level == 'W':
    #     return time + " " + pid + " " + tid + " " + level + " " + tag + " " + _color_log(fyellow, msg)
    # elif level == 'E':
    #     return time + " " + pid + " " + tid + " " + level + " " + tag + " " + _color_log(fred, msg)
    # else:
    #     time + " " + pid + " " + tid + " " + level + " " + tag + " " + msg


def split_log(line):
    pattern = re.finditer(r'(^(\d+-\d+ \d+:\d+:\d+.\d+)) +(\d+) +(\d+) +(\w) +(.*?): (.*)\n', line)
    for p in pattern:
        # print("Group->1:" + p.group(1) + " 2:" + p.group(2) + " 3:" + p.group(3) + " 4:" + p.group(4) + " 5:" + p.group(5) + " 6:" + p.group(6) + " 7:" + p.group(7))
        return p.group(1), p.group(3), p.group(4), p.group(5), p.group(6), p.group(7)
    return "", "", "", "", "", ""


for line1 in sys.stdin:
    # sys.stdout.write(line1)
    # print(_color_log(bred, line1))
    (time, pid, tid, level, tag, msg) = split_log(line1)
    log = color_log(time, pid, tid, level, tag, msg)
    for l in log:
        sys.stdout.write(l)
