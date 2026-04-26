import pytest
import requests
import logging
import redis as redis_module
from utils.data_utils import clear_extract_yaml

logger = logging.getLogger("HuZe")


@pytest.fixture(scope='session', autouse=True)
def get_yx_session():
    """
    悦享生活服务平台专属：全局 Session 状态管理
    说明：自动通过 Redis 获取短信验证码完成登录，无需手动配置 Token。
          测试开始时会：
            1. 向指定手机号发送验证码
            2. 从 Redis 读取该手机号的验证码
            3. 用验证码登录获取 Token
            4. 将 Token 注入 Session 的 authorization 请求头
    """
    session = requests.Session()
    phone = "13800138000"

    try:
        # 1. 发送验证码
        code_resp = session.post(f"http://127.0.0.1:8081/user/code?phone={phone}")
        if code_resp.json().get("success"):
            logger.info(f"验证码已发送至手机号: {phone}")

            # 2. 从 Redis 读取验证码
            r = redis_module.Redis(host='127.0.0.1', port=6379, db=0)
            code_key = f"login:code:{phone}"
            code = r.get(code_key)
            if code:
                code = code.decode("utf-8")
                logger.info(f"从 Redis 获取验证码成功")

                # 3. 登录
                login_resp = session.post(
                    "http://127.0.0.1:8081/user/login",
                    json={"phone": phone, "code": code}
                )
                login_data = login_resp.json()
                if login_data.get("success"):
                    token = login_data.get("data")
                    session.headers.update({"authorization": token})
                    logger.info(f"登录成功，Token: {token[:10]}...")
                else:
                    logger.warning(f"登录失败: {login_data.get('errorMsg')}")
            else:
                logger.warning("未从 Redis 获取到验证码")
        else:
            logger.warning("验证码发送失败")

    except Exception as e:
        logger.warning(f"自动登录失败: {e}，仅能测试无需登录的接口")

    yield session

    session.close()


@pytest.fixture(scope='session', autouse=True)
def setup_and_teardown():
    """全局测试环境初始化与脏数据清理"""
    logger.info("==================================================================")
    logger.info("  悦享生活服务平台 核心业务接口自动化测试管线开始执行...")
    logger.info("==================================================================")

    clear_extract_yaml()

    yield

    logger.info("==================================================================")
    logger.info("  悦享生活服务平台 自动化测试用例执行完毕，正在关闭环境...")
    logger.info("==================================================================")
