# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


#温度读取 port:连接P端口；
def get_value(port:bytes) -> Optional[bytes]:
    temp_str=[0xA0, 0x0C, 0x01, 0x71, 0x00, 0xBE]
    temp_str[0]=0XA0+port
    temp_str[4]=0 
    response = base_driver.single_operate_sensor(temp_str)
    if response:
        return response[4]
    else:
        return -1
        