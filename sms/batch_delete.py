import subprocess


def execute_shell(shell_cmd):
    p = subprocess.Popen(shell_cmd, shell=True, stdout=subprocess.PIPE)
    (logs, _) = p.communicate()
    logs = logs.decode(encoding='UTF-8')
    return logs


i = 1
while i < 100:
    execute_shell("echo \"AT+CMGD=" + str(i) + "\" > /dev/cu.usbserial-1420")
    i = i + 1
