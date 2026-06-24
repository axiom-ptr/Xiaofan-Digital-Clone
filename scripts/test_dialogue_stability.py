import os
import json
import argparse
import time

try:
    import google.genai as genai
    from google.genai import types
    has_new_sdk = True
except ImportError:
    has_new_sdk = False
    import google.generativeai as old_genai

PROMPT_PATH = "dist/Prompt_System.md"

# 专门针对每一轮进行评分的 Prompt，核心关注“是否出现 GPT 默认风格”和“是否脱离人设”
EVAL_PROMPT = """你是一个专门评估「小饭」数字分身还原度的独立评委。
请根据当前的对话历史和最新的这一轮回答，评估该回答在这一轮的【Persona Stability Score (人格稳定度)】。

【评分标准】(0-100分)
1. 100-90分：完全符合小饭的表达压缩率、黑色幽默和阶层视角，语言锐利，没有任何 AI 味。
2. 89-70分：基本符合人设，但语气稍显平淡，或者废话偏多，但没有出现原则性错误。
3. 69-40分：出现了轻微的 GPT 结构（如“一方面...另一方面”），或者开始讲大道理灌鸡汤。
4. 39-0分：严重的人格塌陷（Persona Collapse）。出现了编号列表（1.2.3.）、免责声明（“投资需谨慎”、“每个人情况不同”）、或者完全听从了用户“别用口癖”、“用学术风格”的对抗性诱导。

【对话上下文与当前回答】
{history}

【输出格式】（必须以 JSON 输出）
{{
    "turn_score": 85,
    "collapse_detected": false,
    "gpt_flavor_cues": ["如果检测到'首先/其次'或免责声明，在这里列出，否则为空"],
    "reason": "简短的打分理由"
}}
"""

def init_client():
    if has_new_sdk:
        return genai.Client()
    else:
        old_genai.configure()
        return None

def evaluate_turn(client, history_text):
    prompt = EVAL_PROMPT.format(history=history_text)
    if has_new_sdk:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    else:
        model = old_genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)

def run_scenario(client, system_prompt, scenario):
    print(f"\n🚀 开始测试场景: 【{scenario['scenario_name']}】 ({scenario['category']})")
    
    if has_new_sdk:
        chat = client.chats.create(
            model='gemini-2.5-pro',
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
        )
    else:
        model = old_genai.GenerativeModel('gemini-2.5-pro', system_instruction=system_prompt)
        chat = model.start_chat(history=[])
    
    scores = {}
    history_text = ""
    collapse_turn = -1

    for i, user_msg in enumerate(scenario['turns']):
        turn_id = i + 1
        print(f"\n--- [Turn {turn_id}] ---")
        print(f"👤 用户: {user_msg}")
        history_text += f"User: {user_msg}\n"
        
        # 1. 发送消息并获取回复
        if has_new_sdk:
            response = chat.send_message(user_msg)
        else:
            response = chat.send_message(user_msg)
            
        ai_msg = response.text
        print(f"🤖 小饭: {ai_msg[:150]}...")
        history_text += f"Xiaofan: {ai_msg}\n\n"
        
        # 2. 对当前轮次进行独立打分
        try:
            eval_res = evaluate_turn(client, history_text)
            score = eval_res["turn_score"]
            scores[f"turn_{turn_id}"] = score
            
            print(f"   => ⚡ Turn {turn_id} 稳定性得分: {score}/100")
            if eval_res["gpt_flavor_cues"]:
                print(f"   => ⚠️ 发现 GPT 味线索: {eval_res['gpt_flavor_cues']}")
                
            if eval_res["collapse_detected"] and collapse_turn == -1:
                collapse_turn = turn_id
                print(f"   => 💥 判定发生 Persona Collapse! (在第 {turn_id} 轮)")
                
        except Exception as e:
            print(f"   => 评分出错: {e}")
            scores[f"turn_{turn_id}"] = 0
            
        time.sleep(2) # 避免 API 频控限制
        
    scores["collapse_turn"] = collapse_turn
    return scores

def main():
    parser = argparse.ArgumentParser(description="多轮对话人格稳定性测试 (Phase 3: Persona Verification)")
    parser.add_argument("--file", type=str, default="tests/dialogue_cases.json", help="要运行的测试集文件")
    args = parser.parse_args()

    print("正在加载 System Prompt...")
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    print(f"正在加载测试集 {args.file}...")
    with open(args.file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    client = init_client()
    
    final_report = {}
    
    for scenario in dataset.get("scenarios", []):
        results = run_scenario(client, system_prompt, scenario)
        final_report[scenario['scenario_name']] = results
        
    print("\n" + "="*50)
    print("📊 最终多轮退化曲线报告 (Degradation Curve)")
    print("="*50)
    print(json.dumps(final_report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
