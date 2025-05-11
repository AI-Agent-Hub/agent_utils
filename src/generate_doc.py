# -*- coding: utf-8 -*-

import codecs
import re
import json
import os
import random
import time

from constants import *
from data_utils import *
from requests_utils import *
from fetch_ai_agent import process_main_page_aigc_content, get_merge_all_data_ai_agent, read_fetch_whitelist_path, read_category_meta, read_fetch_whitelist_path

from bs4 import BeautifulSoup
from func_timeout import func_set_timeout, FunctionTimedOut
import ai_agent_marketplace as aa

def read_file(file_path):
    lines = []
    with codecs.open(file_path, "r", "utf-8") as file:
        lines = file.readlines()
    lines_clean = []
    for line in lines:
        line_clean = line.replace("\n", "")
        lines_clean.append(line_clean)
    return lines_clean

def save_file(file_path, lines):
    with codecs.open(file_path, "w", "utf-8") as file:
        for line in lines:
            file.write(line + "\n")
    file.close()

def read_category_meta(input_file):
    lines = read_file(input_file)
    category_json_list = []
    ## k1: category_name, v1: list of queries
    query_append_dict = {}

    for line in lines:
        category_json = json.loads(line)
        category_json_list.append(category_json)

        category = category_json["category"] if "category" in category_json else []
        query_list = category_json["query_list"] if "query_list" in category_json else []
        query_append_dict[category] = query_list

    return category_json_list, query_append_dict

def generate_agent_seo_url(args):

    input_file = args.input_file
    print ("DEBUG: generate_agent_seo_url input file %s" % input_file)
    # history_listed_path = "./data/agent_meta/history_listed_items.json"
    history_append_dict_whitelist, category_history_dict = read_fetch_whitelist_path(input_file)
    category_list = list(category_history_dict.keys())

    base_url = "http://www.deepnlp.org/store/ai-agent/"
    url_list = []
    for category_name in category_list:
        url = base_url + get_sug_by_name(category_name)
        url_list.append((category_name, url))
    ## process url_list
    for (category_name, url) in url_list:
        ## 
        print ("## " + category_name)        
        print (url)
        print ("")

def generate_readme_intro_lines(category):
    ## 
    """
        README not specify data
    """    
    intro_line_template ="""
# %s Agent Meta and Traffic Dataset in AI Agent Marketplace | AI Agent Directory | AI Agent Index from DeepNLP

This dataset is collected from AI Agent Marketplace Index and Directory at http://www.deepnlp.org, which contains AI Agents's meta information such as agent's name, website, description, as well as the monthly updated Web performance metrics, including Google,Bing average search ranking positions, Github Stars, Arxiv References, etc.
The dataset is helpful for AI researchers and practitioners to do analysis, write reports, monitor the trends and track the exponentially growth (though flat) of number of AI Agents in all fields.

To add and list your agent to the Agent Index, please visit [AI Agent Directory](http://www.deepnlp.org/store/ai-agent), use the the workspace [http://www.deepnlp.org/workspace/my_ai_services](http://www.deepnlp.org/workspace/my_ai_services) or using python API

To Search all agents, please use AI Agent Search Engine [Agent Search Engine](http://www.deepnlp.org/search/agent)

[Github AI Agent Marketplace](https://github.com/AI-Agent-Hub/AI-Agent-Marketplace)

[Pypi AI Agent Marketplace](https://pypi.org/project/ai-agent-marketplace/)

![AI Agent Marketplace Directory Search](%s)

# Data Samples
"""
    
    image_url = "https://raw.githubusercontent.com/AI-Agent-Hub/AI-Agent-Marketplace/refs/heads/main/docs/image_email_writing_agents.jpg"
    intro_line = [intro_line_template % (category, image_url)]
    return intro_line    

def generate_readme(item_json, category):
    
    ## output
    name = item_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in item_json else ""
    website = item_json[KEY_WEBSITE] if KEY_WEBSITE in item_json else ""
    description = item_json[KEY_DESCRIPTION] if KEY_DESCRIPTION in item_json else ""
    category = item_json[KEY_SUBFIELD] if KEY_SUBFIELD in item_json else ""
    tags = item_json[KEY_CONTENT_TAG_LIST] if KEY_CONTENT_TAG_LIST in item_json else ""
    publisher_id = item_json[KEY_PUBLISHER_ID] if KEY_PUBLISHER_ID in item_json else ""
    detail_url = "http://www.deepnlp.org/store/ai-agent/%s/%s/%s" % (get_sug_by_name(category), get_sug_by_name(publisher_id), get_sug_by_name(name))

    data_readme = []
    data_readme.append("")
    data_readme.append("## [%s](%s)" % (name, website))
    data_readme.append("<details>")
    data_readme.append("")
    data_readme.append("### website")
    data_readme.append(website)
    data_readme.append("### Agent Page")    
    data_readme.append(detail_url)
    data_readme.append("### description")
    data_readme.append(description)
    data_readme.append("### category")
    data_readme.append(category)
    data_readme.append("### tags")
    data_readme.append(tags)
    data_readme.append("")
    data_readme.append("</details>")  
    data_readme.append("")     

    return data_readme


