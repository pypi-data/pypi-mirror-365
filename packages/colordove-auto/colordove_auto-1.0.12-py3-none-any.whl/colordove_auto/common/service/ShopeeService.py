import json
import time
from urllib.parse import urlparse

from env import config
from common.library.Request import Request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.service.EmailService import EmailService
from common.api.shopee.ShopApi import ShopApi
from common.service.ExecuteService import ExecuteService
from exceptions import *
from undetected_chromedriver import Chrome as unChrome

request = Request()
common = Common()
chrome = Chrome()
executeService = ExecuteService()
shopApi = ShopApi()
shopRequest = ShopRequest()
emailService = EmailService()

class ShopeeService():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def login(self, driver: unChrome, data, options):
        '''
        @Desc    : 登录（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        storage_data = data.get("storage_data")
        time.sleep(1)
        # 如果 storage_data 存在，注入缓存
        if storage_data:
            print("🌐 使用缓存尝试自动登录")
            self.inject_storage(driver, storage_data)

        # 访问页面
        driver.get('https://seller.shopee.cn')
        time.sleep(4)
        wait = WebDriverWait(driver, 20)
        # 等待页面加载完成
        wait.until(EC.url_contains('shopee.cn'))
        # 获取登录信息
        res = shopApi.getInfoAccountList(driver, options)
        print("获取登录信息", res)
        if res.get('code', 1000) == 0:
            print("✅ 成功获取店铺信息，可能已登录")
            need_login = False
        else:
            print("🔒 可能未登录")
            print(res)
            need_login = True
        # 根据 need_login 决定是否执行登录逻辑
        if need_login:
            # 执行登录流程
            login_res = self.account_login(driver, data, options)
            # 登录失败
            if login_res['status'] == 0:
                return login_res
        else:
            # 已登录
            print("✅ 已登录")
        print("✅ 登录成功")

        return common.back(1, '登录成功')

    def account_login(self, driver: unChrome, data, options):
        '''
        @Desc    : 账号登录
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print("账号登录")

        shop_global_id = data.get("shop_global_id")
        login_name = data.get("login_name")
        password = data.get("password")

        # 访问页面
        # driver.get('https://seller.shopee.cn')
        wait = WebDriverWait(driver, 15)
        # 等待登陆页面加载完成
        wait.until(EC.url_contains('account/signin'))
        time.sleep(1)

        print("检查页面状态")
        if 'account/signin' not in driver.current_url:
            print('✅ 已不在登陆页 登陆成功')
            # 保存店铺缓存
            self.save_storage(driver, shop_global_id)
            return common.back(1, '登录成功')

        input_user = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')  # 账户输入框
        input_user.send_keys(login_name)
        print("✅ 账号已填写")
        time.sleep(1)

        input_password = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')  # 密码输入框
        input_password.send_keys(password)
        print("✅ 密码已填写")
        time.sleep(1)

        # 如果有记住密码的复选框，可以通过以下代码进行勾选：
        input_checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')  # 记住密码复选框
        if not input_checkbox.is_selected():
            # 使用 JavaScript 来点击复选框
            driver.execute_script("arguments[0].click();", input_checkbox)
            print("✅ 记住密码复选框已勾选")
            time.sleep(1)

        # 找到页面中的所有按钮
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        # 遍历按钮，查找第一个非空文本按钮并点击
        for button in buttons:
            if button.text.strip() != '':
                button.click()
                print("✅ 点击了登录按钮")
                break
        time.sleep(1)

        # 获取当前URL
        current_url = driver.current_url
        print('[当前url] --> ', current_url)

        print("等待15秒")
        time.sleep(15)

        print("检查页面状态")
        if 'account/signin' not in driver.current_url and "/verify/" not in driver.current_url:
            print('✅ 已不在登陆页 登陆成功')
            # 保存店铺缓存
            self.save_storage(driver, shop_global_id)
            return common.back(1, '登录成功')

        # 执行 JavaScript
        js_code = """
        const text_innerText = document.body.innerText;   // web文本内容 公用
        console.log("[定时器检测中][捕获错误] -> ",window.data_info_0x294312)
        const login_error = document.querySelector('.login-error') || document.querySelector('div[role="alert"]');     // 登录错误的异常信息
        const email_error = document.querySelector('.pov-modal__title');  // 邮箱验证码验证
        const email_url_verify = document.querySelector('button[aria-label="Verify by Email Link"]');  // 邮箱链接验证
        const email_url_verify_th = document.querySelector('button[aria-label="ยืนยันตัวตนผ่านลิงก์"], button[aria-label="ยืนยันตัวตนด้วยลิงก์ในอีเมล"]');    // 邮箱链接验证（泰国本土的）
        const email_url_sms_verify_th = document.body.innerText.includes("กรุณาตรวจสอบข้อความในโทรศัพท์ขอ");    // SMS手机验证（泰国本土的）
        if (window.location.href.includes("/verify/") && (email_url_verify || email_url_verify_th)){
            return '邮箱链接验证';
        } else if (window.location.href.includes("/verify/") && email_url_sms_verify_th){
            return 'SMS验证';
        } else if (window.location.href.includes("/verify/")){
            return '未知的验证页面';
        } else if (login_error) {
            return '[其他错误信息]' + login_error.textContent;
        } else if (document.querySelector('aside')) {
            return '人机验证';
        } else if (email_error) {
            return '邮箱验证码';
        } else {
            return '未知错误';
        }
        """

        # 运行 JavaScript 并获取返回的结果
        result = driver.execute_script(js_code)
        # 输出结果
        print("JavaScript 执行结果:", result)
        if result == '邮箱验证码':
            print("❗ [邮箱验证码验证]")
            raise LoginException('登录失败-[邮箱验证码验证]')
        elif result == '邮箱链接验证':
            print("❗ [邮箱链接验证]")
            raise LoginException('登录失败-[邮箱链接验证]')
        elif result == 'SMS验证':
            print("❗ [SMS验证]")
            raise LoginException('登录失败-[SMS验证]')
        elif result == '未知的验证页面':
            print("❗ [未知的验证页面]")
            raise LoginException('登录失败-[未知的验证页面]')
        elif result == '人机验证':
            print("❗ [人机验证]")
            raise LoginException('登录失败-[人机验证]')
        elif result == '未知错误':
            print("❗ [未知错误]")
            raise LoginException('登录失败-[未知错误]')
        else:
            print(f"❗ {result}")
            raise LoginException(f'登录失败-[{result}]')

    def inject_storage(self, driver: unChrome, storage_data):
        '''
        @Desc    : 注入缓存
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        try:
            cookies = storage_data.get("cookies")

            driver.execute_cdp_cmd("Network.enable", {})
            for cookie in cookies:
                try:
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False),
                        "sameSite": cookie.get("sameSite", "None")
                    })
                except Exception as e:
                    print(f"⚠️ CDP 注入 cookie 失败：{cookie}, 错误：{e}")
        except Exception as e:
            print(f"⚠️ 缓存登录失败: {e}")
        print("注入缓存成功")

    def save_storage(self, driver: unChrome, shop_global_id):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取 cookies
        print("获取 cookies")
        cookies = driver.get_cookies()

        storage_data = {
            "shop_global_id": shop_global_id,
            "cookies": json.dumps(cookies)
        }

        # 保存店铺缓存
        print("保存店铺缓存")
        res = shopRequest.saveStorage(storage_data)
        if res['code'] != 1:
            print("保存缓存成功")
            return common.back(0, res['msg'])

        print("保存缓存成功")

    def switch_store(self, driver: unChrome, options) -> dict:
        """
        @Desc     : shopee切换商家
        @Author   : 祁国庆
        @Time     : 2025/05/26 10:51:43
        @Params   :
            - merchant_id: 公司id (非shop_id)
            - shop_id: 店铺id (shop_id)
        @Returns  : 正常返回字典数据，也会返回当前店铺商家的信息
        """
        # 账号-》公司-》店铺    三层
        print(f"——————————————————【shopee切换公司和店铺】")
        merchant_id = str(options.get('merchant_id'))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id'))  # 店铺id
        site = str(options.get('site'))
        if not all(v is not None and v != '' for v in
                   [merchant_id, shop_id, site]):
            raise TaskParamsException("缺少必要参数 merchant_id, shop_id, site")

        # 获取获取当前店铺信息
        at_shop_data: dict = shopApi.getInfoList(driver, options)
        if at_shop_data.get('code') != 0:
            raise UnknownException(f"当前店铺商家信息-请求失败")
        # ——————将当前店铺数据和所有店铺数据打包进行返回
        shop_all = {'at': at_shop_data}
        if merchant_id == str(at_shop_data['merchant_id']) and shop_id == str(at_shop_data['shop_id']):
            return {"status": 1, "message": "无需切换", 'data': shop_all}

        # 公司id 一致则无需切换公司 直接切换店铺即可
        if merchant_id != str(at_shop_data.get('merchant_id')):
            # ——————————————————发起请求，获取新公司的cookie信息，即可自动切换页面
            data = {
                "merchant_id": int(merchant_id)
            }
            headers = {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json;charset=UTF-8"
              }
            url = f"https://seller.shopee.cn/api/cnsc/selleraccount/switch_merchant/?SPC_CDS=--&SPC_CDS_VER=2&cnsc_shop_id={shop_id}&cbsc_shop_region={site.lower()}"
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            res = json.loads(res)
            common.print_('获取新公司的cookie信息-请求', res)
            if res.get('code') != 0:
                raise UnknownException(f"获取新公司的cookie信息-请求失败")
        # 查询 shop_id 是否存在于当前公司内
        queryShopExistCurrentCompany = shopApi.queryShopExistCurrentCompany(driver, options)
        if queryShopExistCurrentCompany != True:
            raise UnknownException(queryShopExistCurrentCompany)

        driver.get(f'https://seller.shopee.cn/?cnsc_shop_id={shop_id}')
        time.sleep(8)
        _ = self.switch_store(driver, options)
        _['message'] = '切换完成'
        return _

