# src/engine/base/runtime_log.py

import os
import json
from datetime import datetime

# 从配置文件获取提示模板读入的方式
# from config import LOG_METHOD
# if LOG_METHOD == 'mongodb':
#     from services.mongodb import logs_collection # client = MongoClient() 的对象
# elif LOG_METHOD == 'file':
#     from config import LOG_FILE_PATH # log的主路径，如“log/run_records”

LOG_METHOD = 'file'
LOG_FILE_PATH = 'log/run_records/'

class RuntimeLog:
    def __init__(self, template_id, class_name, run_id, task_id=None, parent_run_id=None, inputs=None, attributes=None):
        """
        初始化日志并创建数据库记录
        :param class_name: 类名，例如 "task"
        :param template_id: 模板 ID
        :param attributes: 日志附加属性（默认空字典）
        :param inputs: 输入参数（必填）
        :param task_id: 任务 ID（可选）
        :param parent_run_id: 父运行 ID（可选）
        """
        self.log = {
            "run_id": run_id,
            "class": class_name or "unknow",
            "status": "running",
            "task_id": task_id,
            "parent_run_id": parent_run_id,
            "template_id": template_id,
            "start_time": self.current_time(),
            "end_time": None,
            "inputs": inputs,
            "outputs": {},
            "attributes": attributes or {},
            "error_message": None,
            "records": []
        }

        # 在数据库或文件系统中保存初始日志记录
        self.update_log()

    def current_time(self):
        """获取当前时间，格式化为ISO 8601字符串"""
        return datetime.now().isoformat()

    def update_log(self):
        """更新日志，支持MongoDB和文件系统的更新"""
        if LOG_METHOD == 'mongodb':
            self.save_to_mongodb()
        elif LOG_METHOD == 'file':
            self.save_to_file()

    def save_to_mongodb(self):
        """将初始日志记录保存到MongoDB"""
        logs_collection.insert_one(self.log)

    def save_to_file(self):
        """将初始日志记录保存到文件系统"""
        task_id = self.log.get('task_id', '#')
        dir_path = task_id if task_id is not None else '#'
        log_dir = os.path.join(LOG_FILE_PATH, dir_path)
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"{self.log['run_id']}.log")

        with open(log_path, 'w') as log_file:
            json.dump(self.log, log_file, default=str, indent=4)

    def add_record(self, message):
        """
        添加一条运行记录并更新到数据库或文件
        :param message: 记录消息
        """
        record = {
            "timestamp": self.current_time(),
            "message": message
        }
        self.log['records'].append(record)

        self.update_log()

    def mark_as_failed(self, error_message):
        """
        添加错误消息并更新状态为失败 
        :param error_message: 错误信息
        """
        self.log['error_message'] = error_message
        self.log['status'] = 'failed'
        self.log['end_time'] = self.current_time()

        self.update_log()

    def mark_as_complete(self, output_data):
        """
        结束日志，添加输出并更新状态为成功
        :param output_data: 输出参数
        """
        self.log['outputs'] = output_data
        self.log['status'] = 'success'
        self.log['end_time'] = self.current_time()

        self.update_log()