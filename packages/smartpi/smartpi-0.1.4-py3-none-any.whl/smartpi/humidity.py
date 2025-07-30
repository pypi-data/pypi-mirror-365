# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver

             
#湿度读取 port:连接P端口；
def get_value(port:bytes) -> Optional[bytes]:
    humiture_str=[0xA0, 0x0C, 0x01, 0x71, 0x00, 0xBE]
    humiture_str[0]=0XA0+port
    humiture_str[4]=1 
    response = base_driver.single_operate_sensor(humiture_str)
    if response:
        return response[4]
    else:
        return -1




