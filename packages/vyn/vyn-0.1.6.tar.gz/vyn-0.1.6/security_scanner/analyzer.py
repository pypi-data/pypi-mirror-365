# import os
# import ast

# import json
# import http.client

# from bandit_test import run_bandit_on_path
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# from transformers import T5ForConditionalGeneration




# # model_id = "bigcode/starcoder2-7b"  

# # model_id = "tiiuae/falcon-rw-1b" 

# # model_id = "bigcode/starcoder2-3b"
# # model_id = "microsoft/codebert-base"
# model_id = "microsoft/phi-2"

# tokenizer = AutoTokenizer.from_pretrained(model_id)
# model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", trust_remote_code=True)

# generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# # generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)


# # def get_prompt(risk):  # Note: renamed from 'risks' to 'risk' for clarity
# #     code_snippet = risk.get('code', '')
# #     if code_snippet and len(code_snippet) > 500:
# #         code_snippet = code_snippet[:500] + '...'

# #     return f"""
# # You are a security auditor AI. Analyze the following potential security issue found in Python code and provide solutions and suggestions.

# # Issue Details:
# # - **Filename**: {risk.get('filename')}
# # - **Line number**: {risk.get('line_number')}
# # - **Test name**: {risk.get('test_name')}
# # - **Issue**: {risk.get('issue_text')}
# # - **Severity**: {risk.get('issue_severity')}
# # - **Confidence**: {risk.get('issue_confidence')}
# # - **Code snippet**:{risk.get('code')}
# # Please explain:
# # - What the issue means
# # - Why it matters
# # - How to fix it
# # - Any safer alternatives

# # Respond clearly and concisely.
# # """



# def get_prompt(risk):
#     code_snippet = risk.get('code', '')
#     if code_snippet and len(code_snippet) > 500:
#         code_snippet = code_snippet[:500] + '...'

#     return f"""# Security Issue Analysis

# **Filename:** {risk.get('filename')}
# **Line Number:** {risk.get('line_number')}
# **Test Name:** {risk.get('test_name')}
# **Severity:** {risk.get('issue_severity')}
# **Confidence:** {risk.get('issue_confidence')}
# **Issue Description:** {risk.get('issue_text')}

# ## Code Snippet
# ```python
# {code_snippet}
# Explain the following:
# What this issue means

# Why it's a security risk

# How to fix it

# Safer alternatives
# """


# def analyze_risk_with_ai(risks, model="starcoder"):
#     ai_responses = []
#     for risk in risks:
#         prompt = get_prompt(risk)
#         if model == "starcoder":
#             output = generator(
#                 prompt,
#                 max_new_tokens=300,
#                 do_sample=False,
#                 pad_token_id=tokenizer.eos_token_id
#             )[0]['generated_text']
#             ai_response = output[len(prompt):].strip()
#             print("ai_response:", ai_response)
#             ai_responses.append(ai_response)
#     return ai_responses



# def analyze_with_bandit(path):
#     issue_list =  run_bandit_on_path(path)

#     for result in issue_list:
#             issue = result.as_dict()
#             ai_prompt = get_prompt(risks=issue)
#             output = generator(ai_prompt, max_new_tokens=300, do_sample=False, pad_token_id=tokenizer.eos_token_id)[0]['generated_text']
#             ai_response = output[len(ai_prompt):].strip()
#             print(ai_response)
            

    



# # def main(file_path):
# #     target = file_path 
# #     snippets = extract_code_snippets(target)

# #     if not snippets:
# #         print("✅ No Python code snippets found.")
# #         return

# #     for name, snippet in snippets:
# #         print(f"\n=== {name} ===\n")
# #         result = analyze_with_gemini(prompt)
# #         print(result)



# if __name__ == "__main__":
#     main()




# # def extract_code_snippets(target):
# #     code_snippets = []

# #     def process_file(filepath):
# #         with open(filepath, 'r', encoding='utf-8') as file:
# #             try:
# #                 code = file.read()
# #                 tree = ast.parse(code, filename=filepath)
# #                 for node in ast.walk(tree):
# #                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
# #                         snippet = ast.get_source_segment(code, node)
# #                         if snippet:
# #                             name = node.name if hasattr(node, 'name') else 'unknown'
# #                             code_snippets.append((f"{filepath}:{name}", snippet.strip()))
# #             except Exception as e:
# #                 print(f"⚠️ Error parsing {filepath}: {e}")

