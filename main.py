import pandas as pd
from config.config import GNERATE_DATA_SOURCE_PATH
from cruds.sensordata import create_sensor_data
from api.schemas.sensor_data import SensorDataCreate  # Pydantic 모델
import pandas as pd
import numpy as np

generate_df = pd.read_csv(GNERATE_DATA_SOURCE_PATH)

generate_df.rename(columns={
    "tempMode": "temp_mode",
    "Temperature": "temperature"}, inplace=True)

# 누락된 컬럼 채우기
if 'fail_probability' not in generate_df.columns:
    generate_df['fail_probability'] = np.nan

for idx, row in generate_df.iterrows():
    print(row)
