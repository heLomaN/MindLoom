# src/engine/executor/action/action.py

from config import root_path
from engine.executor.executor import Executor

class Action(Executor):
    def __init__(self, id, secret):
        super().__init__(id, secret)
    
    # 执行流程
    def _execute(self, inputs):
        if self.id == "action_weather0001":
            outputs = {
                "weather_result": "{\"results\":[{\"location\":{\"id\":\"WX4FBXXFKE4F\",\"name\":\"北京\",\"country\":\"CN\",\"path\":\"北京,北京,中国\",\"timezone\":\"Asia/Shanghai\",\"timezone_offset\":\"+08:00\"},\"daily\":[{\"date\":\"2024-12-03\",\"text_day\":\"晴\",\"code_day\":\"0\",\"text_night\":\"多云\",\"code_night\":\"4\",\"high\":\"9\",\"low\":\"-3\",\"rainfall\":\"0.00\",\"precip\":\"0.00\",\"wind_direction\":\"西南\",\"wind_direction_degree\":\"225\",\"wind_speed\":\"8.4\",\"wind_scale\":\"2\",\"humidity\":\"47\"},{\"date\":\"2024-12-04\",\"text_day\":\"多云\",\"code_day\":\"4\",\"text_night\":\"晴\",\"code_night\":\"1\",\"high\":\"8\",\"low\":\"-2\",\"rainfall\":\"0.00\",\"precip\":\"0.00\",\"wind_direction\":\"西南\",\"wind_direction_degree\":\"225\",\"wind_speed\":\"8.4\",\"wind_scale\":\"2\",\"humidity\":\"43\"},{\"date\":\"2024-12-05\",\"text_day\":\"晴\",\"code_day\":\"0\",\"text_night\":\"多云\",\"code_night\":\"4\",\"high\":\"9\",\"low\":\"-1\",\"rainfall\":\"0.00\",\"precip\":\"0.00\",\"wind_direction\":\"西北\",\"wind_direction_degree\":\"315\",\"wind_speed\":\"3.0\",\"wind_scale\":\"1\",\"humidity\":\"59\"}],\"last_update\":\"2024-12-03T08:00:00+08:00\"}]}"
            }
            return outputs
        return {}