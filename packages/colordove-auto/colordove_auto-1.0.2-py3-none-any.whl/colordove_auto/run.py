# -*- coding: utf-8 -*-

import sys
import subprocess
import sys
from pathlib import Path
from common.Common import Common

common = Common()

def main():
    '''
    @Desc    : 入口
    @Author  : 钟水洲
    @Time    : 2024/05/31 10:01:57
    '''
    # 检查环境
    check_env()

    args = common.handleArgs(sys.argv)

    # 解析命令行参数
    module_name = f"command.{args.f}.{args.m}"

    class_name = args.m.capitalize()
    method_name = args.a

    # 导入模块
    __import__(module_name)

    # 获取类和方法
    module = sys.modules[module_name]
    Bot = getattr(module, class_name)()
    method = getattr(Bot, method_name)

    # 调用方法
    method(args.options)

def check_env():
    '''
    @Desc    : 检查环境，确保虚拟环境存在，不存在则创建
    @Author  : 钟水洲
    @Time    : 2024/05/31 10:01:57
    '''
    # 确定虚拟环境目录（当前文件所在目录）
    current_file_dir = Path(__file__).resolve().parent
    venv_dir = current_file_dir / '.venv'

    # 检查操作系统类型，确定激活脚本路径
    if sys.platform.startswith('win'):
        activate_script = venv_dir / 'Scripts' / 'activate.bat'
        python_bin = venv_dir / 'Scripts' / 'python.exe'
        pip_bin = venv_dir / 'Scripts' / 'pip.exe'
    else:
        activate_script = venv_dir / 'bin' / 'activate'
        python_bin = venv_dir / 'bin' / 'python'
        pip_bin = venv_dir / 'bin' / 'pip'

    # 检查虚拟环境是否存在
    if not venv_dir.exists() or not activate_script.exists():
        print("未检测到虚拟环境，正在创建...")
        try:
            # 创建虚拟环境
            subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
            print(f"虚拟环境已创建: {venv_dir}")
            print("请激活虚拟环境后重新运行:")
            if sys.platform.startswith('win'):
                print(f"  .\\.venv\\Scripts\\activate")
            else:
                print(f"  source ./.venv/bin/activate")
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print(f"创建虚拟环境失败: {e}")
            sys.exit(1)

    print("虚拟环境已存在且可用")

if __name__ == "__main__":
    main()