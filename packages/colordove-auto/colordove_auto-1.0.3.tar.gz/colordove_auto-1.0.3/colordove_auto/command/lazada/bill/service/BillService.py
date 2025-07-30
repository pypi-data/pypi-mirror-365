import json
from common.Common import Common
from common.api.lazada.PaymentBillApi import PaymentBillApi
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.service.LazadaService import LazadaService
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
paymentbillApi = PaymentBillApi()
shopRequest = ShopRequest()
lazadaService = LazadaService()
taskRequest = TaskRequest()

class BillService():
    def __init__(self):
        super().__init__()

    def getPaymentBillDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取打款账单
        @Author  : 洪润涛
        @Time    : 2024/07/15 14:20:33
        '''
        print('shop_data', shop_data)
        print('options', options)
        # 账号登录
        res = lazadaService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取打款账单
        paymentbillApi.payment_bill(driver, options)
