import json
import time
import uuid
from env import config
from common.library.Request import Request
from common.Common import Common
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from common.service.ExecuteService import ExecuteService
from common.request.common.TaskRequest import TaskRequest
from exceptions import TaskParamsException
from common.service.LazadaService import LazadaService

request = Request()
common = Common()
executeService = ExecuteService()
taskRequest = TaskRequest()
lazadaService = LazadaService()


class EarnestAmountApi():
    def __init__(self):
        super().__init__()
        self.host = config['api']
        # 请求ID
        self.request_id = str(uuid.uuid4())

    def earnest_amount(self, driver, options):
        '''
        @Desc    : 获取资金申报-保证金
        @Author  : 洪润涛
        @Time    : 2024/07/24 11:50:37
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 获取保证金，只有非本土才有保证金，不是所有非本土都有保证金
        print('-----------------开始获取资金申报【保证金】数据')
        load_data = {"_timezone": -8}
        # 接口api
        api = 'mtop.lazada.onboard.cb.deposit.getDepositDetail'
        # 获取sign_data
        sign_data = lazadaService.get_sign(driver, load_data,g='4272')
        # 获取params 保证金站点固定为MY
        params = lazadaService.get_params(sign_data=sign_data, site='MY', api=api)
        # 请求 URL
        url = f'https://acs-gsp-my.lazada.com/h5/{api}/1.0/?' + common.object_to_params(params)
        # 发送请求
        response = executeService.request(driver, url, method='GET')
        print('********请求【保证金】得到的数据：', type(response), response)
        # 数据格式转换
        if isinstance(response, (dict, list)):
            response = json.dumps(response, ensure_ascii=False)
        # 保存数据
        options['request_id'] = str(uuid.uuid4())
        options['response'] = response
        taskRequest.save(options)
