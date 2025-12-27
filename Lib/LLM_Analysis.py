from openai import OpenAI
from json_yaml_IO import *
import yaml
import json
import time

class LLM_model:
    def __init__(self, api_key, base_url, prompts_file=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        if prompts_file is not None:
            self.prompts_config = read_yaml(prompts_file)
        else:
            self.prompts_config = None

    def set_messages(self, user_input=None, prompts_key=None, system_prompt=None):
        if system_prompt is None:
            system_prompt = self.prompts_config[prompts_key]

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Handle both string and list inputs
        if isinstance(user_input, list):
            # Add multiple user messages if input is a list
            for item in user_input:
                messages.append({
                    "role": "user",
                    "content": str(item)
                })
        else:
            # Single user message for string input
            messages.append({
                "role": "user",
                "content": str(user_input)
            })
        
        return messages

    def get_json_response(
        self, 
        messages=None, 
        user_input=None, 
        prompts_key=None, 
        system_prompt=None, 
        model="deepseek-chat", 
        response_format='json_object'
        ):
        if messages is None:
            messages = self.set_messages(
                user_input=user_input, 
                prompts_key=prompts_key, 
                system_prompt=system_prompt
                )
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                'type': response_format
            }
        )
        result_text = response.choices[0].message.content.strip()

        return result_text
    

    # Classify the job position
    def get_job_position_info(self, user_input, prompts_key='get_job_position_info', model="deepseek-chat"):
        result_text = self.get_json_response(user_input, prompts_key, model=model)
        print(f'using_model: {model}')
        time_start = time.time()
        try:
            result = json.loads(result_text)
            
            return result.get("job_class", "")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Original output: {result_text}")
            return None

        finally:
            time_end = time.time()
            print(f'used time: {time_end - time_start} seconds')


    # Get Company Info result
    def get_Company_Info_result(self, user_input, prompts_key='analyze_company_info', model="deepseek-chat"):
        result_text = self.get_json_response(user_input, prompts_key, model=model)
        print(f'using_model: {model}')
        time_start = time.time()
        try:
            result = json.loads(result_text)
            ordered_result = {
                "company_name": result.get("company_name", ""),
                "company_description": result.get("company_description", ""),
                "is_foreign_company": result.get("is_foreign_company", False),
                "is_small_company": result.get("is_small_company", False)
            }
            return ordered_result
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Original output: {result_text}")
            return None
        finally:
            time_end = time.time()
            print(f'used time: {time_end - time_start} seconds')

if __name__ == "__main__":
    llm_model = LLM_model(api_key='sk-52622bdf335b421897f5d2bbfb1ab15c', base_url="https://api.deepseek.com")
    user_input_file = 'Data_Base/Business_Analysis_en.json'
    user_data_base = read_json(user_input_file)
    user_input_list = []
    for index, item in enumerate(user_data_base[:30]):
        user_input_list.append({
            "index": index,
            "job_details_content": item.get("job_details_content", "")
        })
    result = llm_model.get_json_response(user_input_list, 'Job_Matching_Prompt')
    result = json.loads(result)
    write_json('Job_Matching_Result.json', result)
    print(result)