# #     if os.path.isfile(target):
# #         process_file(target)
# #     elif os.path.isdir(target):
# #         for root, _, files in os.walk(target):
# #             for file in files:
# #                 if file.endswith('.py'):
# #                     process_file(os.path.join(root, file))
# #     else:
# #         raise FileNotFoundError(f"No such file or directory: {target}")

# #     return code_snippets


# # def analyze_with_gemini(prompt):
# #     conn = http.client.HTTPSConnection("gemini-pro-ai.p.rapidapi.com")

# #     payload = json.dumps({
# #         "contents": [
# #             {
# #                 "parts": [
# #                     {"text": prompt}
# #                 ]
# #             }
# #         ]
# #     })

# #     headers = {
# #         'x-rapidapi-key': "31ba40adaamshf438034211f2b0dp15b847jsnff8d0bfabb84",
# #         'x-rapidapi-host': "gemini-pro-ai.p.rapidapi.com",
# #         'Content-Type': "application/json"
# #     }

# #     conn.request("POST", "/", payload, headers)
# #     res = conn.getresponse()
# #     data = res.read()

# #     try:
# #         return json.loads(data.decode("utf-8"))["candidates"][0]["content"]["parts"][0]["text"]
# #     except Exception as e:
# #         return f"⚠️ Error parsing response: {e}\nRaw response: {data}"








# from transformers import pipeline

# qa_pipeline = pipeline("question-answering", 
#                        model="deepset/tinyroberta-squad2", 
#                        tokenizer="deepset/tinyroberta-squad2")



# def get_ai_suggestion(issue_text, code_snippet):
#     question = f"""🔒 Security Issue Detected:

# Issue: {issue_text}

# Code:
# {code_snippet}

# 🔧 Suggest a fix for this security issue. Include code improvements, best practices, and any explanation that helps developers write safer code.
# """
#     context = code_snippet[:512] 
#     try:
#         response = qa_pipeline(question=question, context=context)
#         return response['answer']
#     except Exception as e:
#         return f"AI failed: {str(e)}"
    
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_AI_KEY") 

# def get_ai_suggestion(issue_text, code_snippet):
#     prompt = f"""🔒 Security Issue Detected:

# Issue: {issue_text}

# Code:
# {code_snippet}

# 🔧 Suggest a secure fix for the issue above. Provide:
# 1. A safer version of the code.
# 2. A short explanation of the fix.
# 3. Best practices if applicable.
# """

#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": "mistralai/mistral-7b-instruct",  
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(data))
#         response.raise_for_status() 
#         reply = response.json()
#         return reply["choices"][0]["message"]["content"]
#     except Exception as e:
#         return f"AI request failed: {str(e)}"


