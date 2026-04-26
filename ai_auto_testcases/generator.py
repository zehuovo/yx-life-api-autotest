"""AI测试用例生成器 - 支持手动定义接口（无需Swagger）"""

import os
import yaml
import sys
from openai import OpenAI

# 确保能导入父目录的 common 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import API_KEY, AI_URL, AI_MODEL

# 脚本所在目录（保证在任何位置运行都能找到文件）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置
MANUAL_API_FILE = os.path.join(BASE_DIR, "api_definitions.yaml")
PROMPT_FILE = os.path.join(BASE_DIR, "prompt.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "more_testcases")

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 预加载系统提示词
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    system_prompt = f.read()


def get_ai_client():
    """获取AI客户端（检查配置）"""
    if not API_KEY:
        print("[ERR] 未配置API_KEY！请在.env文件中添加以下配置：")
        print("   API_KEY=你的API密钥")
        print("   AI_URL=https://api.deepseek.com  # 或其他兼容OpenAI的API地址")
        return None
    if not AI_URL:
        print("[ERR] 未配置AI_URL！请在.env文件中添加AI接口地址")
        return None
    return OpenAI(api_key=API_KEY, base_url=AI_URL)


def load_manual_apis():
    """从YAML文件加载手动定义的接口列表（无需Swagger）"""
    if not os.path.exists(MANUAL_API_FILE):
        print(f"[ERR] 未找到手动接口定义文件：{MANUAL_API_FILE}")
        print(f"   请先创建 {MANUAL_API_FILE} 文件，或检查路径是否正确")
        return []

    with open(MANUAL_API_FILE, "r", encoding="utf-8") as f:
        apis = yaml.safe_load(f)

    if not apis:
        print("[ERR] 接口定义文件为空")
        return []

    print(f"[OK] 已加载 {len(apis)} 个手动定义的接口")
    api_list = []
    for api in apis:
        path = api.get("path", "")
        method = api.get("method", "GET")
        api_name = api.get("api_name", f"{method}_{path}")

        # 组装成和Swagger解析一样的格式，方便AI理解
        single_api_doc = {
            "接口名称": api_name,
            "接口地址": path,
            "请求方法": method.upper(),
            "接口描述": api.get("description", "无"),
            "请求参数": api.get("parameters", []),
            "响应参数": api.get("responses", {})
        }

        # 生成文件名
        safe_path = path.replace("/", "_").replace("{", "").replace("}", "")
        file_name = f"test_{method.lower()}{safe_path}.yml"

        api_list.append({
            "api_name": api_name,
            "file_name": file_name,
            "api_doc": single_api_doc
        })
        print(f"[API] 加载接口：{method.upper()} {path} -> {api_name}")

    return api_list


def generate_yaml(api_info, client):
    """单个接口生成YAML用例"""
    api_doc_str = yaml.dump(api_info, allow_unicode=True, sort_keys=False)

    print(f"\n[WAIT] AI生成中：{api_info.get('接口名称', '未知接口')} ...")

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"接口文档：{api_doc_str}\n请直接返回可用的YAML用例"}
            ],
            stream=True,
            top_p=0.8,
            temperature=0.7
        )

        answer_content = ""
        is_answering = False

        for chunk in response:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                if not is_answering:
                    print("\n" + "=" * 20 + "用例内容" + "=" * 20)
                    is_answering = True
                print(delta.content, end="", flush=True)
                answer_content += delta.content

        return answer_content.strip()
    except Exception as e:
        print(f"\n[ERR] AI调用失败：{str(e)}")
        print("  请检查：")
        print("  1. API_KEY 是否正确")
        print("  2. AI_URL 是否正确（需要兼容OpenAI接口格式）")
        print("  3. 网络连接是否正常")
        return ""


def save_yaml(content, filename):
    """保存单个接口的YAML用例文件"""
    path = os.path.join(OUTPUT_DIR, filename)

    # 去除 markdown 代码块格式
    content = content.strip()
    if content.startswith("```"):
        content = content[3:]  # 去掉 ```
    content = content.strip()
    if content.lower().startswith("yaml"):
        content = content[4:]  # 去掉 yaml (不区分大小写)
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # 校验YAML格式
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        print(f"\n[ERR] 生成的YAML格式非法，文件：{filename}，错误：{e}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  已保存原始文件供人工修正：{path}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[OK] 用例生成成功：{path}")
    return True


def select_apis(api_list):
    """让用户选择要生成的接口"""
    print("\n" + "=" * 50)
    print("可选择要生成的接口（输入编号，用逗号分隔）")
    print("  直接回车 = 全部生成")
    print("  输入 q = 退出")
    print("=" * 50)

    for idx, api in enumerate(api_list, 1):
        print(f"  {idx}. {api['api_name']}  ({api['api_doc']['请求方法']} {api['api_doc']['接口地址']})")

    choice = input("\n请输入: ").strip()
    if choice.lower() == "q":
        return []
    if not choice:
        return api_list

    try:
        indices = [int(i.strip()) for i in choice.split(",") if i.strip()]
        return [api_list[i - 1] for i in indices if 1 <= i <= len(api_list)]
    except (ValueError, IndexError):
        print("输入格式错误，将生成全部接口")
        return api_list


if __name__ == "__main__":
    print("=" * 50)
    print("  悦享生活服务平台 - AI测试用例生成器")
    print("=" * 50)
    print("  用法: python generator.py          # 交互式选择接口")
    print("        python generator.py --all    # 全部自动生成")
    print("=" * 50)

    # 1. 检查AI配置
    client = get_ai_client()
    if not client:
        exit(1)

    # 2. 从手动定义文件加载接口（无需Swagger）
    api_list = load_manual_apis()
    if not api_list:
        exit(1)

    # 3. 选择要生成的接口
    auto_all = len(sys.argv) > 1 and sys.argv[1] == "--all"
    if auto_all:
        selected_apis = api_list
        print("\n[INFO] --all 模式，将生成全部接口")
    else:
        selected_apis = select_apis(api_list)
    if not selected_apis:
        print("已退出")
        exit(0)

    # 4. 批量生成用例
    print(f"\n[START] 开始生成 {len(selected_apis)} 个接口的测试用例...")
    success_count = 0
    for index, api in enumerate(selected_apis, 1):
        print(f"\n==================== 进度：{index}/{len(selected_apis)} ====================")
        yaml_content = generate_yaml(api["api_doc"], client)
        if yaml_content:
            if save_yaml(yaml_content, api["file_name"]):
                success_count += 1
        else:
            print(f"\n[ERR] 接口 {api['api_name']} 生成内容为空，跳过")

    print(f"\n[DONE] 全部执行完成！成功生成 {success_count}/{len(selected_apis)} 个接口用例")
    print(f"[DIR] 用例保存目录：{os.path.abspath(OUTPUT_DIR)}")
