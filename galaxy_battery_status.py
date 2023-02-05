import subprocess

def check_battery_status():
    cmd = 'cat /sys/class/power_supply/battery/capacity'
    try:
        return 'Galaxy Battery: {}%'.format(str(subprocess.run(cmd.split(), capture_output=True).stdout.decode('utf-8').rstrip()))
    except Exception as e:
        return "Failed to get battery status.\n" + str(e)


