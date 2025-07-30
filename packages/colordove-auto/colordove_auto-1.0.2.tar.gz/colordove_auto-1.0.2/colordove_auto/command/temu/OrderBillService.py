import json
import time
import uuid
import undetected_chromedriver
from common.Common import Common
from common.api.temu.ShopApi import ShopApi
from common.api.temu.OrderBillApi import OrderBillApi
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
orderBillApi = OrderBillApi()
# 请求服务
request = Request()

class OrderBillService():
    def __init__(self):
        pass
    
    def order_bill(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 订单账单 
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """        
        print("订单账单")
        # 主账号登录
        temuService.login(driver, shop_data, options)
        # 站点登录
        temuService.authorize(driver, options)
        
        # 测试固定时间
        if 'start_time' not in options and 'end_time' not in options:
            options['start_time'] = '2025-06-01'
            options['end_time'] = '2025-06-30'
        
        # 导出账单
        res = orderBillApi.export(driver, options)
        if ('success' not in res or not res['success']) and res['errorMsg'] != "导出任务已存在, 请勿重复创建, 请前往【导出历史】查看":
            raise ValueError(f"导出账单表格失败 - {res}")
         
        time.sleep(1)
        # 获取账单列表
        res = orderBillApi.getList(driver, options)
        if 'success' not in res or not res['success']:
            raise ValueError(f"获取账单列表失败 - {res}")
        fileId = res['result']['merchantMerchantFileExportHistoryList'][0]['id']
        
        num = 0
        while True:
            if num > 10:
                raise ValueError(f"获取账单下载链接超时")
            time.sleep(1)
            # 获取账单下载链接
            res = orderBillApi.getDownloadLink(driver, options,fileId)
            if 'success' not in res or not res['success']:
                raise ValueError(f"获取账单下载链接失败 - {res}")
            
            if 'result' in res and 'fileUrl' in res['result']:
                break
            
            num += 1
            
        fileUrl = res['result']['fileUrl']
        
        print(f"账单下载链接：{fileUrl}")
        
        cookies = {item['name']:item['value'] for item in driver.get_cookies()}
        
        dataXlsx = request.downloadExcel(fileUrl,{"cookies": cookies})
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],
            "response":json.dumps(dataXlsx,ensure_ascii=False),
            "request_id":request_id
        }
        
        # 保存数据
        taskRequest.save(data)
        
        print("订单账单结束")
