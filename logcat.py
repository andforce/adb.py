import re
import sys
import re

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

need_high_light_tags = ['ActivityManager', 'am_kill ', 'ActivityThread']


def _color_tag(color, tag):
    return "\033[0;%sm%s\033[0m" % (color, "%20s" % tag)


def _color_log(color, msg):
    return "\033[0;%sm%s\033[0m" % (color, msg)


def cut_long_msg(msg):
    length = 1500
    list_of_strings = []
    r = list(range(0, len(msg), length))
    if len(r) == 1:
        list_of_strings.append(msg)
    else:
        for i in r:
            if i == 0:
                list_of_strings.append(msg[i:length + i] + '↩')
            elif i == (len(r) - 1):
                list_of_strings.append(msg[i:length + i])
            else:
                list_of_strings.append(msg[i:length + i] + '↩')

    return list_of_strings


def color_log(time, pid, tid, level, tag, msg):
    list_result = []
    list_msg = cut_long_msg(msg)
    tag_fix = tag.replace("%", "%%")
    if need_high_light_tags.__contains__(tag_fix):
        tag_fix = _color_tag(fyellow, tag_fix)
    i = 0
    for msg_log in list_msg:
        msg_log_fix = msg_log.replace("%", "%%")
        i = i + 1
        if level == 'V':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag_fix)
            part2 = msg_log
        elif level == 'D':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag_fix)
            part2 = _color_log(fblue, msg_log_fix)
        elif level == 'I':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag_fix)
            part2 = _color_log(fgreen, msg_log_fix)
        elif level == 'W':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag_fix)
            part2 = _color_log(fyellow, msg_log_fix)
        elif level == 'E':
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag_fix)
            part2 = _color_log(fred, msg_log_fix)
        else:
            part1 = "%s [%5s/%-5s] %s %20s: " % (time, pid, tid, level, tag_fix)
            part2 = msg_log

        if i == 1:
            list_result.append(part1 + part2 + "\n")
        else:
            list_result.append("".ljust(len(part1)) + part2 + "\n")
    return list_result


def split_log(long_log):
    match = re.match(r'^(\d+-\d+ \d+:\d+:\d+.\d+) +(\d+) +(\d+) +(\w) +(.*?): (.*)\n', long_log)
    if match is None:
        return None
    else:
        return match.groups()


def format_log(lines):
    for line in lines:
        result = split_log(line)
        if result is None:
            sys.stdout.write(line)
        else:
            (time, pid, tid, level, tag, msg) = result
            log = color_log(time, pid, tid, level, tag, msg)
            for l in log:
                sys.stdout.write(l)


try:
    all_log = []
    if len(sys.argv) == 1:
        format_log(sys.stdin)
    elif sys.argv[1] == 'pidof':
        print(sys.argv[1] + " " + sys.argv[2])
        filter_log = ""
        pkg_name = sys.argv[2]
        for line in sys.stdin:
            all_log.append(line)
            if line.find(pkg_name) != -1:
                # sys.stdout.write(line)
                filter_log = filter_log + line
        # print(filter_log)
        pids = set()
        for match in re.finditer(r'(\d+):' + pkg_name, filter_log):
            print(match.group(1))
            pids.add(match.group(1))
        for match in re.finditer(r'(\d+),\d+,' + pkg_name, filter_log):
            print(match.group(1))
            pids.add(match.group(1))

        format_result = []
        for pid in pids:
            format_result.append("--------------------------- pid of " + pid + "----------------------------\n")
            for one in all_log:
                if one.find(' ' + pid + ' ') != -1:
                    # sys.stdout.write(one)
                    format_result.append(one)
            format_result.append("=========================== pid of " + pid + "============================\n")
        format_log(format_result)
except BrokenPipeError:
    exit(0)

