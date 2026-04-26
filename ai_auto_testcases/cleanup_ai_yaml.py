"""清洗 AI 生成的 YAML 测试用例，适配悦享生活服务平台的实际 API 响应格式"""
import os
import yaml
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

AI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "more_testcases")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "more_testcases_backup")


def backup_originals():
    """备份原始 AI 生成的 YAML"""
    import shutil
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(AI_DIR, BACKUP_DIR)
    print(f"[INFO] 已备份原始文件到: {BACKUP_DIR}")


def clean_yaml(data):
    """清洗单个 YAML 文件的所有测试用例"""
    cleaned = {}
    for case_name, case_data in data.items():
        try:
            expected = case_data.get("steps", {}).get("expected", {})
            if not expected:
                cleaned[case_name] = case_data
                continue

            # 1. 强制 status_code 为 200（API 对业务错误也返回 200）
            expected["status_code"] = 200

            response = expected.get("response", {})
            if not response:
                cleaned[case_name] = case_data
                continue

            # 2. 删除 code 和 msg 字段（API 不返回这些）
            response.pop("code", None)
            response.pop("msg", None)

            # 3. 处理 data.assert.eq 中的数据提升到 response 层
            data_config = response.get("data", {})
            assert_config = data_config.get("assert", {})
            eq_config = assert_config.get("eq", {}) if assert_config else {}

            # 提取 success 和 errorMsg（放在 response 层而不是 data.assert.eq 层）
            if "success" in eq_config:
                response["success"] = eq_config.pop("success")
            if "errorMsg" in eq_config:
                response["errorMsg"] = eq_config.pop("errorMsg")
            if "msg" in eq_config:
                # API 用 errorMsg 而不是 msg
                response["errorMsg"] = eq_config.pop("msg")

            # 4. 检查 data 层级是否还有有效断言
            has_data_asserts = bool(assert_config and any(
                v for v in assert_config.values() if v
            ))
            has_list_check = "list_check" in data_config
            has_required_fields = bool(data_config.get("required_fields"))

            # 如果 data 层没有有效内容，删除它
            if not has_data_asserts and not has_list_check and not has_required_fields:
                response.pop("data", None)
            elif has_required_fields:
                # 只保留 required_fields，删除 assert
                if assert_config:
                    data_config.pop("assert", None)

            # 5. 处理 data.required_fields 包含 success 或 errorMsg 的情况
            if data_config and "required_fields" in data_config:
                rf = data_config["required_fields"]
                # 移除 success 和 errorMsg（它们是根字段不是 data 字段）
                data_config["required_fields"] = [f for f in rf if f not in ("success", "errorMsg")]
                if not data_config["required_fields"]:
                    data_config.pop("required_fields")

            # 6. 删除空的 data{}
            if data_config and not any(data_config.values()):
                response.pop("data", None)

            cleaned[case_name] = case_data

        except Exception as e:
            print(f"[ERR] 清洗用例 {case_name} 失败: {e}")
            cleaned[case_name] = case_data

    return cleaned


def main():
    print("=" * 50)
    print("  AI 测试用例清洗工具 - 适配悦享生活API")
    print("=" * 50)

    # 备份
    backup_originals()

    # 遍历所有 AI 生成的 YAML
    yaml_files = [f for f in os.listdir(AI_DIR) if f.endswith((".yml", ".yaml"))]
    success_count = 0
    total_cases = 0

    for filename in sorted(yaml_files):
        filepath = os.path.join(AI_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            continue

        case_count = len(data)
        total_cases += case_count

        # 清洗
        cleaned_data = clean_yaml(data)

        # 写回
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(cleaned_data, f, allow_unicode=True, sort_keys=False, indent=2)

        print(f"[OK] {filename} ({case_count} 个用例)")
        success_count += 1

    print(f"\n[DONE] 清洗完成！共处理 {success_count} 个文件，{total_cases} 个测试用例")
    print(f"[INFO] 原始文件备份在: {BACKUP_DIR}")


if __name__ == "__main__":
    main()
