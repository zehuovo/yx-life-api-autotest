import pytest
from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list

# 所有测试用例列表
shop_data = read_yaml_list("data/yx_test_data/shop.yaml")


class TestYxShop:

    @pytest.mark.parametrize("data", shop_data)
    def test_shop(self, data, get_yx_session):
        ApiRunner(data, session=get_yx_session).run()
