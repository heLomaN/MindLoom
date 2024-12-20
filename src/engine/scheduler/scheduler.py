# src/engine/scheduler/scheduler.py

# 导入配置文件从而确定根路径
from engine.base.base import Base
from engine.executor.action.action import Action
from engine.executor.generator.generator import Generator
from engine.executor.tool.tool import Tool

class Scheduler(Base):
    # 定义提示模板中的calss字段与py定义的类名的映射关系
    EXECUTION_CLASS_MAPPING = {
        'action': Action,
        'generator': Generator,
        'process': None,
        'tool': Tool
    }

    # 动态存储参数的字典
    parameters = {}

    def __init__(self, id, secret):
        super().__init__(id, secret)

    @classmethod
    def validate_template_call(cls, call_dict):
        errors = []  # 用于记录所有校验错误
        validated_call = {}  # 用于存储验证通过的字段

        # 检查 call_dict 是否是一个字典
        if not isinstance(call_dict, dict):
            errors.append("call_dict 必须是一个字典/MAP。")
        else:
            # 检查 "class" 键
            if "class" not in call_dict or not isinstance(call_dict["class"], str) or call_dict["class"] not in cls.EXECUTION_CLASS_MAPPING:
                errors.append("class 必须是 action，generator，process 或者 tool。")
            else:
                validated_call["class"] = call_dict["class"]

            # 检查 "id" 键
            if "id" not in call_dict or not isinstance(call_dict["id"], str):
                errors.append("id 必须存在并且是一个字符串。")
            else:
                validated_call["id"] = call_dict["id"]

            # 检查 "inputs" 和 "outputs" 键
            for key in ["inputs", "outputs"]:
                if key not in call_dict or (call_dict[key] is not None and not isinstance(call_dict[key], list)):
                    errors.append(f"{key} 必须存在，要么是 None 要么是一个列表。")
                else:
                    validated_call[key] = call_dict[key]

                    # 验证 inputs 和 outputs 的具体内容
                    if call_dict[key] is not None:
                        for item in call_dict[key]:
                            if not isinstance(item, dict):
                                errors.append(f"{key} 的每一项必须是一个字典/MAP。")
                                continue

                            # 检查每个 item 是否包含 "name" 和 "type" 键
                            required_item_keys = ["name", "type"]
                            for item_key in required_item_keys:
                                if item_key not in item:
                                    errors.append(f"{key} 中的每项必须包含 '{item_key}'。")
                                elif item[item_key] is None or not isinstance(item[item_key], str):
                                    errors.append(f"'{key}' -> '{item_key}' 必须是一个字符串。")

                            # 获取参数名字，如果漏写，打印：未知参数
                            param_name = item.get("name", "未知参数")

                            # 检查 "type" 的值是否合法
                            if "type" in item:
                                type_name = item["type"]
                                if type_name not in cls.PARAMETER_TYPE:
                                    errors.append(f"'{key}' 中的 '{param_name}' 的 'type' 不能是 '{type_name}'。")

                            # 检查 inputs 和 outputs 的特定字段
                            if key == "inputs":
                                if "source" not in item and "value" not in item:
                                    errors.append(f"'inputs' 中的 '{param_name}' 中必须包含 'source' 或 'value'。")
                                else:
                                    if item["source"] is None or not isinstance(item["source"], str):
                                        errors.append(f"'inputs' 中的 '{param_name}' 的 'source' 必须是一个字符串。")

                            elif key == "outputs":
                                if "target" not in item:
                                    errors.append(f"{key} 中必须包含 'target'。")
                                else:
                                    if item["target"] is None or not isinstance(item["target"], str):
                                        errors.append(f"'outputs' 中的 '{param_name}' 的 'target' 必须是一个字符串。") 

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_call

    # 校验提示模板是否合法
    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 获取当前类名
        class_name = cls.__name__
        class_name = class_name.lower()

        # 调用父类的 validate_template 方法
        try:
            validated_template = super().validate_template(template)
        except cls.TemplateError as base_errors:
            # 从父类校验中收集错误
            errors.extend(base_errors.errors)

        # 校验调度器必须包含 'execution'
        if 'execution' in template:
            validated_template['execution'] = {}
        else:
            errors.append(f"'{class_name}' 中必须包含 'execution' 字段。")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

    # 从传入的inputs中给参数字典赋值
    def set_parameters_by_inputs(self, inputs):
        # 如果提示模板规定输入变量是空值，不需要赋值
        if self.template["inputs"] == None:
            return
        # 根据模板规定需要输入，在类内存空间添加相应变量
        for template_input in self.template["inputs"]:
            param_name = template_input["name"]
            self.parameters[param_name] = inputs[param_name]

    # 从参数字典获取提示模板规定的outputs
    def get_outputs_by_parameters(self):
        # 如果提示模板规定的输出是空，直接返回空
        if self.template["outputs"] == None:
            return None
        # 如果提示模板规定的输出不是空，构造返回字典
        outputs = {}
        for template_output in self.template["outputs"]:
            param_name = template_output["name"]
            if param_name not in self.parameters:
                raise self.ValidationError(f"缺少输出参数: {param_name}。")
            outputs[param_name] = self.parameters[param_name]
        return outputs

    # 执行一次嵌套调用
    def _call_execute(self, call_dict):
        # 根据class字段名，获取类定义
        call_class = self.EXECUTION_CLASS_MAPPING[call_dict['class']]
        # 直接新实例化一个对应类的对象！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        call = call_class(call_dict['id'], secret = None)

        print(call_dict)

        # 从类内存变量中获取call需要的输入参数
        if call_dict['inputs'] == None:
            inputs = None
        else:
            inputs = {}
            for input in call_dict['inputs']:
                # 如果value存在，直接赋初始值
                if 'value' in input:
                    inputs[input['name']] = input['value']
                # 如果value不存在，需要从类内存空间获取
                else:
                    param_name = input['source']
                    # 校验参数是否存在
                    if param_name not in self.parameters:
                        raise self.ValidationError(f"缺少输入参数: {param_name}。")
                    # 校验参数类型是否合法
                    self.validate_param_type(param_name,input['type'],self.parameters[param_name])
                    # 给需要传入的参数赋值
                    inputs[input['name']] = self.parameters[param_name]

        # 执行一次call，获取outputs！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        outputs = call.run(inputs)

        # 将call调用返回的outputs放置到类内存空间的变量中
        if call_dict['outputs'] == None:
            pass
        else:
            for output in call_dict['outputs']:
                param_name = output['source']
                # 校验需要的输出参数是否存在
                if param_name not in outputs:
                    raise self.ValidationError(f"缺少输出参数: {param_name}。")
                # 校验参数类型是否合法
                self.validate_param_type(param_name,output['type'],outputs[param_name])
                # 将输出放入类内存变量中
                self.parameters[output['name']] = outputs[param_name]

    def _execute(self,inputs):
        return {}