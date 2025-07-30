import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.api.shopee.BillApi import BillApi
from common.request.common.ShopRequest import ShopRequest
from common.service.ShopeeService import ShopeeService
from common.request.common.TaskRequest import TaskRequest
from undetected_chromedriver import Chrome as unChrome

common = Common()
chrome = Chrome()
billApi = BillApi()
shopRequest = ShopRequest()
ShopeeService = ShopeeService()
taskRequest = TaskRequest()

class BillService():
    def __init__(self):
        super().__init__()

    def getPaymentBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('shop_data', shop_data)
        print('options', options)
        # 登录
        res = ShopeeService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取shopee账单（非本土）
        billApi.getNoNativeBill(driver, options)

    def getPaymentBillDetails(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单详情（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('shop_data', shop_data)
        print('options', options)
        # 登录
        res = ShopeeService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取shopee账单详情（非本土）
        billApi.getNoNativeBillDetails(driver, options)

    def getPaymentBillTime(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单时间（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('shop_data', shop_data)
        print('options', options)
        # 登录
        res = ShopeeService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取shopee账单时间（非本土）
        billApi.getNoNativeBillTime(driver, options)

    def getBillPdf(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee进账报表pdf并上传（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('shop_data', shop_data)
        print('options', options)
        # 登录
        res = ShopeeService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取shopee进账报表pdf并上传（非本土）
        billApi.getNoNativeBillPdf(driver, options)