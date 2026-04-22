import pytest
from utils.data_utils import get_testcases
from common.api_utils import ApiRunner

# 自动扫描 data/test_data/ 目录下你刚才写的那个 yaml 文件
cases = get_testcases("data/test_data")

class TestYueXiangLife:
    
    # 用参数化机制，把读取到的 YAML 用例一条条送进来执行
    @pytest.mark.parametrize("case_data", cases)
    def test_run_business_flow(self, case_data, get_yx_session):
        # 1. 初始化发动机（传入用例数据 + 全局已登录的 Token Session）
        runner = ApiRunner(data=case_data, session=get_yx_session)
        # 2. 点火运行！
        runner.run()
