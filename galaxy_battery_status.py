import subprocess
from telegram_bot import send_to_telegram


cmd = 'cat /sys/class/power_supply/battery/capacity'
try:
    send_to_telegram('Galaxy Battery: ' + str(subprocess.run(cmd.split()).stdout))
except Exception as e:
    send_to_telegram("Failed to get battery status.\n" + str(e))


