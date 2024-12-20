# src/engine/base/base.py

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
    PARAMETER_TYPE = ['string','number','bool','array','object','vector']
    
    # 定义提示模版
    template = {}

    #构造函数加载模板和校验模板
    def __init__(self, id, secret):
        self.id = id
        self.secret = secret

        # 获取当前类名作为class_name
        class_name = self.__class__.__name__
        # 转换成小写，因为文件名和mongoDB默认用小写标记类
        class_name = class_name.lower()

        template = TemplateLoader.load_template(class_name,id)
        
        self.template = self.validate_template(template)

############## 提示模板相关逻辑 ##############

    # 获取提示模板
    def get_template(self):
        return self.template

    # 校验模板是否合法
    @classmethod
    def validate_template(cls, template):
        errors = []  # 用于记录所有校验错误
        validated_template = {}  # 用于存储验证通过的字段

        # 首先检查是否是字典
        if not isinstance(template, dict):
            errors.append("模板必须是一个对象。")
            raise cls.TemplateError(errors)

                # 校验每个字段，并收集错误
        try:
            if "name" in template:
                validated_template["name"] = cls.validate_name(template["name"])
            else:
                errors.append("模板必须包含 'name' 字段。")
        except cls.TemplateError as e:
            errors.extend(e.errors)

        try:
            if "description" in template:
                validated_template["description"] = cls.validate_description(template["description"])
            else:
                errors.append("模板必须包含 'description' 字段。")
        except cls.TemplateError as e:
            errors.extend(e.errors)

        try:
            if "inputs" in template:
                validated_template["inputs"] = cls.validate_template_param(template["inputs"])
            else:
                errors.append("模板必须包含 'inputs' 字段。")
        except cls.TemplateError as e:
            errors.append("'inputs' 字段错误：")
            errors.extend(e.errors)

        try:
            if "outputs" in template:
                validated_template["outputs"] = cls.validate_template_param(template["outputs"])
            else:
                errors.append("模板必须包含 'outputs' 字段。")
        except cls.TemplateError as e:
            errors.append("'outputs' 字段错误：")
            errors.extend(e.errors)

        # 如果有任何错误，抛出 TemplateError 异常
        if errors:
            raise cls.TemplateError(errors)

        return validated_template

    # 校验name字段
    @staticmethod
    def validate_name(name):
        errors = []
        if not isinstance(name, str):
            errors.append("'name' 必须是一个字符串。")
        if errors:
            raise Base.TemplateError(errors)
        return name

    # 校验description字段
    @staticmethod
    def validate_description(description):
        errors = []
        if not isinstance(description, str):
            errors.append("'description' 必须是一个字符串。")
        if errors:
            raise Base.TemplateError(errors)
        return description

    # 校验参数列表
    @classmethod
    def validate_template_param(cls, param):
        errors = []
        if param is not None and not isinstance(param, list):
            errors.append("必须是一个列表或 null。")
            raise cls.TemplateError(errors)

        if isinstance(param, list):
            validated_items = []
            for item in param:
                try:
                    validated_items.append(cls.validate_param_item(item))
                except cls.TemplateError as e:
                    errors.extend(e.errors)

            if errors:
                raise cls.TemplateError(errors)

            return validated_items
        return []

    # 校验参数内容
    @classmethod
    def validate_param_item(cls, item):
        errors = []
        if not isinstance(item, dict):
            errors.append("每个元素必须是一个字典。")
            raise cls.TemplateError(errors)

        validated_item = {}

        # 校验每个字段
        try:
            if "name" in item:
                validated_item["name"] = cls.validate_name(item["name"])
            else:
                errors.append("参数 'name' 必须存在。")
        except cls.TemplateError as e:
            errors.append("参数 'name' 错误：")
            errors.extend(e.errors)

        try:
            if 'description' in item:
                validated_item["description"] = cls.validate_description(item["description"])
            else:
                errors.append("参数 'description' 必须存在。")
        except cls.TemplateError as e:
            param_name = validated_item.get("name", "<unknown>")
            errors.append(f"'{param_name}' 的 'description' 错误：")
            errors.extend(e.errors)

        try:
            if "type" in item:
                validated_item["type"] = cls.validate_type(item["type"])
            else:
                errors.append("参数 'type' 必须存在。")
        except cls.TemplateError as e:
            param_name = validated_item.get("name", "<unknown>")
            errors.append(f"'{param_name}' 的 'type' 错误：")
            errors.extend(e.errors)

        try:
            if "default" in item and "type" in item:
                item_type = item.get("type","string")
                validated_item["default"] = cls.validate_default(item["default"],item_type)
        except cls.TemplateError as e:
            param_name = validated_item.get("name", "<unknown>")
            errors.append(f"'{param_name}' 的 'default' 错误：")
            errors.extend(e.errors)

        if errors:
            raise cls.TemplateError(errors)

        return validated_item

    @staticmethod
    def validate_type(type_name):
        errors = []
        if not isinstance(type_name, str) or type_name not in Base.PARAMETER_TYPE:
            errors.append("'type' 必须是有效的类型值。")
        if errors:
            raise Base.TemplateError(errors)
        return type_name

    @staticmethod
    def validate_default(default,type_name):
        errors = []
        if type_name == 'string' and not isinstance(default, (int, float)):
            errors.append("'default' 必须是 string 类型。")
            raise Base.TemplateError(errors)
        elif type_name == 'number' and not isinstance(default, (int, float)):
            errors.append("'default' 必须是 number 类型。")
            raise Base.TemplateError(errors)
        elif type_name == 'bool' and not isinstance(default, bool):
            errors.append("'default' 必须是 bool 类型。")
            raise Base.TemplateError(errors)
        elif type_name == 'array' and not isinstance(default, list):
            errors.append("'default' 必须是 array 类型。")
            raise Base.TemplateError(errors)
        elif type_name == 'object' and not isinstance(default, dict):
            errors.append("'default' 必须是 object 类型。")
            raise Base.TemplateError(errors)
        elif type_name == 'vector':
            if not (isinstance(default, (list, tuple)) and all(isinstance(x, (int, float)) for x in value)):
                errors.append("'default' 必须是 vector 类型。")
                raise Base.TemplateError(errors)
        return default

