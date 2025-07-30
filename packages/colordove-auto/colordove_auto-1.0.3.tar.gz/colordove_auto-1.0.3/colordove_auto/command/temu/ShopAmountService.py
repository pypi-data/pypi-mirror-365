import json
import time
import uuid
import undetected_chromedriver
from common.Common import Common
from common.api.temu.ShopApi import ShopApi
from common.api.temu.ShopAmountApi import ShopAmountApi
from common.library.Request import Request
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.request.common.TaskRequest import TaskRequest
from common.service.TemuService import TemuService

# 公共服务
common = Common()
# 店铺服务
shopRequest = ShopRequest()
# 任务服务
taskRequest = TaskRequest()
# temu服务
temuService = TemuService()
# 店铺api
shopApi = ShopApi()
# api
shopAmountApi = ShopAmountApi()
# 请求服务
request = Request()

class ShopAmountService():
    
    def shop_amount(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 资金申报 
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """
        print("资金申报")
        # 主账号登录
        temuService.login(driver, shop_data, options)
        
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        
        res = shopAmountApi.getAayment(driver, options)
        
        if 'success' not in res or not res['success']:
            raise ValueError(f"资金申报获取失败 - {res}")

        data = {
            **data,
            "response":json.dumps(res,ensure_ascii=False),
        }
        # 保存数据
        taskRequest.save(data)
        
        print("资金申报结束")

