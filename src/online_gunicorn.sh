#!/bin/bash
#
#使用gunicorn启动, 要求系统安装了gunicorn, gevent
#

dir=$(cd $(dirname $0); pwd)
cd $dir

#定义变量(自定义更改)

#准备环境
if [ -r online_preboot.sh ]; then
    . online_preboot.sh
fi

#定义常量(请勿更改)
host=$(python -c "from config import GLOBAL;print GLOBAL['Host']")
port=$(python -c "from config import GLOBAL;print GLOBAL['Port']")
procname=$(python -c "from config import GLOBAL;print GLOBAL['ProcessName']")
cpu_count=$(cat /proc/cpuinfo | grep "processor" | wc -l)
[ -d ${dir}/logs ] || mkdir -p ${dir}/logs
logfile=${dir}/logs/gunicorn.log
pidfile=${dir}/logs/${procname}.pid

function Monthly2Number() {
    case "$1" in
        Jan) echo 1;;
        Feb) echo 2;;
        Mar) echo 3;;
        Apr) echo 4;;
        May) echo 5;;
        Jun) echo 6;;
        Jul) echo 7;;
        Aug) echo 8;;
        Sep) echo 9;;
        Oct) echo 10;;
        Nov) echo 11;;
        Dec) echo 12;;
        *)   exit;;
    esac
}

case $1 in
start)
    if [ -f $pidfile ]; then
        echo "Has pid($(cat $pidfile)) in $pidfile, please check, exit." ; exit 1
    else
        gunicorn -w $cpu_count --threads 16 -b ${host}:${port} main:app -k gevent --daemon --pid $pidfile --log-file $logfile --max-requests 250 --name $procname
        sleep 1
        pid=$(cat $pidfile)
        [ "$?" != "0" ] && exit 1
        echo "$procname start over with pid ${pid}"
    fi
    ;;

run)
    #前台运行
    gunicorn -w $cpu_count --threads 16 -b ${host}:${port} main:app -k gevent --max-requests 250 --name $procname
    ;;

stop)
    if [ ! -f $pidfile ]; then
        echo "$pidfile does not exist, process is not running"
    else
        echo "Stopping ${procname}..."
        pid=$(cat $pidfile)
        kill $pid
        while [ -x /proc/${pid} ]
        do
            echo "Waiting for ${procname} to shutdown ..."
            kill $pid ; sleep 1
        done
        echo "${procname} stopped"
        rm -f $pidfile
    fi
    ;;

status)
    if [ ! -f $pidfile ]; then
        echo -e "\033[39;31m${procname} has stopped.\033[0m"
        exit
    fi
    pid=$(cat $pidfile)
    procnum=$(ps aux | grep -v grep | grep $pid | grep $procname | wc -l)
    m=$(ps -eO lstart | grep $pid | grep $procname | grep -vE "worker|grep|Team.Api\." | awk '{print $3}')
    t=$(Monthly2Number $m)
    if [[ "$procnum" != "1" ]]; then
        echo -e "\033[39;31m异常，pid文件与系统pid数量不相等。\033[0m"
        echo -e "\033[39;34m  pid数量：${procnum}\033[0m"
        echo -e "\033[39;34m  pid文件：${pid}($pidfile)\033[0m"
    else
        echo -e "\033[39;33m${procname}\033[0m":
        echo "  pid: $pid"
        echo -e "  state:" "\033[39;32mrunning\033[0m"
        echo -e "  process start time:" "\033[39;32m$(ps -eO lstart | grep $pid | grep $procname | grep -vE "worker|grep|Team.Api\." | awk '{print $6"-"$3"-"$4,$5}' | sed "s/${m}/${t}/")\033[0m"
        echo -e "  process running time:" "\033[39;32m$(ps -eO etime| grep $pid | grep $procname | grep -vE "worker|grep|Team.Api\." | awk '{print $2}')\033[0m"
    fi
    ;;

reload)
    if [ -f $pidfile ]; then
        kill -HUP $(cat $pidfile)
    fi
    ;;

restart)
    bash $(basename $0) stop
    bash $(basename $0) start
    ;;

*)
    echo "Usage: $0 start|run|stop|reload|restart|status"
    ;;
esac
