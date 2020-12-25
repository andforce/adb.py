# !/usr/bin/python
import subprocess
import sys
import time
import os
import re
import math
import json

def find_with_reg(reg, src):
    pattern = re.search(reg, src)
    if pattern is None:
        return None
    return pattern.group()


def device_info():
    info = {}
    out = execute_shell('adb shell getprop ro.product.model').strip()
    info['Product Model'] = out
    out = execute_shell('adb shell wm size').split(':')[1].strip()
    info['Physical Size'] = out
    out = execute_shell('adb shell wm density')
    if out.find('Override density') != -1:
        density = {}
        for line in out.strip().split('\n'):
            kv = line.split(':')
            density[kv[0].strip()] = kv[1].strip()
        info['Density'] = density
    else:
        info['Density'] = out.strip().split(":")[1].strip()
    out = execute_shell('adb shell dumpsys window displays')
    # print(out)
    """
    可能存在多个Display，切割成多个
    """
    pattern = re.finditer('Display: mDisplayId=(.*\s*)*?Control map:', out)
    display_info = []
    for group in pattern:
        g = group.group()
        display = find_with_reg("(?<=mDisplayInfo=DisplayInfo)(.*)", g)
        # format
        display = re.sub(r'(\{\")(.*?, )(\w+ )(\d)(")', r'{\3\4', display)
        display = re.sub(r'(\d+)( x )(\d+)', r'\1x\3', display)
        display = re.sub(r'([A-Za-z]+) ([A-Za-z]+ )', r'\1_\2', display)
        display = re.sub(r'([A-Za-z]+)=', r'\1 ', display)
        # find all key
        display = re.sub(r'([a-zA-Z]+_?)([a-zA-Z]+) ', r'"\1\2": ', display)
        display = re.sub(r'": (\d+x\w+)', r'": "\1"', display)
        display = re.sub(r'"state": (([a-zA-Z]+(, )?_?)+[\w])', r'"state": "\1"', display)
        display = re.sub(r'"hdrCapabilities": (\S+), "', r'"hdrCapabilities": "\1", "', display)
        display = re.sub(r'"density": (.*dpi)', r'"density": "\1"', display)
        display = re.sub(r'"type": (([a-zA-Z]+_?)+)', r'"type": "\1"', display)
        display = json.loads(display)
        # print(display)
        display_info.append(display)
        # print(display_id)
    info['display_info'] = display_info

    out = execute_shell("adb shell service call iphonesubinfo 1 | cut -c 52-66 | tr -d '.[:space:]'")
    info['IMEI'] = out
    out = execute_shell("adb shell service call iphonesubinfo 3 i32 1 | cut -c 52-66 | tr -d '.[:space:]'")
    info['MEID'] = out

    out = execute_shell('adb shell getprop ro.build.version.release')
    info['Android Version'] = out.strip()

    # CPU Info
    out = execute_shell('adb shell cat /proc/cpuinfo')
    cpu = {}
    processor = find_with_reg('(?<=Processor	: ).*', out)
    cpu['Processor'] = processor
    processor_count = out.count('processor')
    cpu['Processor Count'] = processor_count
    hardware = find_with_reg('(?<=Hardware	: ).*', out)
    cpu['Hardware'] = hardware
    # CPU abi
    out = execute_shell('adb shell cat /system/build.prop | grep ro.product.cpu.abi | grep =')
    for line in out.splitlines():
        kv = line.split('=')
        k_tmp = kv[0].split('.')
        k = k_tmp[len(k_tmp) - 1]
        v = kv[1].strip()
        cpu[k] = v
    info['Cpu Info'] = cpu

    # Memory Info
    out = execute_shell('adb shell cat /proc/meminfo')
    memory_info = {}
    for minfo in out.split('\n'):
        if minfo.startswith('MemTotal:'):
            total = find_with_reg('\d+', minfo)
            total_flot = float(total) / 1024 / 1024
            memory_info['MemTotal'] = str(math.ceil(total_flot)) + ' GB'
        if minfo.startswith('MemFree:'):
            free = find_with_reg('\d+', minfo)
            memory_info['MemFree'] = free + " kB"
    info['Memory Info'] = memory_info

    json_str = json.dumps(info, ensure_ascii=False, indent=2, sort_keys=False)
    # highlight key
    json_str = re.sub(r'(".*"):', r'\033[0;33m\1\033[0m:', json_str)
    # highlight {
    json_str = re.sub(r'({)\n', r'\033[0;32m\1\033[0m\n', json_str)
    json_str = re.sub(r'(})', r'\033[0;32m\1\033[0m', json_str)
    print(json_str)
    # print(info)


def _red_log(message):
    return "\033[0;31m%s\033[0m" % message


def _green_log(message):
    return "\033[0;32m%s\033[0m" % message


def _yellow_log(message):
    return "\033[0;33m%s\033[0m" % message


def is_root():
    result = execute_shell("adb shell whoami")
    return result.count('root') > 0


def enter_root():
    execute_shell("adb root && adb remount")


