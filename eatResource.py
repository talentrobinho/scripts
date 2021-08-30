#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import time
import os
from time import clock
import argparse
from multiprocessing import Process
from multiprocessing import cpu_count
import math

def exec_func(bt):
    while True:
        for i in range(0, 9600000):
            pass
        time.sleep(bt)

def eatCpu(cpu_logical_count, cpu_sleep_time):
    p = Process(target=exec_func, args=("bt",))
    ps_list = []
    for i in range(0, cpu_logical_count):
        ps_list.append(Process(target=exec_func, args=(cpu_sleep_time,)))

    for p in ps_list:
        p.start()

    for p in ps_list:
        p.join()

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description='runing')
    parse.add_argument(
        "-c",
        "--count",
        default=cpu_count()/2,
        help="""指定cpu核数
		不加-c参数默认为当前cpu最大核数的1/2"""
        )
    parse.add_argument(
        "-t",
        "--time",
        default=0.01,
        help="""cpu运算频率时间，间隔越小占用越高
		默认0.01"""
        )
    parse.add_argument(
        "-m",
        "--memory",
        default=1,
        help="""内存占用，单位GB, 默认1GB"""
        )

    args = parse.parse_args()
    cpu_logical_count = int(args.count)
    cpu_sleep_time = args.time
    try:
    	memory_used_gb = int(args.memory)
    except Exception as ex:
        raise ValueError(ex)

    try:
        cpu_sleep_time = int(args.time)
    except ValueError:
        try:
            cpu_sleep_time = float(args.time)
        except ValueError as ex:
            raise ValueError(ex)

    pid = os.fork()
    if pid == 0:
        size = int(memory_used_gb)
        s = ' ' * (size * 1024 * 1024 * 1024)
	eatCpu(cpu_logical_count, cpu_sleep_time)
    else:
        sys.exit(0)
