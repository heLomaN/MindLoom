# src/main.py

import sys
import os
import uuid
import json
import argparse

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.scheduler.task.task import Task
from engine.scheduler.process.process import Process
from engine.executor.action.action import Action
from engine.executor.generator.generator import Generator
from engine.executor.tool.tool import Tool
from engine.executor.tool.tool_manager import tool_manager as tm


# 根据 class_name 创建实例
def create_instance(class_name, id):
    if class_name == "task":
        return Task(id)
    elif class_name == "process":
        return Process(id)
    elif class_name == "action":
        return Action(id)
    elif class_name == "generator":
        return Generator(id)
    elif class_name == "tool":
        return Tool(id)
    else:
        print(f"不支持的类名: {class_name}")
        return None


def run(class_name, id, inputs):
    instance = create_instance(class_name, id)
    if not instance:
        return
    
    run_id = str(uuid.uuid4())  # 生成唯一的 run_id
    print(f"任务正在运行，run_id: {run_id}")
    
    try:
        inputs_dict = json.loads(inputs)
    except json.JSONDecodeError:
        print("无效的输入 JSON 格式。")
        return
    
    result = instance.run(inputs_dict, run_id)  # 执行任务
    print(result)  # 输出结果


def get_template(class_name, id):
    instance = create_instance(class_name, id)
    if not instance:
        return
    
    template = instance.get_template()
    print(json.dumps(template, indent=2, ensure_ascii=False))  # 以格式化的 JSON 字符串输出


def validate_template(class_name, template):
    try:
        template_dict = json.loads(template)

        # 映射类名到类
        class_mapping = {
            "task": Task,
            "process": Process,
            "action": Action,
            "generator": Generator,
            "tool": Tool
        }

        # 获取对应的类
        clazz = class_mapping.get(class_name)
        if not clazz:
            print(f"不支持的类名: {class_name}")
            return
        
        # 调用类的静态方法验证模板
        clazz.validate_template(template_dict)
        
        print("模板校验通过")

    except json.JSONDecodeError:
        print("无效的模板 JSON 格式。")
    
    except Exception as e:
        # 处理模板验证错误或者其他异常
        if isinstance(e, (Task.TemplateError, Process.TemplateError, Action.TemplateError, Generator.TemplateError, Tool.TemplateError)):
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        else:
            print(f"未知错误: {str(e)}")


def get_tools_template():
    # 获取工具的完整模板
    tools_template = tm.export_metadata()
    print(json.dumps(tools_template, indent=2, ensure_ascii=False))  # 格式化输出工具模板


def get_tools():
    # 获取工具的 ID 和描述列表
    tools_list = tm.list_tools()
    print(json.dumps(tools_list, indent=2, ensure_ascii=False))  # 格式化输出工具列表


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="执行各种任务")
    
    # 子命令选择
    subparsers = parser.add_subparsers(dest="command")
    
    # 添加运行任务的子命令
    run_parser = subparsers.add_parser("run", help="运行任务")
    run_parser.add_argument("--class-name", type=str, required=True, help="类名 (task, process, action, generator, tool)")
    run_parser.add_argument("--id", type=str, required=True, help="任务的 ID")
    run_parser.add_argument("--inputs", type=str, required=True, help="输入数据，JSON 格式的字符串")

    # 添加获取模板的子命令
    template_parser = subparsers.add_parser("get-template", help="获取任务模板")
    template_parser.add_argument("--class-name", type=str, required=True, help="类名 (task, process, action, generator, tool)")
    template_parser.add_argument("--id", type=str, required=True, help="任务的 ID")

    # 添加模板验证的子命令
    validate_parser = subparsers.add_parser("validate-template", help="验证模板")
    validate_parser.add_argument("--class-name", type=str, required=True, help="类名 (task, process, action, generator, tool)")
    validate_parser.add_argument("--template", type=str, required=True, help="模板数据，JSON 格式的字符串")
    
    # 添加获取工具模板的子命令
    tools_template_parser = subparsers.add_parser("get-tools-template", help="获取工具模板列表")

    # 添加获取工具元数据的子命令
    tools_parser = subparsers.add_parser("get-tools", help="获取工具 ID 和描述列表")

    # 解析命令行参数
    args = parser.parse_args()

    if args.command == "run":
        run(args.class_name, args.id, args.inputs)
    elif args.command == "get-template":
        get_template(args.class_name, args.id)
    elif args.command == "validate-template":
        validate_template(args.class_name, args.template)
    elif args.command == "get-tools-template":
        get_tools_template()
    elif args.command == "get-tools":
        get_tools()
    else:
        print("未知的命令。")
