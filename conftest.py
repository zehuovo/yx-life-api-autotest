import pytest
import requests
import logging
from utils.data_utils import clear_extract_yaml

# 配置日志记录器
logger = logging.getLogger("Hsyuan")

@pytest.fixture(scope='session', autouse=False)
def get_yx_session():
    """
    悦享生活服务平台专属：全局 Session 状态管理
    说明：采用静态 Token 注入方式模拟已登录状态，绕过动态短信验证码的限制，
          保证 CI/CD 自动化测试管线在无人工干预下的稳定性。
    """
    session = requests.Session()
    
    # ⚠️【配置说明】
    # 请先在浏览器中手动登录“悦享生活服务平台”，按 F12 打开开发者工具，
    # 在 Application -> Session Storage 中找到并复制你的真实 Token 字符串，替换掉下面的值。
    TEST_TOKEN = "请把这里替换为你浏览器里真实的Token字符串"
    
    # 将 Token 统一设置到 Session 的请求头中
    # (悦享生活服务平台网关/拦截器统一校验 'authorization' 字段)
    session.headers.update({
        "authorization": TEST_TOKEN
    })
    
    # 打印前10位Token字符做脱敏日志输出，方便排查问题
    logger.info(f"🔑 已成功挂载 [悦享生活服务平台] 测试环境凭证, Token截断: {TEST_TOKEN[:10]}...")

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