def generate_blog_intro_lines(category):
    intro_line_template = """
%s 2025 March Web Traffic Metric Complete Reports Google Bing Similarweb

In this report, we will introduce the latest web performance of %s in 2025 March. The number of AI Agents is increasing rapidly. And this list is collected from AI Agent Marketplace Index and Directory at http://www.deepnlp.org/store/ai-agent, which contains more than 3000 AI Agents and their monthly updated web performance metrics, including Google,Bing average search ranking positions, Github Stars, Arxiv References, etc.
It is helpful for AI practitioners to do analysis, write reports, monitor the trends and track the exponentially growth (though flat) of number of AI Agents in all fields.
To see the complete list and traffic performance, please visit AI Agent Directory (http://www.deepnlp.org/store/ai-agent) and explore more.
To search all agents and get detailed metric, please use the [Agent Search Engine](http://www.deepnlp.org/search/agent)
To add and list your agent to the Agent Index, please visit use the the workspace [http://www.deepnlp.org/workspace/my_ai_services](http://www.deepnlp.org/workspace/my_ai_services) or using python API
Github:https://github.com/AI-Agent-Hub/AI-Agent-Marketplace
Pypi AI Agent Marketplace:https://pypi.org/project/ai-agent-marketplace
%s Complete List: http://www.deepnlp.org/store/ai-agent/%s
    """
    intro_line = [intro_line_template % (category, category, category, get_sug_by_name(category))]
    return intro_line    

def generate_blog_intro_lines_zh(category):
    ## 
    intro_line_template = """%s 25年3月AI智能体Top 100流量报告 DeepNLP AI Agent Index Directory Marketplace

在这份报告中我们覆盖 AI Agent %s 赛道, 25年3月Top 100 Agent 在全网 Web端流量的监控，Web Traffic流量监控的 Metric包含了Google/Bing等搜索引擎平均排名 (Average Position), SimilarWeb, Github Stars等流量数据的指标。对于AI从业者进行行业研究，研发计划，政策制定，投资分析汇总，趋势预测和监控等提供更好的数据服务。

- %s 全网完整列表Complete List: http://www.deepnlp.org/store/ai-agent/%s

访问AI Agent Marketplace AI Agent Directory，地址：http://www.deepnlp.org/store/ai-agent
Agent搜索引擎找到领域AI Agent，地址：http://www.deepnlp.org/search/agent
注册添加到 AI Agent Index，登录网页版：http://www.deepnlp.org/workspace/my_ai_services，或者使用 Python API (https://github.com/AI-Agent-Hub/AI-Agent-Marketplace)

Github：https://github.com/AI-Agent-Hub/AI-Agent-Marketplace
Pypi：https://pypi.org/project/ai-agent-marketplace, https://pypi.org/project/ai-agent-index
"""

    intro_line = [intro_line_template % (category, category, category, get_sug_by_name(category))]
    return intro_line    

def generate_blog(id, item_json, category):
    """
    """
    ## output
    name = item_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in item_json else ""
    website = item_json[KEY_WEBSITE] if KEY_WEBSITE in item_json else ""
    description = item_json[KEY_DESCRIPTION] if KEY_DESCRIPTION in item_json else ""
    category = item_json[KEY_SUBFIELD] if KEY_SUBFIELD in item_json else ""
    tags = item_json[KEY_CONTENT_TAG_LIST] if KEY_CONTENT_TAG_LIST in item_json else ""
    publisher_id = item_json[KEY_PUBLISHER_ID] if KEY_PUBLISHER_ID in item_json else ""
    
    statistic_dict = item_json[KEY_STATISTIC] if KEY_STATISTIC in item_json else ""
    statistic_list = []
    for key, value in statistic_dict.items():
        statistic_list.append(str(key) + ":" + str(value))
    statistic_str = ",".join(statistic_list)

    detail_url = "http://www.deepnlp.org/store/ai-agent/%s/%s/%s" % (get_sug_by_name(category), get_sug_by_name(publisher_id), get_sug_by_name(name))

    data_readme = []
    data_readme.append("")
    data_readme.append("%d. %s" % (id, name))
    data_readme.append("")  
    data_readme.append("Website:" + website)
    data_readme.append("")
    data_readme.append("Agent Page:" + detail_url)
    data_readme.append("")    
    data_readme.append("metric:" + statistic_str)
    data_readme.append("")
    data_readme.append("description:" + description)
    data_readme.append("")
    data_readme.append("category:" + category)
    data_readme.append("")

    return data_readme