def get_ai_suggestion(issue_text, code_snippet):
    prompt = f"""🔒 Security Issue:

Issue: {issue_text}

Code:
{code_snippet}

🔧 Suggest a concise fix (max 5 lines of code) and a 1-line explanation. Skip extra details or long best practices.
"""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        reply = response.json()
        return reply["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI request failed: {str(e)}"


def save_scan_report(results, filename="scan_report.txt"):
    try:
        print('results', results)
        print('results type:', type(results))
        
        # Check if results is a string that needs parsing
        if isinstance(results, str):
            issues = parse_security_scan_results(results)
            
            with open(filename, "w", encoding='utf-8') as f:
                f.write("# Security Audit Report\n\n")
                f.write(f"**Issues Found:** {len(issues)} total issues\n")
                f.write("\n---\n\n")
                
                for i, issue in enumerate(issues, 1):
                    f.write(f"## {i}. {issue['title']}\n")
                    f.write(f"**File:** {issue['file']}\n")
                    f.write(f"**Line:** {issue['line']}\n")
                    f.write(f"**Severity:** {issue['severity']}\n")
                    f.write(f"**Confidence:** {issue['confidence']}\n\n")
                    f.write("**Issue:**\n")
                    f.write(f"{issue['issue']}\n\n")
                    
                    if issue['ai_suggestion']:
                        f.write("**AI Suggestion:**\n")
                        f.write(f"{issue['ai_suggestion']}\n\n")
                    
                    f.write("---\n\n")
                    
        # Check if results is a dictionary with the expected structure
        elif isinstance(results, dict):
            with open(filename, "w", encoding='utf-8') as f:
                f.write("# Security Audit Report\n\n")
                
                # Safely access metrics if they exist
                if 'metrics' in results and '_totals' in results['metrics']:
                    totals = results['metrics']['_totals']
                    loc = totals.get('loc', 'Unknown')
                    high = totals.get('SEVERITY.HIGH', 0)
                    medium = totals.get('SEVERITY.MEDIUM', 0) 
                    low = totals.get('SEVERITY.LOW', 0)
                    
                    f.write(f"**Target:** {loc} lines scanned\n")
                    f.write(f"**Issues Found:** {high} HIGH | {medium} MEDIUM | {low} LOW\n")
                else:
                    f.write("**Metrics:** Not available\n")
                
                f.write("\n---\n\n")
                
                # Process individual issues if they exist
                if 'results' in results and isinstance(results['results'], list):
                    for i, issue in enumerate(results["results"], 1):
                        print("issue", issue)
                        
                        # Safely access issue properties
                        severity = issue.get('issue_severity', 'UNKNOWN')
                        confidence = issue.get('issue_confidence', 'UNKNOWN')
                        filename_issue = issue.get('filename', 'Unknown file')
                        line_number = issue.get('line_number', 'Unknown')
                        more_info = issue.get('more_info', 'No additional info')
                        issue_text = issue.get('issue_text', 'No description')
                        code = issue.get('code', 'No code snippet')
                        
                        f.write(f"## {i}. (Severity: {severity}, Confidence: {confidence})\n")
                        f.write(f"**Location:** {filename_issue} : Line {line_number}\n")
                        f.write(f"**More Info:** {more_info}\n\n")
                        f.write("**Issue:**\n")
                        f.write(f"{issue_text}\n\n")
                        f.write("**Code Snippet:**\n")
                        f.write("```\n")
                        f.write(f"{code}\n")
                        f.write("```\n\n")
                        
                        # Add AI suggestion if available
                        ai_suggestion = issue.get('ai_suggestion', '')
                        if ai_suggestion:
                            f.write("**AI Suggestion:**\n")
                            f.write(f"{ai_suggestion}\n\n")
                        
                        f.write("---\n\n")
                else:
                    f.write("No individual issues found or results format is unexpected.\n")
        else:
            print("Error: results is not a string or dictionary")
            with open(filename, "w", encoding='utf-8') as f:
                f.write("# Security Audit Report\n\n")
                f.write("Error: Unable to parse scan results.\n")
                f.write("Raw results:\n")
                f.write(str(results))
            return
                
        print(f"Scan report saved to {filename}")
        
    except Exception as e:
        print(f"Error saving scan report: {e}")
        # Create a basic error report file
        try:
            with open(filename, "w", encoding='utf-8') as f:
                f.write("# Security Audit Report - Error\n\n")
                f.write(f"An error occurred while generating the report: {e}\n\n")
                f.write("Raw results data:\n")
                f.write(str(results))
        except:
            print("Could not create error report file")


def parse_security_scan_results(results_string):
    """Parse the string output from security scanner into structured data"""
    issues = []
    
    # Split by the separator line
    sections = results_string.split("==================================================")
    
    for section in sections:
        if not section.strip() or "results ==================================================" in section:
            continue
            
        lines = section.strip().split('\n')
        if len(lines) < 2:
            continue
            
        issue = {
            'title': '',
            'file': '',
            'line': '',
            'severity': '',
            'confidence': '',
            'issue': '',
            'ai_suggestion': ''
        }
        
        current_section = None
        ai_suggestion_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('→ Issue'):
                issue['title'] = line.split(':', 1)[1].strip()
            elif line.startswith('→ File'):
                issue['file'] = line.split(':', 1)[1].strip()
            elif line.startswith('→ Line'):
                issue['line'] = line.split(':', 1)[1].strip()
            elif line.startswith('→ Severity'):
                issue['severity'] = line.split(':', 1)[1].strip()
            elif line.startswith('→ Confidence'):
                issue['confidence'] = line.split(':', 1)[1].strip()
            elif line.startswith('→ AI Suggestion'):
                current_section = 'ai_suggestion'
                ai_suggestion_content = line.split(':', 1)[1].strip() if ':' in line else ''
                if ai_suggestion_content:
                    ai_suggestion_lines.append(ai_suggestion_content)
            elif current_section == 'ai_suggestion':
                ai_suggestion_lines.append(line)
        
        # Clean up and join AI suggestion
        if ai_suggestion_lines:
            issue['ai_suggestion'] = '\n'.join(ai_suggestion_lines).strip()
        
        # Set issue description as the title if we have one
        if issue['title']:
            issue['issue'] = issue['title']
            issues.append(issue)
    
    return issues
