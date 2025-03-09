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