from typing import TypedDict

class ClevastDevices():
    result: list

class ClevastDeviceInfo(TypedDict, total=False):
    """Device information returned by the API"""
    id: str
    name: str
    picture: str
    nickname: str
    model: str
    status: int
    deviceLifeStatus:int
    workStatus: int
    onlineStatus: int
    productId: str
    productName: str
    deviceId: str
    productTypeId: str
    productType: str
    pairing:int 
    lineDetection: str
    userId: int
    parentUserId: int
    version: str
    

class ClevastDeviceData(TypedDict, total=False):
    timing_plan: str
    tone_switch: int
    wifi_firmware_version: str
    current_humidity: int
    time_zone: str
    mist_level: int
    mcu_firmware_version: str
    work_state: int
    deviceLifeStatus: int
    humidity: int 
    get_onlinetime: str
    time: int
    remaining_work_time: int
    status: int