import pytest
from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list

# 笔记模块测试用例
blog_data = read_yaml_list("data/yx_test_data/blog.yaml")


class TestYxBlog:

    @pytest.mark.parametrize("data", blog_data)
    def test_blog(self, data, get_yx_session):
        ApiRunner(data, session=get_yx_session).run()
