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
from typing import Union, Dict, Literal, List
from undetected_chromedriver import Chrome as unChrome

request = Request()
common = Common()
executeService = ExecuteService()
taskRequest = TaskRequest()

class ShopApi():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def getInfoAccountList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取当前店铺账号信息（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_session/"
        res = executeService.request(driver=driver, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取当前店铺账号信息', res)
        return res

    def getShopOrHaveHoliday(self, driver: unChrome, options: dict):
        '''
        @Desc    : 获取当前店铺是否已休假（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        休假状态的店铺无法获取 广告费和充值记录
        '''
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2"
        }
        url = "https://seller.shopee.cn/api/selleraccount/user_info/"
        res = executeService.request(driver=driver, params=params, url=url, method="GET")
        res = json.loads(res)
        holiday_mode_on: bool = res['data']['holiday_mode_on']
        common.print_('获取当前店铺是否已休假', res)
        # Ture 已休假  False 未休假
        return holiday_mode_on


    def getInfoList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取当前店铺信息（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2"
        }
        url = f"https://seller.shopee.cn/api/cnsc/selleraccount/get_or_set_shop/"
        res = executeService.request(driver=driver, url=url, params=params, data={}, method="POST")
        res = json.loads(res)
        common.print_('获取当前店铺信息', res)
        return res

    def queryShopExistCurrentCompany(self, driver: unChrome, options: dict) -> Union[bool, str]:
        '''
        @Desc    : 查询当前 shop_id 是否存在于当前公司（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_or_set_shop/"
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2"
        }
        data = {
            "cnsc_shop_id": int(options['shop_id'])
        }
        res = executeService.request(driver=driver, params=params, url=url, data=data, method="POST")
        res = json.loads(res)
        common.print_('查询当前 shop_id 是否存在于当前公司', res)
        debug_msg = True  # 此 shop_id 存在与当前公司
        if res.get('code') != 0:
            debug_msg = res.get('err_detail') or res.get('debug_message') or '[查询失败]查询当前 shop_id 是否存在于当前公司（非本土）'
        return debug_msg

    def getAllShopList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取当前公司所有店铺信息（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        headers = {
            "accept": "application/json, text/plain, */*"
        }
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_merchant_shop_list/"
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2",
            "page_index": "1",
            "page_size": "50",
            "auth_codes": "\\[\"access_my_income\"\\]",
            "feature_keys": "\\[\\]",
            "show_tags": "\\[\\]"
        }
        res = executeService.request(driver=driver, headers=headers, params=params, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取当前公司所有店铺信息', res)
        return res

    def getMerchantList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取所有公司信息merchant_id（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        headers = {
            "accept": "application/json, text/plain, */*"
        }
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2",
            "page_index": "1",
            "page_size": "500",
            "merchant_name": ""
        }
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_merchant_list/"
        res = executeService.request(driver=driver, params=params, headers=headers, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取所有公司信息merchant_id', res)
        return res
