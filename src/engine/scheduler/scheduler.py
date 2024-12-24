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
        'process': None, # 该值是Process
        'tool': Tool
    }

    # 动态存储参数的字典
    parameters = {}

    # 构造函数直接调用父类的构造函数加载模板和校验模板
    def __init__(self, id, secret):
        super().__init__(id, secret)

############## 运行时相关逻辑 ##############

    # 重写执行方法，调度器特殊执行逻辑，需要把输入参数放入变量空间，最后输出再从变量空间取出
    def _execute(self,inputs):
        self.set_parameters_by_inputs(inputs)
        self._process_execute()
        outputs = self.get_outputs_by_parameters()
        return outputs

    # 子类实现的具体执行逻辑
    def _process_execute():
        pass

############## 提示模板相关逻辑 ##############

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
        if 'execution' in template and template['execution'] != None:
            try:
                validated_template['execution'] = cls.validate_template_execution(template['execution'])
            except Scheduler.TemplateError as e:
                error_messages = '\n'.join(str(error) for error in e.errors)
                errors.append(f"'execution' 字段存在错误：{error_messages}")
        else:
            errors.append(f"{class_name} 模板中必须包含 'execution' 字段。")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

############## 提示模板校验相关函数 ##############

    # 需要Process和Task重写具体校验execution模板
    @staticmethod
    def validate_template_execution(execution):
        return {}

    # 校验 call 结构模板，提供给Task和Process调用
    @staticmethod
    def validate_template_call(call_dict):
        errors = []  # 用于记录所有校验错误
        validated_call = {}  # 用于存储验证通过的字段

        if not isinstance(call_dict, dict):
            errors.append("'call' 字段必须是一个结构对象。")
            raise Scheduler.TemplateError(errors)

        # 校验class段必须存在且是流程、操作、生成内容或者工具
        if "class" not in call_dict:
            errors.append("'call' 必须包含 'class' 字段。")
        elif call_dict["class"] is None or not isinstance(call_dict["class"], str):
            errors.append("'call' -> 'class' 必须是有效的字符串类型。")
        elif call_dict["class"] not in Scheduler.EXECUTION_CLASS_MAPPING:
            errors.append("'call' -> 'class' 必须是 action，generator，process 或者 tool。")
        else:
            validated_call["class"] = call_dict["class"]

        # 检查 "id" 值是否合法，这里不会查询其是否存在
        if "id" not in call_dict:
            errors.append("'call' 必须包含 'id' 字段。")
        if call_dict["id"] is None or not isinstance(call_dict["id"], str):
            errors.append("'call' -> 'id' 必须是有效的字符串类型。")
        else:
            validated_call["id"] = call_dict["id"]

        # 检查call输入参数是否合法
        try:
            if "inputs" in call_dict and call_dict["inputs"] != None:
                validated_call["inputs"] = Scheduler.validate_template_call_params(call_dict["inputs"],"input")
            else: 
                errors.append("'call' 必须包含 'inputs' 字段。")
        except Scheduler.TemplateError as e:
            error_messages = '\n'.join(f'{e}' for e in e.errors)
            errors.append(f"'call' -> 'inputs' 字段存在错误：{error_messages}")

        # 检查call输出参数是否合法
        try:
            if "outputs" in call_dict and call_dict["outputs"] != None:
                validated_call["outputs"] = Scheduler.validate_template_call_params(call_dict["outputs"],"output")
            else: 
                errors.append("'call' 必须包含 'outputs' 字段。")
        except Scheduler.TemplateError as e:
            error_messages = '\n'.join(f'{e}' for e in e.errors)
            errors.append(f"'call' -> 'outputs' 字段存在错误：{error_messages}")

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise Scheduler.TemplateError(errors)

        # 返回经过验证的模板
        return validated_call 

    # 校验参数列表
    @staticmethod
    def validate_template_call_params(params, transfer_direction):
        errors = [] # 用于记录所有校验错误
        validated_params = [] # 用于存储验证通过的字段

        # 首先检查是否是字典，不是则直接返回报错
        if not isinstance(params, list):
            errors.append("该值必须是一个参数列表。")
            raise Scheduler.TemplateError(errors)

        # 循环校验每个参数
        for item in params:
            try:
                validated_params.append(Scheduler.validate_template_call_params_item(item,transfer_direction))
            except Scheduler.TemplateError as e:
                errors.extend(e.errors)

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Scheduler.TemplateError(errors)

        return validated_params

    # 校验参数内容
    @staticmethod
    def validate_template_call_params_item(item, transfer_direction):
        errors = [] # 用于记录所有校验错误
        validated_item = {} # 用于记录所有校验错误

        if not isinstance(item, dict):
            errors.append("参数必须是一个结构对象。")
            raise Scheduler.TemplateError(errors)

        # 检查 "name" 值是否存在且合法
        if "name" not in item:
            errors.append("参数必须包含 'name' 字段。")
        if item["name"] is None or not isinstance(item["name"], str):
            errors.append("参数 'name' 字段必须是有效的字符串类型。")
        else:
            validated_item["name"] = item["name"]

        # 保存参数名字，用于打印错误日志
        param_name = validated_item.get("name", "<unknown>")

        # 校验type段必须存在且是流程、操作、生成内容或者工具
        if "type" not in item:
            errors.append(f"'{param_name}' 参数必须包含 'type' 字段。")
        elif item["type"] is None or not isinstance(item["type"], str):
            errors.append("'call' -> 'type' 必须是有效的字符串类型。")
        elif item["type"] not in Scheduler.PARAMETER_TYPE:
            base_types = ', '.join(f'{t}' for t in Base.PARAMETER_TYPE)
            errors.append(f"'{param_name}' 参数的 'type' 必须是 {base_types} 的一种。")
        else:
            validated_item["type"] = item["type"]

        # 获取定义的值
        item_type = validated_item.get("type","string")

        # 校验输入参数必须存在source或者value并且合法
        if transfer_direction == "input":
            if "value" in item and item["value"] != None:
                try:
                    validated_item["value"] = Scheduler.validate_value_type(item["value"],item_type)
                except Scheduler.TemplateError as e:
                    error_messages = '\n'.join(str(error) for error in e.errors)
                    errors.append(f"'{param_name}' 参数的 'value' 错误：{error_messages}")
            elif "source" in item and item["source"] != None:
                if not isinstance(item["source"], str):
                    errors.append(f"'inputs' 中的 '{param_name}' 的 'source' 必须是一个字符串。")
                else:
                    validated_item["source"] = item["source"]
            else:
                errors.append(f"'inputs' 中的 '{param_name}' 中必须包含 'source' 或 'value'。")

        # 校验输出参数必须存在target并且合法
        if transfer_direction == "output":
            if "target" not in item and item["target"] != None:
                errors.append(f"'outputs' 中的 '{param_name}' 中必须包含  'target'。")
            else:
                if not isinstance(item["target"], str):
                    errors.append(f"'outputs' 中的 '{param_name}' 的 'target' 必须是一个字符串。")
                else:
                    validated_item["target"] = item["target"]

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise Scheduler.TemplateError(errors)

        return validated_item

