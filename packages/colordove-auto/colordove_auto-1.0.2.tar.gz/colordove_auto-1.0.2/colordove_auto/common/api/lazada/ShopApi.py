import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from env import config
from common.library.Request import Request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from common.Common import Common
from common.service.ExecuteService import ExecuteService
from common.request.common.TaskRequest import TaskRequest
from exceptions import TaskParamsException

request = Request()
common = Common()
executeService = ExecuteService()
taskRequest = TaskRequest()

class ShopApi():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def getInfoList(self, driver, options):
        '''
        @Desc    : 获取店铺信息
        @Author  : 洪润涛
        @Time    : 2024/07/21 18:15:22
        '''
        # 获取用户信息
        url = 'https://gsp.lazada.com/api/account/manage/query.do?_timezone=-8&tab=account'
        driver.get(url)
        response = executeService.request(driver, url, method="GET")
        return response

