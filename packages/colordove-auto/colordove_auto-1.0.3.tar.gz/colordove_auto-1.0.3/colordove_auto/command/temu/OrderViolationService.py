import json
import time
import uuid
import undetected_chromedriver
from common.Common import Common
from common.api.temu.ShopApi import ShopApi
from common.api.temu.ViolationApi import ViolationApi
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
violationApi = ViolationApi()
# 请求服务
request = Request()

class OrderViolationService():
    def __init__(self):
        pass

    def order_violation(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 订单违规 列表
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """        
        print("订单违规列表")
        # 主账号登录
        temuService.login(driver, shop_data, options)
        # 站点登录
        temuService.authorize(driver, options)
        
        # 测试固定时间
        if 'start_time' not in options and 'end_time' not in options:
            options['start_time'] = '2025-06-01'
            options['end_time'] = '2025-06-30'
        
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        options['pageNo'] = pageNo = 1
        options['pageSize'] = pageSize = 100
        options['targetType'] = 1
        while True:
            res = violationApi.getViolationList(driver, options)
            if 'success' not in res or not res['success']:
                raise ValueError(f"订单违规列表获取失败 - {res}")
                
            list_count = len(res['result']['pageData'] or [])
            total_count = res['result']['total']
            
            # 列表数量小于1
            if list_count < 1:
                # 当页面如果是第一页没有数据的话需要保存没有数据
                if pageNo == 1:
                    data = {
                        **data,
                        "response":json.dumps([],ensure_ascii=False),
                    }
                    # 保存数据
                    taskRequest.save(data)
                break
            
            print(f"当前第{pageNo}页,每页{pageSize} - 共{total_count}条数据")

            data = {
                **data,
                "response":json.dumps(res,ensure_ascii=False),
                "page_number":pageNo, # 页码
                "page_size":pageSize, # 每页数量
                "list_count":list_count, # 当前页数量
                "total_count":total_count # 总数量
            }
            # 保存数据
            taskRequest.save(data)
            
            # 下一页
            pageNo += 1
            options['pageNo'] = pageNo
        print("订单违规列表结束")
    
    def order_violation_detail(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 订单违规详情
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """        
        print("订单违规详情")
        # 主账号登录
        temuService.login(driver, shop_data, options)
        # 站点登录
        temuService.authorize(driver, options)
        
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        
        res = violationApi.getViolationDetail(driver, options)
        if 'success' not in res or not res['success']:
            raise ValueError(f"订单违规详情获取失败 - {res}")
        
        data = {
            **data,
            "response":json.dumps(res,ensure_ascii=False),
        }
        
        # 保存数据
        taskRequest.save(data)
        
        print("订单违规详情结束")