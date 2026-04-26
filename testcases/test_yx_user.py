import pytest
from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list

# 用户模块测试用例
user_data = read_yaml_list("data/yx_test_data/user.yaml")


class TestYxUser:

    @pytest.mark.parametrize("data", user_data)
    def test_user(self, data, get_yx_session):
        ApiRunner(data, session=get_yx_session).run()
