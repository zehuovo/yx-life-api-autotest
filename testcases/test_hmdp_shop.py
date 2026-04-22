import requests

class TestHmdpShop:
    
    def test_get_shop_type_list(self):
        """测试获取商铺分类列表接口"""
        # 1. 拼接你要测试的黑马点评真实接口地址
        url = "http://127.0.0.1:8081/shop-type/list"
        
        # 2. 模拟前端发送 GET 请求
        response = requests.get(url=url)
        
        # 3. 打印一下返回结果看看
        print(f"黑马后台返回的数据是: {response.text}")
        
        # 4. 断言（校验）：如果状态码是 200，说明接口通了！
        assert response.status_code == 200