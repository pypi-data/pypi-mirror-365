import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.api.shopee.AdvertisementBillApi import AdvertisementBillApi
from common.request.common.ShopRequest import ShopRequest
from common.service.ShopeeService import ShopeeService
from common.request.common.TaskRequest import TaskRequest
from undetected_chromedriver import Chrome as unChrome

common = Common()
chrome = Chrome()
advertisementBillApi = AdvertisementBillApi()
shopRequest = ShopRequest()
ShopeeService = ShopeeService()
taskRequest = TaskRequest()

class AdsService():
    def __init__(self):
        super().__init__()

    def getAdsBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee广告费（非本土）
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

        # 获取shopee广告费（非本土）
        advertisementBillApi.getAdsBill(driver, options)

    def getAdsRechargeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee广告充值记录账单（非本土）
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

        # 获取shopee广告充值记录账单（非本土）
        advertisementBillApi.getAdsRechargeBill(driver, options)