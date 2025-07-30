import json
import time
import uuid
import undetected_chromedriver
from common.Common import Common
from common.api.temu.ShopApi import ShopApi
from common.api.temu.ShopRefundLabelApi import ShopRefundLabelApi
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
shopRefundLabelApi = ShopRefundLabelApi()
# 请求服务
request = Request()

class ShopRefundLabelService:
    def __init__(self):
        pass
        
    def shop_refund_label(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 退货面单 
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """
        print("退货面单")
        # 主账号登录
        temuService.login(driver, shop_data, options)
        # 站点登录
        temuService.authorize(driver, options)
        
        # 请求ID
        request_id = str(uuid.uuid4())
        options['pageSize'] = page_size = 100
        page_number = 1
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        
        # 测试固定时间
        if 'start_time' not in options and 'end_time' not in options:
            options['start_time'] = '2025-06-01'
            options['end_time'] = '2025-06-30'

        
        while True:                
            
            # 获取退货面单列表
            res = shopRefundLabelApi.getList(driver, options)
            if 'success' not in res or not res['success']:
                raise ValueError(f"退货面单列表获取失败 - {res}")
            
            list_count = len(res['result']['list'])
            total_count = res['result']['total']
            
            # 列表数量小于1
            if list_count < 1:
                # 当页面如果是第一页没有数据的话需要保存没有数据
                if page_number == 1:
                    data = {
                        **data,
                        "response":json.dumps([],ensure_ascii=False),
                    }
                    # 保存数据
                    taskRequest.save(data)
                break
            
            options['scrollContextString'] = res['result']['scrollContextString']
                
            print(f"当前第{page_number}页,每页{page_size} - 共{total_count}条数据")
            
            data = {
                **data,
                "response":json.dumps(res,ensure_ascii=False),
                "page_number":page_number, # 页码
                "page_size":page_size, # 每页数量
                "list_count":list_count, # 当前页数量
                "total_count":total_count # 总数量
            }
            # 保存数据
            taskRequest.save(data)
            
            page_number += 1
            
        print("退货面单结束")
            
        
    