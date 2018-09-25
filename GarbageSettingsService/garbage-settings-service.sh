#! /bin/sh
# /etc/init.d/garbage-settings-service
#

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting node service "
    node /home/pi/Developer/GarbageSettingsService/app.js &> /dev/null &
    ;;
  stop)
    echo "Stopping all node processes"
    killall node
    ;;
  *)
    echo "Usage: /etc/init.d/garbage-settings-service {start|stop}"
    exit 1
    ;;
esac

exit 0