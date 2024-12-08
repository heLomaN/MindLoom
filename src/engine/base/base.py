# src/engine/base/base.py

from abc import ABC, abstractmethod
from engine.base.template_loader import TemplateLoader

# 定义基础类
class Base:
    # 定义模版校验错误的类
    class TemplateError(Exception):
        def __init__(self, errors):
            super().__init__("Template 格式校验失败：")
            self.errors = errors
    # 定义值校验错误类
    class ParameterError(Exception):
        def __init__(self, errors):
            super().__init__("参数格式校验失败：")
            self.errors = errors

    # 定义参数类型种类
    PARAMETER_TYPE = ['string',' number','bool','array','object','vector']
    
    # 定义提示模版
    template = {}

    # 动态存储参数的字典
    parameters = {}

    #构造函数加载模板和校验模板
    def __init__(self, id, secret):
        self.id = id
        self.secret = secret

        # 获取当前类名作为class_name
        class_name = self.__class__.__name__
        # 转换成小写，因为文件名和mongoDB默认用小写标记类
        class_name = class_name.lower()

        try:
            # 读取模板
            template = TemplateLoader.load_template(class_name,id)
            # 校验模板是否合法
            self.template = self.validate_template(template)
    
        except FileNotFoundError as fnf_error:
            # 模板未找到，抛出更明确的异常信息
            raise ValueError(f"无法初始化实例：模板未找到 (id={self.id})。") from fnf_error

        except self.TemplateError as te:
            # 模板校验失败，抛出更明确的异常信息
            raise ValueError(f"无法初始化实例：模板格式校验失败 (id={self.id})，错误信息: {te.errors}") from te
        
        except ValueError as ve:
            # 捕获其他潜在的 ValueError
            raise ValueError(f"无法初始化实例：无效的值 (id={self.id})。") from ve

        except Exception as e:
            # 捕获所有其他异常，抛出 RuntimeError 以提供详细的上下文
            raise RuntimeError(f"实例初始化时发生未知错误 (id={self.id})。") from e


    # 获取提示模板
    def get_template(self):
        return self.template

    # 校验提示模板是否合法
    @classmethod
    def validate_template(cls,template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 检查 template 是否存在且为字典
        if not template:
            errors.append("模板不能为空。")
        elif not isinstance(template, dict):
            errors.append("模板必须是一个字典。")
        
        # 如果 template 通过初步检查，开始逐个字段校验
        if not errors:
            # 检查必须的参数 name, description, inputs, outputs 是否在 template 中
            required_keys = ["name", "description", "inputs", "outputs"]
            for key in required_keys:
                if key not in template:
                    errors.append(f"模板必须包含 '{key}'。")
                else:
                    validated_template[key] = template[key]  # 将字段添加到验证通过的字典

            # 如果 `inputs` 和 `outputs` 存在，检查它们的合法性
            for key in ["inputs", "outputs"]:
                if key in validated_template:
                    value = template[key]
                    
                    # 确保值是列表或 None
                    if value is not None and not isinstance(value, list):
                        errors.append(f"'{key}' 必须是一个列表或 null。")
                    elif isinstance(value, list):
                        validated_items = []
                        for item in value:
                            # 检查每个元素必须是字典
                            if not isinstance(item, dict):
                                errors.append(f"'{key}' 中的每个元素必须是一个字典。")
                                continue
                            
                            # 检查字典中必须包含的元素
                            item_errors = []
                            required_item_keys = ["name", "description", "type"]
                            validated_item = {}
                            for item_key in required_item_keys:
                                if item_key not in item:
                                    item_errors.append(f"'{item_key}' 在 '{key}' 中的每个元素中必须存在。")
                                else:
                                    validated_item[item_key] = item[item_key]  # 添加字段

                            # 检查 `type` 的合法性
                            if "type" in validated_item:
                                type_name = validated_item["type"]
                                if type_name not in cls.PARAMETER_TYPE:
                                    param_name = validated_item.get("name", "<unknown>")
                                    item_errors.append(f"'{key}' 中的 '{param_name}' 的 'type' 无效：'{type_name}'。")

                            # 如果该元素无错误，添加到 validated_items，否则记录错误
                            if not item_errors:
                                validated_items.append(validated_item)
                            else:
                                errors.extend(item_errors)
                        
                        # 如果整个列表无错误，将验证后的列表添加到 validated_template
                        if not errors:
                            validated_template[key] = validated_items

        # 如果有错误，抛出 TemplateError 并包含所有错误信息
        if errors:
            raise cls.TemplateError(errors)

        # 返回经过验证的模板
        return validated_template

    # 参数类型合法校验
    @staticmethod
    def validate_param_type(param_name,param_type,param_value):
        # 类型检查
        if param_type == 'string':
            if not isinstance(param_value, str):
                raise self.ValidationError(f"参数 {param_name} 应该是字符串。")
        elif param_type == 'array':
            if not isinstance(param_value, list) or not all(isinstance(item, str) for item in param_value):
                raise self.ValidationError(f"参数 {param_name} 应该是一个字符串列表。")

    # 校验输入参数是否合法
    def validate_inputs(self, inputs):
        for template_input in self.template["inputs"]:
            param_name = template_input["name"]
            param_type = template_input["type"]
        
            # 检查提示模板定义的参数是否被传入
            if param_name not in inputs:
                raise self.ValidationError(f"缺少参数: {param_name}。")
            
            # 校验参数的类型
            self.validate_param_type(param_name,param_type,inputs[param_name])

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

    # 必须重载的run函数
    @abstractmethod
    def run(self, instance_id, inputs):
        self.instance_id = instance_id
        return {}