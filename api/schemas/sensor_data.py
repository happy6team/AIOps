# schemas/sensor_data.py
from pydantic import BaseModel
from datetime import datetime

class SensorDataCreate(BaseModel):
    collection_time: datetime
    footfall: int
    temp_mode: int
    AQ: float
    USS: float
    CS: float
    VOC: float
    RP: float
    IP: float
    temperature: float
    fail: bool
    fail_probability: float
