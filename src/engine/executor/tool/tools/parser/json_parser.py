# src/engine/executor/tool/tools/parser/json_parser.py

import json

class JSONParser:
    @staticmethod
    def metadata():
        return {
            "id": "parser.json_parser",
            "name": "json_parser",
            "description": "解析 JSON 字符串并转换为字典。",
            "input": [
                {"name": "json_string", "type": "str", "description": "JSON 格式的字符串"}
            ],
            "output": [
                {"name": "data", "type": "dict", "description": "解析后的字典数据"}
            ]
        }

    @staticmethod
    def run(inputs):
        json_string = inputs.get("json_string", "").strip()
        if not json_string:
            raise ValueError("Input 'json_string' cannot be empty.")
        try:
            return {"data": json.loads(json_string)}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string. Error: {e}")