def is_fastboot_mode():
    out = execute_shell("fastboot devices")
    return out.find('fastboot') != -1


def is_se():
    if find_devices():
        if not is_root():
            enter_root()
        out = execute_shell('adb shell cat /sys/hwinfo/secboot-version')
        return out.find("secboot_version=SE") != -1
    if is_fastboot_mode():
        out = execute_shell('fastboot oem device-info')
        return out.find('SecureBootEnabled=true') != -1


def execute_shell(shell_cmd):
    # print(shell_cmd)
    p = subprocess.Popen(shell_cmd, shell=True, stdout=subprocess.PIPE)
    (logs, _) = p.communicate()
    logs = logs.decode(encoding='UTF-8')
    return logs


def fetch_build_server(branch_name='darwin'):
    build_time = time.strftime("%Y%m%d", time.localtime())
    git_log_command = 'smbclient ' \
                      '-c "cd daily/darwin/SE-r00062.2/release-%s;ls" //10.79.121.16/flash ' \
                      '-U wangdiyuan%%Andforce\!@#456 ' \
                      '-W smartisan.cn | grep userdebug' % build_time
    logs = execute_shell(git_log_command)
    logs = logs.splitlines(False)

    results = []
    for line in logs:
        first = line.split("      ")[0].strip()
        if first.endswith(".tgz"):
            results.append(first)
    result = results[len(results) - 1]
    print(_yellow_log("last_build_image:") + result)
    return result


def download(build_image):
    print('start download:' + _red_log(build_image))
    build_time = time.strftime("%Y%m%d", time.localtime())
    download_cmd = 'cd /home/dy/Documents/darwin;' \
                   'smbclient -c "cd daily/darwin/SE-r00062.2/release-%s;get %s" //10.79.121.16/flash ' \
                   '-U wangdiyuan%%Andforce\!@#456 ' \
                   '-W smartisan.cn' % (build_time, build_image)
    logs = execute_shell(download_cmd)
    print(logs)


def extract_build_image(build_image):
    print('start extract:' + _red_log(build_image))
    logs = execute_shell("cd ~/Documents/darwin && tar xvf " + build_image)
    print(logs)


def reboot_bootloader():
    log = execute_shell("adb reboot bootloader")
    while execute_shell("fastboot devices") == '':
        print("... ", sep=' ', end='', flush=True)
        time.sleep(1)
    else:
        print(_yellow_log("\ndevice have in bootloader mode"))


def find_devices():
    log = execute_shell("adb devices")
    # print(log)
    if log.strip('\n') == "List of devices attached":
        return False
    else:
        return True


def flash_image(build_image):
    wait_device_connect()
    reboot_bootloader()
    extract_image = build_image[:-4].strip()
    flash_cmd = 'cd /home/dy/Documents/darwin/%s && ' \
                'chmod a+x apps/* && ' \
                'python fastboot-flash.py' % extract_image
    print(_yellow_log("flash_image:") + flash_cmd)
    execute_shell(flash_cmd)


def wait_device_connect():
    # print(_yellow_log("waiting device connecting"))
    while not find_devices():
        print("... ", sep=' ', end='', flush=True)
        time.sleep(1)
    else:
        print(_yellow_log("\ndevice connected"))


def wait_device_reboot_complete():
    wait_device_connect()
    print(_yellow_log("waiting device reboot complete"))
    while execute_shell("adb shell dumpsys window windows | grep SetupWizardActivity").find(
            "SetupWizardActivity") <= 0:
        print("... ", sep=' ', end='', flush=True)
        time.sleep(1)
    else:
        print(_yellow_log("\ndevice has reboot completed"))


def skip_setup():
    print(_green_log("skip device setup."))
    if not find_devices():
        wait_device_connect()
    print("disable-verity")
    execute_shell('adb root && adb disable-verity && adb reboot')
    print("等待手机重启")
    wait_device_connect()
    print("手机重启结束，等待进入设置页面...")
    wait_device_reboot_complete()
    print("开始跳过设置页面")
    skip_cmd = 'adb root && adb remount && ' \
               'adb shell am start -n com.smartisanos.setupwizard/.SetupWizardCompleteActivity && ' \
               'sleep 2 && ' \
               'adb shell input tap 540 2300 && adb shell settings put system screen_off_timeout 600001'
    execute_shell(skip_cmd)


def is_build_image_downloaded(build_image):
    return os.path.exists(os.path.expanduser("~/Documents/darwin/" + build_image))


def is_build_image_extracted(build_image):
    return os.path.exists(os.path.expanduser("~/Documents/darwin/" + build_image[:-4]))


device_info()

# print("fastboot mode: " + str(is_fastboot_mode()))
# is_se()
# enter_root()
# print(is_root())
# if find_devices():
#     find_image = fetch_build_server()
#     print(find_image)
#     if not is_build_image_downloaded(find_image):
#         print("build image not download")
#         download(find_image)
#
#     if not is_build_image_extracted(find_image):
#         extract_build_image(find_image)
#
#     flash_image(find_image)
#     skip_setup()
# else:
#     print("devices not connect!!!")
