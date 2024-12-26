# src/engine/scheduler/process/process.py

# 导入配置文件从而确定根路径
from config import root_path
# 导入基础类
from engine.scheduler.scheduler import Scheduler

class Process(Scheduler):
    def __init__(self, template_id, secret=None, task_id=None, parent_run_id=None):
        super().__init__(template_id, secret, task_id, parent_run_id)
        # 添加Process类到类映射中
        self.EXECUTION_CLASS_MAPPING['process'] = Process

    # 校验提示模板是否合法
    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 调用父类的 validate_template 方法，进行基础的模板校验
        try:
            validated_template = super().validate_template(template)
        except cls.TemplateError as base_errors:
            # 从父类校验中收集错误
            errors.extend(base_errors.errors)

        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

    # 执行函数
    def _execute(self, inputs):
        return {}