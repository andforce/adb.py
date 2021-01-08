import re
import sys
import datetime

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


def parse_log(_log_line):
    match = re.match(r'^(\d+-\d+ \d+:\d+:\d+.\d+) +(\d+) +(\d+) +(\w) +(.*?): (.*)\n', _log_line)
    if match is None:
        return None
    else:
        return match.groups()


def format_log(_lines):
    for _format_line in _lines:
        result = parse_log(_format_line)
        if result is None:
            sys.stdout.write(_format_line)
        else:
            (time, pid, tid, level, tag, msg) = result
            _color_logs = color_log(time, pid, tid, level, tag, msg)
            for _one_color_log in _color_logs:
                sys.stdout.write(_one_color_log)


def find_pid_set(_logs, _pid_names):
    _set = set()
    for _find_in_line in _logs:
        for _pid_name in _pid_names:
            if _pid_name.strip() == '':
                continue
            _patterns = [r'(\d+):' + _pid_name,
                         r'(\d+),\d+,' + _pid_name,
                         r'(\d+) +(\d+) +[A-Z] +' + _pid_name + r'( +)?:']
            for _pattern in _patterns:
                _match = re.search(_pattern, _find_in_line)
                if _match is not None:
                    _set.add(_match.group(1))
    return _set


print(sys.argv)


def read_log_time(_one_line_log):
    match = re.match(r'\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d', _one_line_log)
    if match is not None:
        return match.group()
    return None


def time_in_right(time, start_time, end_time):
    result = (start_time <= time) and (time <= end_time)
    return result


try:
    if len(sys.argv) == 1:
        format_log(sys.stdin)
    elif sys.argv[1] == 'pidof':
        _logs = []
        for _line in sys.stdin:
            _logs.append(_line)

        print(sys.argv[1] + " " + sys.argv[2])
        _pid_name_str = sys.argv[2]
        _pid_names = _pid_name_str.split("|")
        print(_pid_names)
        _pid_set = find_pid_set(_logs, _pid_names)
        print(_pid_set)

        for line in _logs:
            for _pid in _pid_set:
                if line.__contains__(' ' + _pid + ' '):
                    format_log([line])
    elif sys.argv[1] == 'time':
        _times = sys.argv[2].split("/")
        print(_times)
        _times_begin = _times[0]
        _times_end = _times[1]

        # 12-31 17:54:41.038
        begin_time = datetime.datetime.strptime(_times_begin, "%m-%d %H:%M:%S.%f")
        print(begin_time)
        end_time = datetime.datetime.strptime(_times_end, "%m-%d %H:%M:%S.%f")
        print(end_time)

        for _line in sys.stdin:
            _this_line_time_str = read_log_time(_line)
            if _this_line_time_str is not None:
                _this_date_time = datetime.datetime.strptime(_this_line_time_str, "%m-%d %H:%M:%S.%f")
                if time_in_right(_this_date_time, begin_time, end_time):
                    sys.stdout.write(_line)


except BrokenPipeError:
    exit(0)
