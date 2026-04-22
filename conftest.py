import pytest
import requests
import logging
from utils.data_utils import clear_extract_yaml
from common.config import SERVER_URL  # 引入全局的服务器地址

# 配置日志记录器
logger = logging.getLogger("Hsyuan")

@pytest.fixture(scope='session', autouse=False)
def get_yx_session():
    """
    悦享生活专属：全局 Session 状态与动态鉴权管理
    说明：在自动化管线启动时，自动调用登录接口获取最新 Token，彻底解决 Token 过期导致的 CI/CD 失败问题。
    """
    session = requests.Session()
    
    # 1. 组装登录接口的 URL
    login_url = f"{SERVER_URL}/user/login"
    
    # 2. 准备登录参数（黑马点评通常是手机号+验证码/密码）
    # ⚠️ 注意：测试环境中，为了自动化，建议在后端给这个测试手机号写死一个验证码，或者临时关闭这个手机号的验证码校验
    payload = {
        "phone": "13800000000",
        "code": "123456"  # 根据你后端的实际情况修改
    }
    
    logger.info(f"⏳ 正在尝试自动登录悦享生活，测试账号: {payload['phone']}")
    
    try:
        # 3. 发送真实的登录请求
        resp = requests.post(login_url, json=payload)
        resp_json = resp.json()
        
        # 4. 黑马点评的成功响应结构通常是 {"success": true, "data": "你的token字符串"}
        if resp_json.get("success") == True or resp_json.get("code") == 200:
            # 提取新鲜的 Token
            fresh_token = resp_json.get("data")
            
            # 将 Token 统一设置到 Session 的请求头中
            session.headers.update({
                "authorization": fresh_token
            })
            logger.info(f"🔑 自动登录成功! 已挂载动态 Token: {fresh_token[:10]}...")
        else:
            logger.error(f"❌ 自动登录失败，后端返回信息: {resp_json}")
            raise Exception("自动化登录流程失败，中断测试")
            
    except Exception as e:
        logger.error(f"❌ 登录请求发生网络异常: {e}")
        raise e

    # 将携带了身份认证信息的 session 交付给下游所有的测试用例
    yield session

    # 整个测试会话结束，安全释放网络连接资源
    session.close()


@pytest.fixture(scope='session', autouse=True)
def setup_and_teardown():
    """全局测试环境初始化与脏数据清理"""
    logger.info("==================================================================")
    logger.info("  🚀 [悦享生活服务平台] 核心业务接口自动化测试管线开始执行...")
    logger.info("==================================================================")
    
    # 清理历史运行产生的临时环境变量（避免测试用例之间产生数据污染）
    clear_extract_yaml()

    yield
    
    logger.info("==================================================================")
    logger.info("  🏁 [悦享生活服务平台] 自动化测试用例执行完毕，正在关闭环境...")
    logger.info("==================================================================")
