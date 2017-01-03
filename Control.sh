#!/bin/sh

dir=$(cd $(dirname $0); pwd)
log_dir=${dir}/src/logs
[ -d $log_dir ] || mkdir $log_dir
procname=$(grep '"ProcessName":' ${dir}/src/config.py | awk '{print $2}' | awk -F \" '{print $2}'|head -1)
pidfile=${log_dir}/${procname}.pid

function _start()
{
    $(which python) -O ${dir}/src/Product.py &>> ${log_dir}/output.log &
    pid=$!
    echo $pid > $pidfile
    echo "$procname start over."
}

function _start_front()
{
    $(which python) -O ${dir}/src/Product.py
}

function _start_test()
{
    nohup $(which python) ${dir}/src/main.py > ${log_dir}/output.log &
    pid=$!
    echo $pid > $pidfile
    echo "$procname start over."
}

function _status()
{
    if [ ! -f $pidfile ]; then
        if [[ $(ps aux | grep -v grep | grep $procname | wc -l) -lt 1 ]];then
            echo -e "\033[39;31m${procname} has stopped.\033[0m"
            exit 127
        else
            pid=$(pgrep $procname)
            [ "$pid" = "root" ] && pid=$(ps aux | grep -v grep | grep $procname | awk '{print $1}')
        fi
    else
        pid=$(cat $pidfile)
    fi
    if [[ -z $pid ]]; then
        echo -e "\033[39;31mSTATUS ERROR!\033[0m"
    else
        echo -e "\033[39;33m${procname}\033[0m":
        echo "  pid: $pid"
        echo -e "  state:" "\033[39;32mrunning\033[0m"
        echo -e "  process start time:" "\033[39;32m$(ps -eO lstart | grep $pid | grep -vE "worker|grep" | awk '{print $6"-"$3"-"$4,$5}')\033[0m"
        echo -e "  process running time:" "\033[39;32m$(ps -eO etime| grep $pid | grep -vE "worker|grep" | awk '{print $2}')\033[0m"
    fi
}

case $1 in
start)
    if [ -f $pidfile ]; then
        if [[ $(ps aux | grep $(cat $pidfile) | grep -v grep | wc -l) -lt 1 ]]; then
            _start
        fi
    else
        _start
    fi
    ;;

front)
    if [[ $(ps aux | grep $procname | grep -v grep | wc -l) -lt 1 ]]; then
        _start_front
    fi
    ;;

test)
    if [ -f $pidfile ]; then
        if [[ $(ps aux | grep $(cat $pidfile) | grep -v grep | wc -l) -lt 1 ]]; then
            _start_test
        fi
    else
        _start_test
    fi
    ;;

stop)
    [ -f $pidfile ] && kill -9 `cat $pidfile`
    retval=$?
    if [ $retval -ne 0 ]; then
        killall $procname
    fi
    rm -f $pidfile
    echo "$procname stop over."
    ;;

status)
    _status
    ;;

restart)
    sh $0 stop
    sh $0 start
    ;;

*)
    sh $0 start
    ;;
esac
