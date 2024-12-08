# src/engine/scheduler/task/task.py

# 导入配置文件从而确定根路径
from engine.scheduler.scheduler import Scheduler
from engine.scheduler.process.process import Process

class Task(Scheduler):
    # 定义主流程调用
    main_call = {}

    def __init__(self, id, secret):
        super().__init__(id, secret)
        # 添加Process类到类映射中
        self.EXECUTION_CLASS_MAPPING['process'] = Process
        # 设置主流程
        self.main_call = self.template["execution"]["call"]

    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 获取当前类名并转为小写
        class_name = cls.__name__.lower()

        # 调用父类的 validate_template 方法
        try:
            validated_template = super().validate_template(template)
        except cls.TemplateError as base_errors:
            # 从父类校验中收集错误
            errors.extend(base_errors.errors)

        # 校验 'execution' 和 'call' 的合法性
        if not isinstance(template, dict) or "execution" not in template or not isinstance(template["execution"], dict):
            pass
        elif "call" in template["execution"]:
            try:
                # 校验 'call' 字段
                call_dict = cls.validate_template_call(template["execution"]["call"])
                validated_template.setdefault("execution", {})["call"] = call_dict
            except cls.TemplateError as call_errors:
                errors.append(f"'{class_name}' 中 'execution' 的 'call' 字段存在以下错误：")
                errors.extend(call_errors.errors)
                errors.append(f"'call' 字段错误展示结束。")
        else:
            errors.append(f"'{class_name}' 中 'execution' 字段必须包含 'call' 字段。")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

    # 执行函数
    def run(self, inputs):
        # 校验输入参数是否合法
        self.validate_inputs(inputs)
        # 将输入参数设置到类变量列表
        self.set_parameters_by_inputs(inputs)
        # 执行主流程调用
        self.call_execute(self.main_call)
        # 获取输出参数
        outputs = self.get_outputs_by_parameters()
        return outputs