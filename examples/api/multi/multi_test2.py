#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
import time
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.tools.list_ports import get_ports


"""
开启监听串口线程，自动连接所有过滤到的串口，并同步运动
运行中途可以断开或新连接机械臂
"""

swifts = {}
speed = 1000000
timeout = None
lock = threading.Lock()


class ListenPort(threading.Thread):
    def __init__(self):
        super(ListenPort, self).__init__()
        self.daemon = True
        self.alive = True

    def run(self):
        while self.alive:
            try:
                ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'})
                for port in ports:
                    if port['device'] not in swifts.keys():
                        new_swift = SwiftAPI(port=port['device'])
                        new_swift.waiting_ready()
                        print(new_swift.port, new_swift.get_device_info())
                        new_swift.set_mode(mode=0)
                        with lock:
                            swifts[port['device']] = new_swift
                    else:
                        swift = swifts[port['device']]
                        if not swift.connected:
                            with lock:
                                swifts.pop(port['device'])
            except Exception as e:
                pass
            time.sleep(0.001)


listen = ListenPort()
listen.start()


def multi_swift_cmd(cmd, *args, **kwargs):
    wait = kwargs.pop('wait', False)
    timeout = kwargs.get('timeout', None)
    with lock:
        for swift in swifts.values():
            if swift.connected and swift.power_status:
                swift_cmd = getattr(swift, cmd)
                swift_cmd(*args, wait=False, **kwargs)
        if wait:
            for swift in swifts.values():
                if swift.connected:
                    if len(swifts.values()) > 1:
                        swift.flush_cmd(timeout, wait_stop=True)
                    else:
                        swift.flush_cmd(timeout)
    time.sleep(0.001)


while True:
    multi_swift_cmd('set_position', x=300, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=100, z=100, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=-100, z=100, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)
    # time.sleep(0.01)





