import os
import sys

# 打印当前运行目录
current_directory = os.getcwd()
print(f"当前运行目录: {current_directory}")

# 设置 PYTHONPATH 环境变量
os.environ["PYTHONPATH"] = current_directory

# 确保模块路径更新
sys.path.insert(0, os.environ["PYTHONPATH"])

# 打印当前模块搜索路径
print("当前模块搜索路径:")
for path in sys.path:
    print(path)

import threading
import pytz
import chardet
import imaplib
import logging
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from email.header import decode_header
from bs4 import BeautifulSoup

from common.library.Queue import Queue
from common.library.Logger import Logger
from common.library.Env import Env

class Main():
    def __init__(self):
        super().__init__()

        # 初始化加载模块
        self.init_module()

        # 运行
        self.run()

    def run(self):
        '''
        @Desc    : 运行
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 日志
        Logger()

        # 环境
        Env()

        # 消费队列
        Queue()

    def init_module(self):
        '''
        @Desc    : 初始化加载模块
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 调用这些模块以防打包丢失
        _ = threading.Thread
        _ = uc.Chrome
        _ = webdriver.Chrome
        _ = WebDriverWait
        _ = By
        _ = EC.title_is
        _ = decode_header
        _ = BeautifulSoup
        _ = pytz.timezone
        _ = chardet.detect
        _ = imaplib.IMAP4

def main():
    try:
        # 启动程序
        Main()
    except Exception as e:
        print(f"error {e}")
        logging.error(f"程序发生错误: {e}", exc_info=True)

if __name__ == '__main__':
    main()