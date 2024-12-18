# src/engine/executor/tool/tools/time/local_time.py

from datetime import datetime
import pytz

class LocalTime:
    @staticmethod
    def metadata():
        return {
            "id": "time.local_time",
            "name": "get_local_time",
            "description": "获取本地时间的字符串，包括日期、时间、星期和时区。",
            "input": [
                {"name": "timezone", "type": "str", "description": "时区名称，例如 'Asia/Shanghai'"}
            ],
            "output": [
                {"name": "local_time", "type": "str", "description": "格式化的本地时间字符串"}
            ]
        }

    @staticmethod
    def run(inputs):
        timezone = inputs.get("timezone", "UTC")
        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return {"local_time": now.strftime("%Y-%m-%d %H:%M:%S %A %Z")}
        except Exception as e:
            raise ValueError(f"Invalid timezone: {timezone}. Error: {e}")