import pytest
from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list

# 优惠券模块测试用例
voucher_data = read_yaml_list("data/yx_test_data/voucher.yaml")


class TestYxVoucher:

    @pytest.mark.parametrize("data", voucher_data)
    def test_voucher(self, data, get_yx_session):
        ApiRunner(data, session=get_yx_session).run()
