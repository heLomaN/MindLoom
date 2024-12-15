# src/engine/base/template_loader.py

import os
import json

# 从配置文件获取提示模板读入的方式
from config import TEMPLATE_LOAD_METHOD
if TEMPLATE_LOAD_METHOD == 'mongodb':
    from services.mongodb.mongodb import mongo_db
elif TEMPLATE_LOAD_METHOD == 'file':
    from config import TEMPLATE_FILE_PATH

class TemplateLoader:
    # 从本地文件读取提示模板方法
    @staticmethod
    def load_template_by_file(folder_name, template_id):
        # 生成完整文件夹路径名字
        folder_path = os.path.join(TEMPLATE_FILE_PATH, folder_name)

        # 确认文件夹路径存在
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹 {folder_path} 不存在。")
        
        try:
            # 查找匹配的文件
            for filename in os.listdir(folder_path):
                if filename.startswith(template_id):
                    file_path = os.path.join(folder_path, filename)
                    # 读取文件内json内容
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                        data_dict = json.loads(file_content)
                        return data_dict
            # 未找到符合id的文件，抛出文件未找到异常
            raise FileNotFoundError(f"在文件夹 {folder_path} 中没有找到template_id为 {template_id} 的文件。")
        
        except json.JSONDecodeError as e:
            # 处理JSON解码错误，提供详细的错误信息
            raise ValueError(f"文件 {file_path} 中的JSON格式无效。") from e
        
        except Exception as e:
            # 捕获其他异常并提供上下文信息
            raise RuntimeError(f"读取文件夹 {folder_path} 中的文件时发生异常，folder_name={folder_name}, id={id}。") from e

    # 从mongoDB读取提示模板方法
    @staticmethod
    def load_template_by_mongodb(db_name, object_id):
        try:
            # 使用实例化的MongoDB类的find_data方法查找数据
            data_dict = mongo_db.find_one(db_name, {'_id': object_id})
            if not data_dict:
                raise FileNotFoundError(f"MongoDB没有找到id为 {object_id} 的数据。")
            return data_dict
        except FileNotFoundError as e:
            # 文件未找到的特殊处理
            raise e
        except Exception as e:
            # 其他异常的处理，增加上下文信息
            raise RuntimeError(f"加载MongoDB数据时发生异常，db_name={db_name}, object_id={object_id}。") from e

    @staticmethod
    def load_tools_template(tool_id):
        pass


    # 读取提示模板函数
    @staticmethod
    def load_template(class_name, template_id):
        # 如果是工具类直接返回引擎内模板
        if class_name == 'tool':
            return load_tools_template(template_id)

        # 如果是任务、流程、操作或AI生成类则根据配置文件加载模板
        try:
            # 从本地文件夹读取模板
            if TEMPLATE_LOAD_METHOD == 'file':
                return TemplateLoader.load_template_by_file(class_name, template_id)
            
            # 从MongoDB中读取模板
            elif TEMPLATE_LOAD_METHOD == 'mongodb':
                return TemplateLoader.load_template_by_mongodb(class_name, template_id)
            
            else:
                # 如果加载方法配置无效，抛出异常
                raise ValueError(f"无效的模版加载类型: {TEMPLATE_LOAD_METHOD}，请检查配置文件 prompts->default_source 项。")
        
        except FileNotFoundError:
            # 如果模板未找到，重新抛出以供外部调用处理
            raise
        
        except ValueError:
            # 抛出配置错误的异常
            raise
        
        except Exception as e:
            # 抛出其他未预见的异常，保留原始异常上下文
            raise RuntimeError(f"加载模板时发生未知错误，class_name={class_name}, template_id={template_id}。") from e