def generate_blog_zh(id, item_json, category):
    """
    """
    ## output
    name = item_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in item_json else ""
    website = item_json[KEY_WEBSITE] if KEY_WEBSITE in item_json else ""
    description = item_json[KEY_DESCRIPTION] if KEY_DESCRIPTION in item_json else ""
    category = item_json[KEY_SUBFIELD] if KEY_SUBFIELD in item_json else ""
    tags = item_json[KEY_CONTENT_TAG_LIST] if KEY_CONTENT_TAG_LIST in item_json else ""
    publisher_id = item_json[KEY_PUBLISHER_ID] if KEY_PUBLISHER_ID in item_json else ""

    detail_url = "http://www.deepnlp.org/store/ai-agent/%s/%s/%s" % (get_sug_by_name(category), get_sug_by_name(publisher_id), get_sug_by_name(name))

    statistic_dict = item_json[KEY_STATISTIC] if KEY_STATISTIC in item_json else ""
    statistic_list = []
    for key, value in statistic_dict.items():
        statistic_list.append(str(key) + ":" + str(value))
    statistic_str = ",".join(statistic_list)

    data_readme = []
    data_readme.append("")
    data_readme.append("%d. %s" % (id, name))
    data_readme.append("")
    data_readme.append("指标:" + statistic_str)
    data_readme.append("网址:" + website)
    data_readme.append("Agent详情页:" + detail_url)
    data_readme.append("描述:" + description)
    data_readme.append("类目:" + category)
    return data_readme

def fetch_meta_data():

    input_file = "./data/agent_category_meta.json"
    # input_file = "./agent_category.txt"
    category_json_list, query_append_dict_category = read_category_meta(input_file)
    category_list = [category_json["category"] for category_json in category_json_list]
    output_dict_list = []
    for category in category_list:
        # if category != "Coding Agent":
        #     continue
        result_dict = get_ai_agent_by_category(category)
        output_dict_list.append(json.dumps(result_dict))
        time.sleep(3)

    ## procees_to_item_list
    save_file("./data/output/20250327/data_agent_raw_202503.json", output_dict_list)

def generate_dataset_spit_and_readme(args):

    # input_file = args.input_file 
    input_file = "./data/agent_meta/history_listed_items.json"
    print ("DEBUG: generate_dataset_spit_and_readme input_file %s" % input_file)
    input_lines = read_file(input_file)
    month = args.month
    dt = args.date
    print ("DEBUG: generate_dataset_spit_and_readme input month %d|date %d" % (month, dt))

    all_output_list = []
    readme_sample_size = 20
    ## process data_by_line
    for category_json_str in input_lines:
        
        ## process_output_data
        category_output = []
        ## process readme
        category_json = json.loads(category_json_str)
        category = category_json["category"] if "category" in category_json else ""
        items = category_json["items"] if "items" in category_json else []
        cnt = 0

        readme_list = []
        readme_list.extend(generate_readme_intro_lines(category))
        for item in items:
            cnt += 1
            item[KEY_MONTH] = month
            # clean content 
            content = item[KEY_CONTENT] if KEY_CONTENT in item else ""
            content_clean = content.replace("<h4>", "") 
            content_clean = content_clean.replace("</h4>", "") 
            content_clean = content_clean.replace("<h3>", "") 
            content_clean = content_clean.replace("</h3>", "") 
            content_clean = content_clean.replace("<h2>", "") 
            content_clean = content_clean.replace("</h2>", "")
            content_clean = content_clean.replace("<img>", "") 
            content_clean = content_clean.replace("</img>", "") 
            item[KEY_CONTENT] = content_clean
            # output 1
            category_output.append(json.dumps(item))
            all_output_list.append(json.dumps(item))
            # output 2
            if cnt <= readme_sample_size:
                readme_list.extend(generate_readme(item, category))

        output_file = "./data/output/%s/data_agent_%s_202503.json" % (dt, get_sug_by_name(category))
        save_file(output_file, category_output)

        ## process readme
        output_file = "./data/output/%s/data_agent_%s_202503.md" % (dt, get_sug_by_name(category))
        save_file(output_file, readme_list)

    ## save
    output_file = "./data/output/%s/data_agent_all_202503.json" % dt
    save_file(output_file, all_output_list)

