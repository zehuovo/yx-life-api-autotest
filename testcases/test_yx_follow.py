import pytest
from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list

# 关注模块测试用例
follow_data = read_yaml_list("data/yx_test_data/follow.yaml")


class TestYxFollow:

    @pytest.mark.parametrize("data", follow_data)
    def test_follow(self, data, get_yx_session):
        ApiRunner(data, session=get_yx_session).run()
