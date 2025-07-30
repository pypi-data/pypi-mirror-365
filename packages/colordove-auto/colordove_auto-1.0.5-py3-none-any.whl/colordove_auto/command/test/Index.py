# -*- coding: utf-8 -*-
import time
import json
import gc
import tempfile
import threading
from env import config
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.request.common.TaskRequest import TaskRequest
from exceptions import TimeoutException

common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
taskRequest = TaskRequest()

class Index:
    def __init__(self):
        super().__init__()

        # 记录开始时间
        self.start_time = time.time()

        self.driver = None
        self.mitmdump = None
        self.tmpdir = None
        self.stop_event = None
        self.monitor_thread = None
        self.timeout_seconds = 300  # ⏱ 任务最大运行时长

        self.options = None
        self.default_params = None

    def index(self, options):
        '''
        @Desc    : 测试
        @command : python run.py test -m Index -a index debug=1
        @Author  : 钟水洲
        @Time    : 2024/06/04 15:55:13
        '''
        debug = options['debug']

        self.options = {"task_job":"command.tiktok.product.service.OptimizerService@getOptimizerTitle","params":"{\"type_id\":7,\"task_id\":49800,\"shop_global_id\":4,\"shop_id\":17}"}

        try:
<<<<<<< HEAD
            # 使用线程控制超时
            thread = ExceptionThread(target=self.task_main)
            thread.start()
            thread.join(self.timeout_seconds)
=======
            # 关闭超时进程
            chrome.closeTimeoutProcess()

            options = {"task_job":"command.tiktok.union.service.UnionService@getOpenCollaboration","params":"{\"type_id\":42,\"task_id\":50440,\"shop_global_id\":1,\"shop_id\":4}"}
>>>>>>> 8ac52ce02c8d59b76b4011f6b7cbde9d520242ba

            if thread.is_alive():
                raise TimeoutException(f"任务超时,超过{self.timeout_seconds}秒")
            elif thread.exception:  # 检查线程内部异常
                raise thread.exception  # 重新抛出子线程异常

        except Exception as e:
<<<<<<< HEAD
            # 调试：抛出异常
            if debug == 1:
                raise

=======
            exc_type, exc_obj, tb = sys.exc_info()  # 解包

            # 获取完整 traceback 栈
            tb_list = traceback.extract_tb(tb)

>>>>>>> 8ac52ce02c8d59b76b4011f6b7cbde9d520242ba
            # 失败信息
            try:
                error_data = e.error_data()
            except Exception:
<<<<<<< HEAD
                error_data = {
                    "error_code": "99999",
                    "error_msg": "未知异常",
                    "error_response": str(e)
=======
                if tb_list:
                    last_call = tb_list[-1]  # 最底层的异常点
                    file_path = last_call.filename
                    line_no = last_call.lineno
                else:
                    file_path = None
                    line_no = -1

                error_data = {
                    "error_code": "99999",
                    "error_msg": "未知异常",
                    "error_response": str(exc_obj),
                    "error_file": file_path,
                    "error_line": line_no
>>>>>>> 8ac52ce02c8d59b76b4011f6b7cbde9d520242ba
                }

            # 计算运行时长（秒）
            run_duration = time.time() - self.start_time
            error_data['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 任务ID
            error_data['task_id'] = self.default_params['task_id']
            print("任务失败", json.dumps(error_data, ensure_ascii=False))

            # 任务失败
            taskRequest.error(error_data)

        finally:
            # 停止监听新标签页线程
            if self.stop_event:
                self.stop_event.set()

            if self.monitor_thread:
                self.monitor_thread.join()

            # 关闭 driver
            if self.driver:
                self.driver.quit()
                time.sleep(1)

            # 关闭 mitmdump
            if self.mitmdump:
                self.mitmdump.kill()
                time.sleep(1)

            # 清理临时目录
            if self.tmpdir:
                self.tmpdir.cleanup()

            # 垃圾回收
            gc.collect()

        input("浏览器已打开，按 Enter 键退出...")

    def task_main(self):
        '''
        @Desc    : 任务入口
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        self.default_params = self.options["params"]
        if isinstance(self.default_params, str):
            self.default_params = json.loads(self.default_params)

        res = taskRequest.getTask(self.default_params)
        if res['status'] != 1:
            raise Exception(f"获取任务参数失败：{res['message']}")
        task_data = res['data']

        task_params = task_data['params']

        res = shopRequest.getDetail(self.default_params)
        if res['status'] != 1:
            raise Exception(f"获取店铺详情失败：{res['message']}")
        shop_data = res['data']

        params = {**self.default_params, **task_params}
        self.options['params'] = params

        listen_port = common.get_free_port()
        self.mitmdump = chrome.run_mitmproxy(shop_data, listen_port)
        print(f"✅ mitmproxy 已启动，本地监听 {listen_port}")

        self.tmpdir = tempfile.TemporaryDirectory()
        user_data_dir = self.tmpdir.name
        print("user_data_dir", user_data_dir)

        self.driver = chrome.start_driver(shop_data, listen_port, user_data_dir)

        # chrome.getFingerprint(self.driver, shop_data, params)

        known_handles = set(self.driver.window_handles)
        self.stop_event = threading.Event()
        self.monitor_thread = threading.Thread(
            target=chrome.monitorNewTabs,
            args=(self.driver, shop_data, known_handles, self.stop_event),
            daemon=True
        )
        self.monitor_thread.start()

        common.runJob(self.driver, shop_data, self.options)

        run_duration = time.time() - self.start_time
        params['run_duration'] = run_duration
        print(f"任务用时：{run_duration}秒")

        taskRequest.end(params)

class ExceptionThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = None

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.exception = e  # 捕获并保存异常