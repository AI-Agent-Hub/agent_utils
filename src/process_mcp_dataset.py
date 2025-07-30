# -*- coding: utf-8 -*-
# @Time    : 2025/06/27

import codecs
import json
from prompts.base_prompts import *
import time
import requests

def read_file(file_path):
    lines = []
    lines_clean = []
    try:
        with codecs.open(file_path, "r", "utf-8") as file:
            lines = file.readlines()
        for line in lines:
            line_clean = line.strip()
            line_clean = line_clean.replace("\n", "")
            lines_clean.append(line_clean)
    except Exception as e:
        print ("DEBUG: read_file failed file_path %s" % file_path)
        print (e)
    return lines_clean

def save_file(file_path, lines, if_append=False):
    if if_append:
        with codecs.open(file_path, "a", "utf-8") as file:
            for line in lines:
                file.write(line + "\n")
        file.close()
    else:
        with codecs.open(file_path, "w", "utf-8") as file:
            for line in lines:
                file.write(line + "\n")
        file.close()

def call_qwen_user_prompt_model_selection(user_prompt, model):
    """
        Reference doc: https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api#b30677f6e9437
    """
    try:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        api_key = settings.QWEN_API_KEY
        if api_key is None:
            raise ValueError("qwen_general_api.py call_qwen_max_user_prompt api_key not found, please check .env file key QWEN_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        data = json.dumps(data).encode("utf-8")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("Qwen Response:", result["choices"][0]["message"]["content"])
        else:
            print(f"API Return Failed with Status (Status Code: {response.status_code}): {response.text}")
        return response
    except Exception as e:
        logging.error(e)
        return None


def process_mcp_category(input_server_file, input_category_meta, output_server_file):
    """
    """
    model_selection = "qwen-max"
    servers_meta = read_file(input_server_file)
    category_info = read_file(input_category_meta)
    category_list = []
    category_description_dict = {}
    for line in category_info:
        pairs = line.split("|")
        if len(pairs) == 2:
            category_name = pairs[0]
            category_description = pairs[1]
            category_list.append(category_name)
            category_description_dict[category_name] = category_description
    print (f"DEBUG: category_list {category_list}")
    print (f"DEBUG: category_description_dict {category_description_dict}")

    category_tags_str = ",".join(category_list)
    print (f"Category Tags is {category_tags_str}")
    for i, line in enumerate(servers_meta):
        item_json = {}
        try:
            item_json = json.loads(line)
        except Exception as e:
            print (e)
        server_id = item_json["id"] if "id" in item_json else ""
        content_name = item_json["content_name"] if "content_name" in item_json else ""
        website = item_json["website"] if "website" in item_json else ""
        content = item_json["content"] if "content" in item_json else ""
        category = item_json["category"] if "category" in item_json else ""
        category_norm = category.lower()
        ## tag categgory
        if category_norm == "" or category_norm == "developer" or category_norm == "mcp server":
            user_prompt = category_prediction_prompts.format(category_tags=category_tags_str, category_description_dict=str(category_description_dict), content=content)
            try:
                response = call_qwen_user_prompt_model_selection(user_prompt, model_selection)
                content = response.content.decode()
                result_json = {}
                try:
                    content_json = json.loads(content) 
                    message = content_json['choices'][0]['message']
                    msg_content = message['content'] if 'content' in message else ''
                    msg_content_clean = msg_content.replace("```json", "")
                    msg_content_clean = msg_content_clean.replace("```", "")
                    msg_content_clean = msg_content_clean.replace("\n", "")
                    result_json = json.loads(msg_content_clean) 
                except Exception as e1:
                    print (f"Error Result {content}")
                    print (e1)
                print (f"DEBUG: Processing Line {i} server_id {server_id} result_json {result_json}")
                category = result_json["category"] if "category" in result_json else ""
                description = result_json["description"] if "description" in result_json else ""
                item_json["category"] = category
                item_json["description"] = description
            except Exception as e:
                print (e)
        output_lines = [json.dumps(item_json)]
        save_file(output_server_file, output_lines, if_append=True)
        time.sleep(2)

def get_unique_id(website):
    if website is None:
        return ""
    if "github" not in website:
        return website
    else:
        pattern_github_repo_path = r"https://github.com/([^/]+)/(\S+)"    

        owner_id = ""
        repo_name = ""
        match_tuple_list = re.findall(pattern_github_repo_path, website)
        
        for match in match_tuple_list:
            if len(match) < 2:
                continue
            owner_id = match[0]
            repo_name = match[1]
        unique_id = "%s/%s" % (owner_id, repo_name)
        return unique_id

def get_mcp_official_category():

    input_file_official = "./mcp/meta/official_mcp_server_20250728.json"
    input_official_dict = json.loads(read_file(input_file_official)[0])

    input_official = input_official_dict["items"] if "items" in input_official_dict else []

    input_meta = "./mcp/meta/mcp_server_list_0616.json"
    item_info_dict = {}
    for line in read_file(input_meta):
        item_json = json.loads(line)
        category = item_json["category"] if "category" in item_json else ""
        description = item_json["description"] if "description" in item_json else ""
        item_id = item_json["id"] if "id" in item_json else ""
        item_info_dict[item_id] = {"category": category, "description": description}

    input_official_append = []
    for item_json in input_official:
        website = item_json["website"] if "website" in item_json else ""
        item_id = get_unique_id(website)
        item_info = item_info_dict[item_id] if item_id in item_info_dict else {}
        category = item_info["category"] if "category" in item_info else ""
        description = item_info["description"] if "description" in item_info else ""
        
        item_json["id"] =  item_id
        item_json["category"] = category
        item_json["description"] = description
        input_official_append.append(item_json)

    save_file("./mcp/meta/official_mcp_server_category_20250728.json", [json.dumps(input_official_append)])

    group_by_dict = {}
    for item_json in input_official_append:
        category = item_json["category"] if "category" in item_json else "DEFAULT"

        if category in group_by_dict:
            item_list = group_by_dict[category]
            item_list.append(item_json)
            group_by_dict[category] = item_list
        else:
            group_by_dict[category] = [item_json]
    ## 
    for category in group_by_dict.keys():
        item_list = group_by_dict[category]
        for item_json in item_list:
            line = "\t".join([category, item_json["id"]])
            print (line)

def get_statistic(input_server_file, output_server_file):
    """
        input_server_file: 
    """
    skip_category = "DEVELOPER"
    missing_category = "MISSING"
    servers_meta = read_file(input_server_file)
    print (f"servers_meta Total Cnt is {len(servers_meta)}")
    category_cnt_dict = {}
    missing_server_id = []

    output_list = []
    for i, line in enumerate(servers_meta):
        item_json = {}
        try:
            item_json = json.loads(line)
        except Exception as e:
            print (e)
        server_id = item_json["id"] if "id" in item_json else ""
        category_str = item_json["category"] if "category" in item_json else ""
        category_norm = ""
        if category_str == "":
            missing_server_id.append(server_id)
        else:
            category_list = category_str.upper().split(",")
            if skip_category in category_list:
                category_list.remove(skip_category)
            if missing_category in category_list:
                category_list.remove(missing_category)
            # first category
            category = category_list[0] if len(category_list) > 0 else ""
            category_norm = category.upper()
            if category_norm != "" and category_norm in category_cnt_dict:
                cnt = category_cnt_dict[category_norm]
                cnt += 1
                category_cnt_dict[category_norm] = cnt
            else:
                category_cnt_dict[category_norm] = 1
        ## update
        item_json["category"] = category_norm
        output_list.append(json.dumps(item_json))
    category_cnt_dict["MISSING"] = len(missing_server_id)
    print ("| Category | Cnt |")
    print ("| ---- | ---- |")
    for key, value in category_cnt_dict.items():
        print ("| %s | %s |" % (key, value))

    print ("DEBUG: missing_server_id size %d" % len(missing_server_id))
    # for server_id in missing_server_id:
    #     print (server_id)
    if output_server_file is not None:
        save_file(output_server_file, output_list)

def preprocess_official_file(input_server_file, output_server_file):
    """
    """
    item_json_dict = json.loads(read_file(input_server_file)[0])
    item_json_list = item_json_dict["items"] if "items" in item_json_dict else []
    output_lines = []
    for item_json in item_json_list:
        output_lines.append(json.dumps(item_json))
    save_file(output_server_file, output_lines)

def merge_file_description(file_list, output_file):

    merge_dict = {}
    for file in file_list:
        lines = read_file(file)
        for line in lines:
            item_json = json.loads(line)
            content_name = item_json["content_name"]
            category = item_json["category"]
            description = item_json["description"]
            website = item_json["website"] if "website" in item_json else ""
            content_tag_list = item_json["content_tag_list"] if "content_tag_list" in item_json else ""
            item_id = get_unique_id(website)
            item_json_output = {
                "id": item_id,
                "content_name": content_name,
                "cateogry": category,
                "description": description,
                "content_tag_list": content_tag_list
            }
            if item_id not in merge_dict:
                merge_dict[item_id] = item_json_output
    output_items = [json.dumps(v) for k, v in merge_dict.items()]
    save_file(output_file, output_items)

def main():
    input_server_file = "./mcp/meta/official_mcp_server_20250728.json"
    input_category_meta = "./mcp/meta/meta_category.txt"
    output_server_file = "./mcp/meta/official_mcp_server_20250728_with_category.json"

    # preprocess_official_file("./mcp/meta/official_mcp_server_20250728.json", "./mcp/meta/official_mcp_server_list_20250728.json")
    process_mcp_category("./mcp/meta/official_mcp_server_list_20250728.json", input_category_meta, output_server_file)
    merge_file_description(["./mcp/meta/mcp_server_list_0616.json", "./mcp/meta/official_mcp_server_20250728_with_category.json"], "./mcp/meta/mcp_category_description.json")
    # get_statistic("./mcp/meta/mcp_server_list_0616.json", None)

if __name__ == '__main__':
    main()