############## 运行时参数内存空间管理 ##############

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
                raise self.ParameterError(f"缺少输出参数: {param_name}。")
            outputs[param_name] = self.parameters[param_name]
        return outputs

############## 运行时处理逻辑 ##############

    # 执行一次嵌套调用
    def _call_execute(self, call_dict):
        # 根据class字段名，获取类定义
        call_class = self.EXECUTION_CLASS_MAPPING[call_dict['class']]
        # 直接新实例化一个对应类的对象！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        call = call_class(call_dict['id'], secret = None)

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
                        raise self.ParameterError(f"缺少输入参数: {param_name}。")
                    # 校验参数类型是否合法
                    Scheduler.validate_value_type(self.parameters[param_name],input['type'])
                    # 给需要传入的参数赋值
                    inputs[input['name']] = self.parameters[param_name]

        # 执行一次call，获取outputs！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        outputs = call.run(inputs)

        # 将call调用返回的outputs放置到类内存空间的变量中
        if call_dict['outputs'] == None:
            pass
        else:
            for output in call_dict['outputs']:
                param_name = output['name']
                # 校验需要的输出参数是否存在
                if param_name not in outputs:
                    raise self.ParameterError(f"缺少输出参数: {param_name}。")
                # 校验参数类型是否合法
                Scheduler.validate_value_type(outputs[param_name],output['type'])
                # 将输出放入类内存变量中
                self.parameters[output['target']] = outputs[param_name]

