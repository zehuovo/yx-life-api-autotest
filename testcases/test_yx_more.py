"""补充测试用例"""
import pytest
from common.api_utils import ApiRunner
from utils.data_utils import get_testcases

# 加载 data/more_testcases/ 目录下所有补充测试用例
more_data = get_testcases("data/ai_testcases")


class TestYxMore:

    @pytest.mark.parametrize("data", more_data)
    def test_more(self, data, get_yx_session):
        ApiRunner(data, session=get_yx_session).run()