############## 参数校验相关逻辑 ##############

    # 校验参数的具体类型
    def _validate_type(self, value, expected_type):
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'bool':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'vector':
            return isinstance(value, (list, tuple)) and all(isinstance(x, (int, float)) for x in value)
        return False

    # 通用参数校验方法
    def _validate_param(self, template_params, actual_params, param_type):
        errors = []
        validated_params = {}  # 存放校验过后的参数
        
        for param in template_params:
            name = param['name']
            expected_type = param['type']
            default_value = param.get('default', None)
            
            # 检查实际参数中是否有该字段
            if name in actual_params:
                value = actual_params[name]
            elif default_value is not None:
                value = default_value
            else:
                errors.append(f"{param_type}缺少参数: {name}")
                continue

            # 校验参数类型
            if not self._validate_type(value, expected_type):
                errors.append(f"{param_type}参数类型不匹配: {name} (期望 {expected_type}, 实际 {type(value).__name__})")
            else:
                # 参数校验通过，添加到 validated_params
                validated_params[name] = value
        
        if errors:
            raise self.ParameterError(errors)
        
        return validated_params  # 返回校验过后的参数字典

############## 执行相关逻辑 ##############

    # 运行的主体方法
    def run(self, inputs):
        # 获取合法输入如果没有输入需要模板填充默认值，并校验是否合法，合法继续，不合法报错
        validated_inputs = self._validate_param(self.template["inputs"], inputs, "输入")
        # 执行函数需要子类重载实现，根据输入获取输出
        outputs = self._execute(validated_inputs)
        # 根据返回的outputs判断是否有没生成的，再填充默认值，并校验是否合法，不合法报错，合法则返回。
        validated_outputs = self._validate_param(self.template["outputs"], outputs, "输出")
        return validated_outputs

    # 子类实现的具体执行逻辑
    def _execute(self,inputs):
        return {}