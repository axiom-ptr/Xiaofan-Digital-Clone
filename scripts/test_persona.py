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
TEST_CASES_PATH = "tests/test_cases_extended.json"

# v2.1 评分权重
WEIGHTS = {
    "anti_gpt": 0.40,
    "logic": 0.40,
    "vocabulary": 0.20
}

EVAL_PROMPT = """你是一个专门评估「小饭」数字分身还原度的评委。
请根据以下三项指标为AI生成的回答打分（0-100分），并给出最终加权总分。

【评分标准 v2.1】
1. Anti-GPT 表现 (权重 40%)
   - 100分：完全没有AI味，像真人在直播中不假思索的脱口而出。拒绝了"首先/其次"、拒绝了分点、拒绝了居高临下的说教。
   - 0分：典型的AI回复（如"作为一个AI"、列举123点、强行理中客、总结式结尾）。

2. 核心立意 (权重 40%)
   - 100分：精准匹配原版小饭的底层逻辑（如阶层对立、零和博弈、对权力的嘲讽、看透不说透的清醒），甚至比原话更锋利。
   - 0分：立意偏离，充满正能量或教科书式的分析。

3. 口癖与语感 (权重 20%)
   - 100分：自然使用了小饭的高频词汇（如渣男战法、弱关系、牛马、精神股东、妈妈队等），且情绪到位（嘲讽、摆烂或拷打）。
   - 0分：语气平淡，没有使用任何标志性词汇，或者强行堆砌显得做作。

【输入数据】
用户问题：{question}
小饭原版核心立意（参考）：{core_logic}
AI分身回答：{ai_answer}

【输出格式要求】（必须以JSON格式输出）
{{
    "anti_gpt_score": 80,
    "logic_score": 90,
    "vocabulary_score": 85,
    "total_score": 85.0,
    "eval_reason": "简短的评价理由"
}}
"""

def init_client():
    if has_new_sdk:
        return genai.Client()
    else:
        old_genai.configure()
        return None

def generate_answer(client, system_prompt, question):
    if has_new_sdk:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
        )
        return response.text
    else:
        model = old_genai.GenerativeModel('gemini-2.5-pro', system_instruction=system_prompt)
        response = model.generate_content(question)
        return response.text

def evaluate_answer(client, question, core_logic, ai_answer):
    prompt = EVAL_PROMPT.format(question=question, core_logic=core_logic, ai_answer=ai_answer)
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
        # Parse JSON
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)

def main():
    parser = argparse.ArgumentParser(description="小饭 Persona 自动化评测管道 (v2.1)")
    parser.add_argument("--count", type=int, default=5, help="要评测的题目数量（默认前5题）")
    parser.add_argument("--category", type=str, default="", help="指定评测的题目类别")
    args = parser.parse_args()

    print("正在加载 System Prompt...")
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    print("正在加载测试题库...")
    with open(TEST_CASES_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    test_cases = dataset.get("test_cases", [])
    if args.category:
        test_cases = [tc for tc in test_cases if args.category in tc.get("category", "")]
    
    test_cases = test_cases[:args.count]
    print(f"准备评测 {len(test_cases)} 道题目...")

    client = init_client()
    
    total_weighted_score = 0
    results = []

    for i, tc in enumerate(test_cases):
        question = tc["question"]
        core_logic = tc.get("core_logic", "无")
        
        print(f"\n[{i+1}/{len(test_cases)}] 测试问题: {question}")
        
        # 1. 生成回答
        ai_answer = generate_answer(client, system_prompt, question)
        print(f"--> AI 回答 (截断前100字): {ai_answer[:100]}...")
        
        # 2. 自动化评分
        try:
            eval_res = evaluate_answer(client, question, core_logic, ai_answer)
            score = (
                eval_res["anti_gpt_score"] * WEIGHTS["anti_gpt"] + 
                eval_res["logic_score"] * WEIGHTS["logic"] + 
                eval_res["vocabulary_score"] * WEIGHTS["vocabulary"]
            )
            print(f"    评分: Anti-GPT={eval_res['anti_gpt_score']}, 立意={eval_res['logic_score']}, 口癖={eval_res['vocabulary_score']} => 加权总分: {score:.1f}")
            print(f"    评委点评: {eval_res['eval_reason']}")
            
            total_weighted_score += score
            results.append({
                "question": question,
                "ai_answer": ai_answer,
                "evaluation": eval_res,
                "final_score": score
            })
        except Exception as e:
            print(f"    评分失败: {e}")
            continue

        time.sleep(2) # 避免限流

    if results:
        avg_score = total_weighted_score / len(results)
        print(f"\n{'='*40}")
        print(f"评测完成！平均得分: {avg_score:.2f} / 100")
        print(f"{'='*40}")

if __name__ == "__main__":
    main()
