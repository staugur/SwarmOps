#!/bin/bash

dir=$(cd $(dirname $0); pwd)
tail -f ${dir}/logs/sys.log | grep -v Put2Etcd | grep -n --color=auto $(date +%F)