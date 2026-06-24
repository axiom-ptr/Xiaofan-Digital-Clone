import os
import json
import requests
import time
import sys
from datetime import datetime

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"
# 优先读取命令行参数中的模型名，否则默认使用 GLM-5.2
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else "zai-org/GLM-5.2"

def main():
    print(f"正在加载小饭人格核心 (Prompt_System + Canonical Principles)...")
    try:
        with open("dist/Prompt_System.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
        with open("identity/canonical_principles.md", "r", encoding="utf-8") as f:
            principles = f.read()
    except Exception as e:
        print(f"加载文件失败: {e}")
        return
        
    full_system_prompt = system_prompt + "\n\n【底层世界观原则（绝对不可违背）】\n" + principles
    
    print("正在加载 L4 反事实测试题库 (Counterfactual Cases)...")
    try:
        with open("tests/counterfactual_cases.json", "r", encoding="utf-8") as f:
            cases = json.load(f)
    except Exception as e:
        print(f"加载题库失败: {e}")
        return
        
    # 取第一道反事实题目
    test_case = cases["scenarios"][0] 
    
    report_lines = []
    header = f"========================================\n[测试环境] API: 硅基流动 | 模型: {MODEL_NAME}\n[测试类别] Level 4: {test_case['category']}\n========================================"
    print(f"\n{header}")
    
    report_lines.append(f"# 自动化评测报告: {MODEL_NAME}\n")
    report_lines.append(f"> **测试类别**: Level 4 ({test_case['category']})")
    report_lines.append(f"> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"> **测试题目**: {test_case['scenario_name']}\n")
    report_lines.append("---\n")
    
    messages = [
        {"role": "system", "content": full_system_prompt}
    ]
    
    for i, turn in enumerate(test_case['turns']):
        print(f"\n🗣️ User: {turn}")
        report_lines.append(f"### Turn {i+1}\n")
        report_lines.append(f"**User**: {turn}\n")
        messages.append({"role": "user", "content": turn})
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.7
        }
        
        try:
            resp = requests.post(BASE_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                answer = resp.json()['choices'][0]['message']['content']
                print(f"\n🤖 Xiaofan: {answer}")
                report_lines.append(f"**Xiaofan**: {answer}\n")
                report_lines.append("---\n")
                messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = f"\n❌ API 请求失败: {resp.text}"
                print(error_msg)
                report_lines.append(error_msg)
                break
        except Exception as e:
            error_msg = f"\n❌ 请求异常: {e}"
            print(error_msg)
            report_lines.append(error_msg)
            break
        
        time.sleep(1.5)
        
    # 写入报告
    # 过滤掉模型名称中的特殊字符以便作为文件名
    safe_model_name = MODEL_NAME.replace("/", "_")
    report_filename = f"evaluation/monthly_reports/report_{safe_model_name}_{int(time.time())}.md"
    
    os.makedirs("evaluation/monthly_reports", exist_ok=True)
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\n✅ 测试报告已保存至: {report_filename}")

if __name__ == "__main__":
    main()