def get_normalize_category(category_name):
    """
    """
    category_name_norm = ""
    if "agent" not in category_name.lower():
        category_name_norm = category_name + " AI Agent"
    else:
        category_name_norm = category_name
    return category_name_norm

def generate_blog_data(args):
    """
    """
    lang = args.lang
    input_file = args.input_file
    date = args.date
    month = args.month 

    print ("DEBUG: generate_blog_data input args input_file|%s" % input_file)
    print ("DEBUG: generate_blog_data input args lang code|%s" % lang)
    print ("DEBUG: generate_blog_data input args date|%s" % date)
    print ("DEBUG: generate_blog_data input args month|%s" % month)

    input_lines = read_file(input_file)
    all_output_list = []
    ## process data_by_line
    for category_json_str in input_lines:

        category_json = json.loads(category_json_str)
        category = category_json["category"] if "category" in category_json else ""
        category_name_norm = get_normalize_category(category)

        doc_list = []
        if lang == "en":
            doc_list.extend(generate_blog_intro_lines(category_name_norm))
        elif lang == "zh":
             doc_list.extend(generate_blog_intro_lines_zh(category_name_norm))
        else :
            print ("DEBUG: Lang Code not supported %s" % lang)

        items = category_json["items"] if "items" in category_json else []
        cnt = 0
        ## 
        for i, item in enumerate(items):
            if lang == "en":
                doc_list.extend(generate_blog(i+1, item, category_name_norm))
            elif lang == "zh":
                doc_list.extend(generate_blog_zh(i+1, item, category_name_norm))
            else:
                continue
        ## process readme
        output_file = "./data/output/%s/data_agent_%s_blog_%s.txt" % (date, get_sug_by_name(category), lang)
        save_file(output_file, doc_list)

def test_generate_search_result():
    import requests

    url = "http://www.deepnlp.org/api/ai_agent_marketplace/v1?category=Coding%20Agent&limit=1000&return_fields=statistic"
    timeout = 10
    result = requests.get(url, timeout=timeout)
    data = result.json()


    items = data["items"] if "items" in data else []


    type(result)

def generate_huggingface_dataset():
    """
    """
    base_huggingface = "https://huggingface.co/DeepNLP/%s"

    input_file = "./data/agent_category_meta.json"
    # input_file = "./agent_category.txt"
    category_json_list, query_append_dict_category = read_category_meta(input_file)
    category_list = [category_json["category"] for category_json in category_json_list]
    dataset_url_list = []
    for category in category_list:
        category_name_norm = get_normalize_category(category)
        dataset_url = base_huggingface % get_sug_by_name(category_name_norm)
        dataset_url_list.append(dataset_url)
    for url in dataset_url_list:
        print (url)

def main():
    """
        ## generate_blog_data
        python3 generate_doc.py --mode "blog" --date "20250411" --input_file "./data/agent_meta/history_listed_items.json" --lang "zh" 
        python3 generate_doc.py --mode "blog" --date "20250411" --input_file "./data/agent_meta/history_listed_items.json" --lang "en" 

        ## generate docs
        ### download data
        python3 process_ai_agent.py process_history_ai_agents_data()
        ### generate docs
        python3 generate_doc.py --mode "markdown"
    
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', type=str, default="", help='Input Mode of Functions')
    parser.add_argument('--input_file', type=str, default="", help='Input File of Category Listed Items')
    parser.add_argument('--lang', type=str, default="en", help='Language for Reports')
    parser.add_argument('--date', type=str, default="", help='date of runing scripts')
    parser.add_argument('--month', type=str, default="", help='month of generating blogs')

    args = parser.parse_args()
    lang = args.lang
    mode = args.mode
    date = args.date

    print ("DEBUG: Input mode %s" % args.mode)
    print ("DEBUG: Input lang %s" % args.lang)
    print ("DEBUG: Input date %s" % args.date)

    if mode == "blog":
        generate_blog_data(args)
    elif mode == "markdown":
        generate_dataset_spit_and_readme(args)
    else:
        print ("DEBUG: Current Mode Not Supported %s" % mode)

if __name__ == '__main__':
    main()    
