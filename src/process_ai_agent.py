# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import codecs
import re
import json
import os
import random
import time

from constants import *
from data_utils import *
from requests_utils import *
from fetch_ai_agent import process_main_page_aigc_content, get_merge_all_data_ai_agent, read_fetch_whitelist_path

import emoji

from bs4 import BeautifulSoup
from func_timeout import func_set_timeout, FunctionTimedOut
import ai_agent_marketplace

def read_file(file_path):
    lines_clean = []
    try:
        lines = []
        with codecs.open(file_path, "r", "utf-8") as file:
            lines = file.readlines()
        for line in lines:
            line_clean = line.replace("\n", "")
            lines_clean.append(line_clean)
    except Exception as e:
        print (e)
    return lines_clean

def save_file(file_path, lines):
    try:
        with codecs.open(file_path, "w", "utf-8") as file:
            for line in lines:
                file.write(line + "\n")
        file.close()
    except Exception as e:
        print (f"Failed to save file {file_path}")
        print (e)

def process_ai_agents_employees():
    """
    """
    data_file = "./raw_agent_employees.md"
    lines = read_file(data_file)
    output_json_list = []
    output_readme_list = []

    category = "Workplace"
    for line in lines:
        if line.startswith("#"):
            continue
        items = line.split("|")

        data_json = {}
        data_readme = []
        if len(items) > 5:
            name = items[1]
            website = items[2]
            description = items[3]
            tags = items[4]

            data_json["name"] =  name
            data_json["website"] =  website
            data_json["description"] =  description
            data_json["tags"] =  tags
            data_json["category"] = category
            output_json_list.append(json.dumps(data_json))

            data_readme.append("## [%s](%s)" % (name, website))
            data_readme.append("<details>")
            data_readme.append("")
            data_readme.append("### website")
            data_readme.append(website)
            data_readme.append("### description")
            data_readme.append(description)
            data_readme.append("### category")
            data_readme.append(category)
            data_readme.append("### tags")
            data_readme.append(tags)
            data_readme.append("")
            data_readme.append("</details>")  
            data_readme.append("")          
            output_readme_list.extend(data_readme)

    ## output 
    save_file("./data/agent_employees.json", output_json_list)
    save_file("./data/agent_employees.md", output_readme_list)


def is_new_section(line, prefix="## "):
    if line.startswith(prefix):
        return True
    else:
        return False

def process_ai_agents_finance():
    """ 
    """
    data_file = "./raw_finance_agent.md"
    lines = read_file(data_file)
    output_json_list = []
    output_readme_list = []

    pattern = r"\[\s*(.*?)\s*\]\((.*?)\)"

    section_list = []
    section = []
    for line in lines:
        if is_new_section(line, prefix="## "):
            ## append current section to list
            section_list.append(section)
            section = []
            section.append(line)
        else:
            section.append(line)
    print ("DEBUG: Generating Section List Size %d" % len(section_list))

    section_dict_list = []
    for section in section_list:
        section_dict = {}
        key = ""
        value = ""
        for line in section:
            if line.startswith("## "):
                # save old section
                line_clean = line.replace("##", "").strip()
                meta_info = line_clean
                match = re.search(pattern, meta_info)
                if match:
                    item_name = match.group(1)  # The text inside the square brackets
                    item_url = match.group(2)   # The URL inside the parentheses
                    section_dict["name"] = item_name
                    section_dict["website"] = item_url
            elif line.startswith("###"):
                key = line.replace("###", "").strip()
            elif (line == "<details>" or line == "</details>" or line == ""): 
                continue
            else:
                value = line.strip()
                ## update
                if key != "" and value != "":
                    section_dict[key] = value
                    key = ""
                    value = ""
        ## 
        section_dict_list.append(json.dumps(section_dict))
    ## append last one
    # section_dict_list.append(json.dumps(section_dict))
    print ("DEBUG: section_dict_list size %d" % len(section_dict_list))
    ## output
    save_file("./data/agent_finance.json", section_dict_list)


def parse_name_url(input):
    """
        input format   [name](url)
        [IBM Watson Health](https://www.ibm.com/industries/healthcare)
    """
    pattern = r"\[\s*(.*?)\s*\]\((.*?)\)"
    match = re.search(pattern, input)
    output_dict = {}
    if match:
        name = match.group(1)  # The text inside the square brackets
        url = match.group(2)   # The URL inside the parentheses
        output_dict["name"] = name
        output_dict["url"] = url
    return output_dict

def process_ai_agent_healthcare():
    """
    """
    data_file = "./raw_healthcare_agent.md"
    lines = read_file(data_file)
    output_json_list = []
    output_readme_list = []

    category = "Heathcare"
    for line in lines:
        if line.startswith("#"):
            continue
        items = line.split("|")

        data_json = {}
        data_readme = []
        if len(items) > 4:

            tags = items[1].strip()
            name_url = items[2].strip()
            description = items[3].strip()

            output_dict = parse_name_url(name_url)
            name = output_dict["name"] if "name" in output_dict else ""
            website = output_dict["url"] if "url" in output_dict else ""

            data_json["name"] =  name
            data_json["website"] =  website
            data_json["description"] =  description
            data_json["tags"] =  tags
            data_json["category"] = category
            output_json_list.append(json.dumps(data_json))

            data_readme.append("## [%s](%s)" % (name, website))
            data_readme.append("<details>")
            data_readme.append("")
            data_readme.append("### website")
            data_readme.append(website)
            data_readme.append("### description")
            data_readme.append(description)
            data_readme.append("### category")
            data_readme.append(category)
            data_readme.append("### tags")
            data_readme.append(tags)
            data_readme.append("")
            data_readme.append("</details>")  
            data_readme.append("")          
            output_readme_list.extend(data_readme)

    ## output 
    save_file("./data/agent_healthcare.json", output_json_list)
    save_file("./data/agent_healthcare.md", output_readme_list)


def process_ai_agent_law():
    """
    """
    data_file = "./raw_law_agent.md"
    lines = read_file(data_file)
    output_json_list = []
    output_readme_list = []

    category = "Law"
    # tags = "Law,Legal"
    for line in lines:
        if line.startswith("#"):
            continue
        items = line.split("|")

        data_json = {}
        data_readme = []
        if len(items) > 4:

            name = items[1].strip()
            website = items[2].strip()
            description = items[3].strip()
            tags = items[4].strip()

            data_json["name"] =  name
            data_json["website"] =  website
            data_json["description"] =  description
            data_json["tags"] =  tags
            data_json["category"] = category
            output_json_list.append(json.dumps(data_json))

            data_readme.append("## [%s](%s)" % (name, website))
            data_readme.append("<details>")
            data_readme.append("")
            data_readme.append("### website")
            data_readme.append(website)
            data_readme.append("### description")
            data_readme.append(description)
            data_readme.append("### category")
            data_readme.append(category)
            data_readme.append("### tags")
            data_readme.append(tags)
            data_readme.append("")
            data_readme.append("</details>")  
            data_readme.append("")          
            output_readme_list.extend(data_readme)

    ## output 
    save_file("./data/agent_law.json", output_json_list)
    save_file("./data/agent_law.md", output_readme_list)


def process_ai_agent_education_clean():

    input_file = "./data/raw/raw_agent_education.json"
    lines = read_file(input_file)

    output_json_list = []
    output_readme_list = []

    category = "Education"
    # tags = "Law,Legal"
    for line in lines:
        input_json = json.loads(line)

        data_json = {}
        data_readme = []
        if len(input_json) > 0:
            name = input_json["repo_name"]
            website = input_json["url"]
            description = input_json["description"]
            tags = "Education"
            github = input_json["url"]
            star = input_json["repo_star"] if "repo_star" in input_json else "0"

            print ("DEBUG: star %d" % int(star))

            if int(star) < 5:
                print ("Skipped...")
                continue
            else:
                print ("Passed...")

            data_json["name"] =  name
            data_json["website"] =  website
            data_json["description"] =  description
            data_json["tags"] =  tags
            data_json["category"] = category
            data_json["github"] = github

            output_json_list.append(json.dumps(data_json))

            data_readme.append("## [%s](%s)" % (name, website))
            data_readme.append("<details>")
            data_readme.append("")
            data_readme.append("### website")
            data_readme.append(website)
            data_readme.append("### description")
            data_readme.append(description)
            data_readme.append("### category")
            data_readme.append(category)
            data_readme.append("### tags")
            data_readme.append(tags)
            data_readme.append("### github")
            data_readme.append(github)            
            data_readme.append("")
            data_readme.append("</details>")  
            data_readme.append("")          
            output_readme_list.extend(data_readme)

    ## output 
    save_file("./data/agent_education.json", output_json_list)
    save_file("./data/agent_education.md", output_readme_list)

def get_sug_by_name(content_name):
    """
        seperator: " ", "."
    """
    import re
    content_name_lower = content_name.lower()
    content_name_lower_seg = re.split(r'[ .]+', content_name_lower)

    content_name_sug = "-".join(content_name_lower_seg)
    return content_name_sug


github_icon_readme_small_url = "https://th.bing.com/th?id=ODLS.b2099a11-ca12-45ce-bede-5df940e38a48&w=32&h=32&qlt=90&pcl=fffffc&o=6&pid=1.2"

def process_data_line_to_markdown(input_json):
    """
        args: json
        output: list of str
    """
    content_name = input_json["content_name"] if "content_name" in input_json else ""
    repo_name = input_json["repo_name"] if "repo_name" in input_json else ""
    website = input_json["website"] if "website" in input_json else ""
    description = input_json["content"] if "content" in input_json else ""
    
    tags = input_json["content_tag_list"] if "content_tag_list" in input_json else ""
    image_path = input_json["thumbnail_picture"] if "thumbnail_picture" in input_json else ""

    if "githubassets.com" in image_path:
        # change to small log
        image_path = github_icon_readme_small_url

    category = input_json["category"] if "category" in input_json else ""

    ## links
    github_url = input_json["url"] if "url" in input_json else ""
    star = input_json["repo_star"] if "repo_star" in input_json else "0"

    image_line = "![thumbnail_picture](%s)" % image_path if image_path != "" else ""

    publisher_id = input_json["publisher_id"] if "publisher_id" in input_json else ""
    publisher_id = "pub-" + publisher_id if "pub-" not in publisher_id else publisher_id
    content_name_url = get_sug_by_name(content_name)
    field = input_json["field"] if "field" in input_json else ""
    field_url = get_sug_by_name(field)
    subfield = input_json["subfield"] if "subfield" in input_json else ""
    subfield_url = get_sug_by_name(subfield)
    review_url = "http://www.deepnlp.org/store/%s/%s/%s/%s" % (field_url, subfield_url, publisher_id, content_name_url)
    reviews = "[%s Reviews Traffic and AI Agent Marketplace](%s)" % (content_name, review_url)

    data_readme = []
    data_readme.append("## [%s](%s)" % (content_name, website))
    data_readme.append(image_line)
    data_readme.append("")    
    data_readme.append(description)
    data_readme.append("<details>")
    data_readme.append("")
    data_readme.append("### Website")
    data_readme.append(website)
    data_readme.append("### Description")
    data_readme.append(description)
    data_readme.append("### Category")
    data_readme.append(category)
    data_readme.append("### Tags")
    data_readme.append(tags)
    data_readme.append("### Reviews")
    data_readme.append(reviews)
    data_readme.append("### Links")
    if github_url != "":
        data_readme.append(github_url + "<br>") 
    if website != "":
        data_readme.append(website + "<br>")
    if review_url != "":
        data_readme.append(review_url + "<br>")
    data_readme.append("")
    data_readme.append("</details>")  
    data_readme.append("")              
    return data_readme

def process_merge_ai_agent_file():
    """
        group_markdown_json: dict key: category_name, value: list of data_json
    """
    data_file_list = [
        "./data/merge/20250225/merge_bing_data.json",
        "./data/merge/20250225/merge_google_data.json",
        "./data/merge/20250224/merge_google_data.json",
        "./data/merge/2025223/merge_google_data.json",
        "./data/merge/2025222/merge_google_data.json",
        "./data/merge/2025222/merge_bing_data.json",
        "./data/merge/2025219/merge_google_data.json",
        ]
    
    input_file = "./data/agent_category.txt"
    # input_file = "./agent_category.txt"
    category_list = read_file(input_file)
    category_list_clean = []
    for category_name in category_list:
        category_name_norm = category_name.lower()
        category_list_clean.append(category_name_norm)
    print ("DEBUG: category_list_clean size %d" % len(category_list_clean))

    ## merge sub group, key: category_name_norm, value:list
    group_data_json = {}
    for file in data_file_list:
        data_lines = read_file(file)
        for line in data_lines:
            ## process one line 
            input_json = json.loads(line)
            category = input_json["category"] if "category" in input_json else ""

            if category in group_data_json:
                sublist = group_data_json[category]
                ## no dup
                publisher_id_list = [item_json["publisher_id"] for item_json in sublist]
                cur_publisher = input_json["publisher_id"]
                if cur_publisher not in publisher_id_list:
                    sublist.append(input_json)
                group_data_json[category] = sublist
            else :
                group_data_json[category] = [input_json]
    print ("DEBUG: group_data_json size %d" % len(group_data_json))

    ## bing data
    markdown_file_output = []
    # key: category_name, value: list of str, markdown
    group_markdown_json = {}
    for category_name_norm in group_data_json.keys():
        sublist = group_data_json[category_name_norm]
        category_name_norm_display = category_name_norm + " AGENT" if "agent" not in category_name_norm else category_name_norm
        markdown_file_output.append("# " + category_name_norm_display.upper())
        print ("DEBUG: Processing Category %s" % category_name_norm)

        sub_markdown_file_output = []
        for i, input_json in enumerate(sublist):
            if i % 5 == 0:
                print ("DEBUG: Processing Category sublist id %d" % i)
            readme_markdown = process_data_line_to_markdown(input_json)

            sub_markdown_file_output.extend(readme_markdown)
            sub_markdown_file_output.append("\n")

        markdown_file_output.extend(sub_markdown_file_output)
        group_markdown_json[category_name_norm] = sub_markdown_file_output
    save_file("./data/merge/2025216/merge_ai_agents.md", markdown_file_output)

    return group_markdown_json, group_data_json

def convert_category_to_keywords(category_name):
    category_name_norm = category_name
    if "agent" not in category_name.lower():
        category_name_norm = category_name + " " + "AI AGENT"
    return category_name_norm

def process_ai_agent_meta_mapping():
    category_file = "./data/agent_category.txt"
    category_list = read_file(category_file)
    output_list = []
    for category in category_list:

        category_info_dict = {}

        query_list = []
        # query_list.append(category)
        category_name_norm = convert_category_to_keywords(category)
        query_list.append(category_name_norm)
        
        category_info_dict["category"] = category
        category_info_dict["query_list"] = query_list
        output_list.append(json.dumps(category_info_dict))
    save_file("./data/agent_category_meta.json", output_list)

def process_ai_agents():
    
    # process_ai_agents_employees()
    # process_ai_agents_finance()
    # process_ai_agent_healthcare()
    # process_ai_agent_law()
    # process_ai_agent_education_clean()
    process_ai_agent_meta_mapping()

def merge_all_data_ai_agent():
    """
        Post Data AI Agent
        content_name,content_url,Image,Documentation,Discord,GitHub,content
        
        Required
             'publisher_id'： not required
             'content_name': required
             'content',  required
             'field', required
             'subfield', required
             'content_tag_list', required
             'website': required
        ## ai-hub-admin
        publisher
        
        # not working
    
        user_id
        pub_id
    """
    import requests
    data_file_folder = "../ai_agent_marketplace/data/merge"
    output_file = "../ai_agent_marketplace/data/merge/statistic/merge_ai_agent_statistic.json"
    ## process data_file_list
    data_file_list = []
    for sub_folder in os.listdir(data_file_folder):
        sub_folder_path = os.path.join(data_file_folder, sub_folder)
        if os.path.isdir(sub_folder_path):
            for file in os.listdir(sub_folder_path):
                data_file = os.path.join(sub_folder_path, file)
                if ".DS_Store" not in data_file:
                    data_file_list.append(data_file)
    print ("DEBUG: data_file_list size %d" % len(data_file_list))

    directory = {} ## KKV, K1L category, K2 content_name, value: list of json
    total_kv_cnt = 0
    for data_file in data_file_list:
        lines = read_file(data_file)
        for i, line in enumerate(lines):
            total_kv_cnt += 1

            output_json = None
            try:
                output_json = json.loads(line)
            except Exception as e:
                print (data_file)
                print (e)
            if output_json is None:
                continue
            # check if meet filter
            if filter_no_agent_json_bing(output_json):
                continue
            try:
                content_name = output_json["content_name"] if "content_name" in output_json else ""
                # website = output_json["website"] if "content_name" in output_json else ""
                category = output_json["category"] if "category" in output_json else ""
                if category in directory:
                    ## k1: content_name, v1 list of json
                    data_map = directory[category]
                    if content_name in data_map:
                        cur_data_series_list = data_map[content_name]
                        cur_data_series_list.append(output_json)
                        data_map[content_name] = cur_data_series_list
                    else:
                        data_map[content_name] = [output_json]
                else:
                    data_map = {}
                    data_map[content_name] = [output_json]
                    directory[category] = data_map
            except Exception as e:
                print (data_file)
                print (e)
    ## statistic
    total_content_name_cnt = 0
    for category in directory.keys():
        data_map = directory[category]
        content_size = len(data_map.keys())
        total_content_name_cnt += content_size
    print ("DEBUG: Total Input Json File Dup Cnt %d, total_content_name_cnt %s, category cnt %d" % (total_kv_cnt, total_content_name_cnt, len(directory)))

    ## Generate Data Series
    # k1: category
    # v1: dict, key: category_name, value: list of float
    # K1: category, K2: content_name
    output_data_series_list = []
    for category in directory.keys():
        ## k1: content_name, v1: list of value
        data_map = directory[category]
        output_statistic_map = {}
        ## content metric dict 
        content_map = {}
        for content_name in data_map.keys():
            ### get series_data of current content_name
            data_series = data_map[content_name]
            # key1: metric, value: list of (dt, value) pair
            metric_data_series_map = process_data_series(data_series)
            content_map[content_name] = metric_data_series_map
        ## 
        output_statistic_map["category"] = category
        output_statistic_map["data"] = content_map
        output_data_series_list.append(json.dumps(output_statistic_map))
    ## 
    save_file(output_file, output_data_series_list)

## missing, rather than >= 200
DEFAULT_RANK = 200  
## max_display >= 200
DISPLAY_RANK_TOP = 200

# 50?
def get_date():
    """
    """
    import datetime
    now = datetime.datetime.now()
    # today = datetime.date.today()
    # datetimestr = str(today.year) + str(today.month) + str(today.day)
    month_str = str(now.month)
    if len(month_str) == 1:
        month_str = "0%s" % month_str 

    day_str = str(now.day)
    if len(day_str) == 1:
        day_str = "0%s" % day_str 
    datetimestr = str(now.year) + month_str + day_str
    return datetimestr

def date_diff(start_date_value, end_date_value):
    """
        date -> str
    """
    from datetime import datetime
    date_format = "%Y%m%d"
    start_date = datetime.strptime(str(start_date_value), date_format)
    end_date = datetime.strptime(str(end_date_value), date_format)
    date_diff = end_date - start_date
    return date_diff.days

def date_minus(date_value, num_days):
    """
        str -> date
    """
    from datetime import datetime, timedelta
    date_format = "%Y%m%d"

    date = datetime.strptime(str(date_value), date_format)
    prev_date = date - timedelta(days= num_days)
    prev_date_str = prev_date.strftime("%Y%m%d")
    prev_date_int = int(prev_date_str)
    return prev_date_int 


def date_interator(start_date_value , end_date_value):
    """
        date
    """
    ## add int
    from datetime import datetime, timedelta
    date_format = "%Y%m%d"

    start_date = datetime.strptime(str(start_date_value), date_format)
    end_date = datetime.strptime(str(end_date_value), date_format)

    dt_list = []
    max_add_times = 100
    cnt = 0
    while start_date <= end_date and cnt < max_add_times:
        cnt += 1
        start_date_value = int(start_date.strftime("%Y%m%d"))
        dt_list.append(int(start_date_value))
        start_date += timedelta(days=1)
    return dt_list

def test_date_format():


    max_df = 20250406
    min_df = 20250406
    date_diff = date_diff(max_dt, min_dt)

    date_value = 20250406
    num_days = 10
    prev_date =date_minus(date_value, num_days)
    print ("DEBUG: prev_date is %s" % prev_date)


    start_date = 20250324
    end_date = 20250406
    date_list = date_interator(start_date, end_date)

def clip_valid_rank(rank_data):

    if rank_data <= 0:
        return DISPLAY_RANK_TOP
    if rank_data >= DISPLAY_RANK_TOP:
        return DISPLAY_RANK_TOP
    return rank_data

def process_data_series(data_series):
    """
        data_series
        source: Google Bing
        dt: various

        "source"
        "rank"
        "Google Rank"
        "Bing Rank"
    """

    google_rank_offset = 5.0

    ## get_average_value
    value_list = []
    for data_json in data_series:        
        source = data_json["source"] if "source" in data_json else ""
        rank = data_json["rank"] if "rank" in data_json else DEFAULT_RANK
        metric = ""
        if source == "google":
            metric = "Google Rank"
        elif source == "bing":
            metric = "Bing Rank"
        else:
            continue
            #print ("DEBUG: source not supported %s" % (source))
        if metric in data_json:
           value = data_json[metric]
           if value != 0 and value != DEFAULT_RANK:
                value_list.append(value)
    average_value = (1.0 * sum(value_list)/len(value_list)) if len(value_list) > 0 else DISPLAY_RANK_TOP

    # k1: metric
    # v1: list of float
    required_metric_list = ["Bing Rank", "Google Rank"]
    data_series_length = 7
    
    output_dict = {}
    for data_json in data_series:
        source = data_json["source"] if "source" in data_json else ""
        rank = data_json["rank"] if "rank" in data_json else DEFAULT_RANK
        metric = ""
        if source == "google":
            metric = "Google Rank"
        elif source == "bing":
            metric = "Bing Rank"
        else:
            continue
            # print ("DEBUG: source not supported %s" % (source))
        if metric in output_dict:
            data_list = output_dict[metric]
            data_list.append(data_json)
            output_dict[metric] = data_list
        else:
            data_list = [data_json]
            output_dict[metric] = data_list

    ## fill data
    output_dict_final = {}
    for metric in required_metric_list:
        data_list = output_dict[metric] if metric in output_dict else []
        ## merged values expand
        values_expand = [] 
        if len(data_list) == 0:
            ## exisitng
            end_dt = get_date()
            start_dt = date_minus(end_dt, data_series_length)
            ## append average value for empty 
            for dt in date_interator(start_dt, end_dt):
                value_dummy = average_value
                if metric == "Google Rank" and value_dummy != DEFAULT_RANK:
                    value_dummy += (google_rank_offset + random.random())
                
                value_dummy = clip_valid_rank(value_dummy)
                values_expand.append((dt, value_dummy))
        else:
            ## missing
            ## list of [(value, dt)]
            # values = [(int(data["dt"], data[metric])) for data in data_list]
            values = []
            for data in data_list:
                dt_str = data["dt"] if "dt" in data else get_date()
                dt = int(dt_str)
                value = data[metric] if metric in data else DEFAULT_RANK 
                values.append((dt, value))
            values_sorted = sorted(values, key=lambda x:x[0], reverse=False)

            dt_value_dict = {}
            for pair in values_sorted:
                dt = pair[0]
                data = pair[1]
                dt_value_dict[dt] = data

            # extend_data
            dt_list = [pair[0] for pair in values]
            min_dt = dt_list[0]
            max_dt = dt_list[len(dt_list) - 1]

            end_dt = max_dt
            ## [min(min_dt, max_dt - length), max_dt]
            start_dt = min_dt if (date_diff(max_dt, min_dt) >= data_series_length) else date_minus(max_dt, data_series_length)
            ## fill blank
            value_running = dt_value_dict[min_dt]
            for dt in date_interator(start_dt, end_dt):
                value = DEFAULT_RANK
                if dt in dt_value_dict:
                    # value exist
                    value = dt_value_dict[dt]
                    ## updating value_running
                    value_running = value
                else:
                    # value missing, using running default
                    value = value_running
                values_expand.append((dt, value))
            # print ("DEBUG: Metric %s Before Filling data series size %d, after filling size %d" % (metric, len(values_sorted), len(values_expand)))
        output_dict_final[metric] = values_expand
    return output_dict_final

def parse_maintext_and_multimedia(url, html, llm_intro_map, domain_dict_map):
    """
        args:
            html
        output:
            KEY_CONTENT
            KEY_UPLOAD_IMAGE_FILES
    """
    topk_image = 10
    fetch_image_url_enable = True
    try:
        soup = BeautifulSoup(html, "html.parser")

        ## images
        image_id_list = []
        ## meta 
        ## other image, beatiful soup tags to dict
        images = soup.select("img")
        if images is not None:
            for image in images:
                image_src = image["src"] if "src" in image.attrs else ""
                if image_src != "":
                    ## domain or others
                    full_image_url = append_url(url, image_src)
                    image_id_list.append(full_image_url)
        ## meta <meta>
        meta_list = soup.select("meta")
        if meta_list is not None:
            for meta_tag in meta_list:
                meta_content = meta_tag["content"] if "content" in meta_tag.attrs else ""
                meta_property = meta_tag["property"] if "property" in meta_tag.attrs else ""
                if is_image_url(meta_content):
                    full_image_url = append_url(url, meta_content)
                    image_id_list.append(meta_content)

        ## image need to curl and get results
        image_id_merge = ""
        if fetch_image_url_enable:
            try:
                image_id_sorted_topk = get_image_file_sorted_by_size(image_id_list, topk_image)
                image_id_merge = ",".join(image_id_sorted_topk)
            except FunctionTimedOut as e:
                print (e)
                image_id_merge = ",".join(image_id_list)
        else:
            image_id_merge = ",".join(image_id_list)

        ## videos
        video_id_list = []
        video_tag_list = soup.select("video")
        for video_tag in video_tag_list:
            source_list = video_tag.select("source")
            if len(source_list) > 0:
                source_tag = source_list[0]
                src = source_tag["src"] if "src" in source_tag else ""
                if src != "":
                    video_id_list.append(src)
        video_id_merge = ",".join(video_id_list)


        upload_image_files = ",".join([image_id_merge, video_id_merge])

        ## main text
        ### description
        description = ""
        for meta_tag in meta_list:
            if "name" in meta_tag and meta_tag["name"] == "description":
                description = meta_tag["content"] if "content" in meta_tag else ""

        ## p and span tags
        main_text_p_dict = process_main_page_content(html)
        main_text_p = main_text_p_dict[KEY_MAIN_TEXT] if KEY_MAIN_TEXT in main_text_p_dict else ""

        ## llm summary
        norm_url = normalize_url(url)
        domain = get_domain(norm_url)
        
        # p1: fetch exact url
        llm_intro = llm_intro_map[norm_url] if norm_url in llm_intro_map else "" 
        # p2: set domain default
        if llm_intro == "":
            llm_domain_list = domain_dict_map[domain] if domain in domain_dict_map else []
            llm_domain_list_sorted = sorted(llm_domain_list, key=lambda x:len(x), reverse=True)
            llm_intro = llm_domain_list_sorted[0] if len(llm_domain_list_sorted) > 0 else ""

        ## main text processing
        main_text_list = []
        if description != "":
            main_text_list.append(description) 
        if llm_intro != "":
            main_text_list.append(llm_intro) 
        if main_text_p != "":
            main_text_list.append(main_text_p)


        main_text = " ".join(main_text_list)
        output_dict = {}
        output_dict[KEY_CONTENT] = main_text
        output_dict[KEY_UPLOAD_IMAGE_FILES] = upload_image_files
        return output_dict

    except Exception as e:
        print (e)
        output_dict = {}
        return output_dict

def process_top_html_item_json(item_list):
    """
        sort item_list according to len(content) desc

        same key: content_name
        different item: meta, metric, dt, subfield
    """
    try:
        item_list_clean = []
        for item_json in item_list:
            content_name = item_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in item_json else ""
            content = item_json[KEY_CONTENT] if KEY_CONTENT in item_json else ""
            if content != "":
                item_list_clean.append(item_json)
        ## sort
        item_list_clean_sorted = sorted(item_list_clean, key=lambda x:len(x[KEY_CONTENT]), reverse = True)
        if len(item_list_clean_sorted) > 0:
            return item_list_clean_sorted[0]
        else:
            return {}
    except Exception as e:
        print (e)
        item_return = item_list[0] if len(item_list) > 0 else []
        return item_return

def get_data_map_from_merged_file(input_file):
    """
        input_file = "./data/merge/20250314/merge_bing_data.json"
        group by normalize content_name

        output: kkv
            k1: category
            k2: normalize content_name
            v2: list of item_json,  content_name duplicate, subfield duplicate, url duplicate (data series)
    """
    data_inputs = read_file(input_file)
    print ("DEBUG: get_data_map_from_merged_file input files count %d" % len(data_inputs))
    data_map = {}
    website_set = set()
    for line in data_inputs:
        item_json = json.loads(line)
        category = item_json[KEY_CATEGORY] if KEY_CATEGORY in item_json else ""
        content_name_original = item_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in item_json else ""
        ## normalize content_name
        content_name = normalize_content_name(content_name_original)
        website = item_json[KEY_WEBSITE] if KEY_WEBSITE in item_json else ""
        # check if meet filter
        if filter_no_agent_json_bing(item_json):
            print ("# DEBUG: item_json not passed|" + str(content_name))
            continue
        website_set.add(website)
        if category in data_map:
            content_name_map = data_map[category]
            if content_name in content_name_map:
                cur_list = content_name_map[content_name]
                cur_list.append(item_json)
                content_name_map[content_name] = cur_list
            else:
                content_name_map[content_name] = [item_json]
            data_map[category] = content_name_map
        else:
            content_name_map = {}
            content_name_map[content_name] = [item_json]
            data_map[category] = content_name_map
    ## statistic
    input_content_cnt = 0
    for category in data_map:
        content_map = data_map[category] if category in data_map else {}
        for content in content_map.keys():
            input_content_cnt += 1
    print ("DEBUG: get_data_map_from_merged_file output pass content %d" % input_content_cnt)

    ## print meta info
    print ("#### DEBUG: Input Website:")
    website_list = list(website_set)
    for website in website_list:
        print ("# " + website)
    return data_map


def pre_process_merge_file_whitelist():

    ## test dummy, output list of items, 
    data_file = "./data/merge/20250315/merge_bing_data.json"
    # data_file = "./data/bing/20250315/agent_bing_ai_search_agent.json"
    data_map = get_data_map_from_merged_file(data_file)

    ## k1: category, v1: list of query + name whitelist
    fetch_whitelist_path = "./data/agent_meta/fetch_missing_entity.json"
    query_append_dict_whitelist, category_whitelist_dict = read_fetch_whitelist_path(fetch_whitelist_path)

    ## item的 domain 和 domain匹配
    duplicate_list = []
    for category in data_map.keys():
        # dict, kkv
        content_dict = data_map[category]
        # list of json
        whitelist_list = category_whitelist_dict[category] if category in category_whitelist_dict else []

        for whitelist_item in whitelist_list:
            
            whitelist_content_name = whitelist_item[KEY_CONTENT_NAME]
            whitelist_website = whitelist_item[KEY_WEBSITE]
            whitelist_domain = get_domain(whitelist_website)

            ## get domain, existing
            for content_name in content_dict.keys():
                ## current item
                content_list = content_dict[content_name]
                for item_json in content_list:
                    cur_domain = get_domain(item_json[KEY_WEBSITE])
                    if cur_domain == whitelist_domain:
                        duplicate_item_json = item_json
                        duplicate_item_json[KEY_CONTENT_NAME] = whitelist_content_name
                        duplicate_list.append(duplicate_item_json)
    
    print ("DEBUG: duplicate_list size %d" % len(duplicate_list))
    output_file = "./data/merge/20250315/merge_bing_data_v2.json"
    input_data_list = read_file(data_file)
    for duplicate_item in duplicate_list:
        input_data_list.append(json.dumps(duplicate_item))
    save_file(output_file, input_data_list)

def process_main_text_body_and_images(args):
    """
    """
    # data_map_history = get_merge_all_data_ai_agent()
    
    data_file = args.data_file
    output = args.output
    llm_summary_file = args.llm_summary_file
    input_category = args.category

    print ("DEBUG: process_main_text_body_and_images data_file %s" % data_file)
    print ("DEBUG: process_main_text_body_and_images output %s" % output)
    print ("DEBUG: process_main_text_body_and_images llm_summary_file %s" % llm_summary_file)
    print ("DEBUG: process_main_text_body_and_images category %s" % input_category)

    ## test dummy, output list of items, 
    data_map = get_data_map_from_merged_file(data_file)
    
    ## aigc, call LLM from list of website
    llm_intro_map, domain_dict_map = process_main_page_aigc_content(llm_summary_file)
    
    output_json_list = []
    data_content_list_map = {}
    process_cnt = 0
    for category in data_map.keys():
        content_name_list = []
        ## key, list json
        content_dict = data_map[category]
        for name, item_list in content_dict.items():
            process_cnt += 1
            ## item_list list of json, choose top 1
            content_json = process_top_html_item_json(item_list)
            if len(content_json) == 0:
                print ("DEBUG: content_name %s pass valid html item_json empty....")
                continue
            content_name = content_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in content_json else ""
            html = content_json[KEY_HTML] if KEY_HTML in content_json else ""
            url = content_json[KEY_WEBSITE] if KEY_WEBSITE in content_json else ""
            
            output_dict = parse_maintext_and_multimedia(url, html, llm_intro_map, domain_dict_map)

            ## update output_dict to original
            content_json[KEY_CONTENT] = output_dict[KEY_CONTENT] if KEY_CONTENT in output_dict else ""
            content_json[KEY_UPLOAD_IMAGE_FILES] = output_dict[KEY_UPLOAD_IMAGE_FILES] if KEY_UPLOAD_IMAGE_FILES in output_dict else ""

            ## post process, values saparatoed by comma , tempary
            for key in [KEY_UPLOAD_IMAGE_FILES, KEY_THUMBNAIL_PICTURE]:
                original_value = content_json[key] if key in content_json else ""
                new_value = original_value.replace(" ", ",")
                content_json[key] = new_value
            ## row_mapper
            content_json_mapped = {}
            content_source = content_json[KEY_SOURCE] if KEY_SOURCE in content_json else ""
            if content_source == DATA_SOURCE_BING:
                content_json_mapped, if_missing = row_mapper_agent(fill_bing_data_json(content_json))
            elif content_source == DATA_SOURCE_GOOGLE:
                content_json_mapped, if_missing = row_mapper_agent(fill_google_data_json(content_json))
            else:
                content_json_mapped, if_missing = row_mapper_agent(fill_bing_data_json(content_json))
            if content_json_mapped is None:
                print ("DEBUG: content_json_mapped is missing %s" % content_name)
                continue
            output_json_list.append(json.dumps(content_json_mapped))

        if process_cnt % 100 == 0:
            print ("DEBUG: Total Processing Cnt %d" % process_cnt)

    print ("DEBUG: Finish Processing output_json_list size %d" % len(output_json_list))
    save_file(output, output_json_list)

def filter_merged_ai_agent_data():
    input_file = "./data/merge/maintext/merge_ai_agent_meta_v2.json"
    data_ai_agent_merge = []
    data_ai_agent_merge_dict = {}
    for line in read_file(input_file):
        data_json = json.loads(line)
        content_name = data_json["content_name"]

        data_ai_agent_merge_dict[content_name] = data_json
        data_ai_agent_merge.append(data_json)

    if "accio" in data_ai_agent_merge_dict:
        print ("DEBUG: data_ai_agent_merge_dict %s" % str(data_ai_agent_merge_dict))
    else:
        print ("DEBUG: data_ai_agent_merge_dict not included...")

def process_history_ai_agents_data():
    """
    """
    """
    """
    input_file = "./data/agent_category_meta.json"
    output_file = "./data/agent_meta/history_listed_items.json"
    lines = read_file(input_file)

    output_lines = []
    total_cnt = 0
    for line in lines:
        line_json = json.loads(line)
        category = line_json["category"] if "category" in line_json else ""
        # category = "Coding Agent"
        result = get_ai_agent_by_category(category)
        items = result["items"] if "items" in result else []
        total_cnt += len(items)

        output_dict = {}
        output_dict["category"] = category
        output_dict["items"] = items
        output_lines.append(json.dumps(output_dict))
        time.sleep(5)
    print ("DEBUG: Total Archived Item Cnt %d" % total_cnt)
    save_file(output_file, output_lines)

def extract_image_src(html):
    pattern=r'<img[^>]*src=[\'"]([^\'"]+)[\'"][^>]*>'
    matches = re.findall(pattern, html)
    return matches


def is_section(line, section_prefix):
    match = line.startswith(section_prefix)
    return match

def parse_content_tags(section):
    content_tag_list = []
    if "Reference Servers" in section:
        content_tag_list.append("official")
    if "Official Integrations" in section:
        content_tag_list.append("official")
    if "Community Servers" in section:
        content_tag_list.append("community")
    if "Frameworks" in section:
        content_tag_list.append("frameworks")
    if "For servers" in section:
        content_tag_list.append("servers")
    if "For clients" in section:
        content_tag_list.append("clients")
    if "Resources" in section:
        content_tag_list.append("resources")
    return content_tag_list

def test_item_line():
    line = "- **[AI Agent Marketplace Index](https://github.com/AI-Agent-Hub/ai-agent-marketplace-index-mcp)** - MCP server to search more than 5000+ AI agents and tools of various categories from [AI Agent Marketplace Index](http://www.deepnlp.org/store/ai-agent) and monitor traffic of AI Agents."

    pattern = r'\[\s*(.*?)\s*\]\((.*?)\)([^[]+)'
    image_pattern = r"\<\s*src=\"(.*?)\"\s*\/>"

    match_tuple_list = re.findall(pattern, line)
    for match in match_tuple_list:
        if len(match) < 3:
            continue
        item_name = match[0]  # The text inside the square brackets
        item_url = match[1]   # The URL inside the parentheses
        item_content = match[2]
        item_content_clean = item_content.replace("**", "")

def remove_emojis(text):
   clean_text = emoji.replace_emoji(text, '')
   return clean_text

def parse_git_readme(folder_path):
    """
        folder_path = "./mcp_server_dev"
    """
    content_dict = {}
    for sub_folder in os.listdir(folder_path):
        sub_folder_path = os.path.join(folder_path, sub_folder)
        readme_file = os.path.join(sub_folder_path, "README.md")
        if os.path.exists(readme_file):
            lines = read_file(readme_file)
            readme_text = "\n".join(lines)
            ## clean content
            readme_text = remove_emojis(readme_text)
            content_dict[sub_folder] = readme_text
    return content_dict

def parse_clean_json_object(input_str):
    """
    """
    try:
        json_obj = {}
        json_obj = json.loads(input_str)
        return json_obj
    except Exception as e:
        print (e)
        json_obj = {}
        return json_obj

def parse_git_readme_mcp_json(folder_path):
    """
        folder_path = "./data/mcp/github"
        modify the content : ```json -> ```
    """
    ## kkv
    content_json_dict = {}
    for sub_folder in os.listdir(folder_path):
        sub_folder_path = os.path.join(folder_path, sub_folder)
        readme_file = os.path.join(sub_folder_path, "README.md")
        if os.path.exists(readme_file):
            lines = read_file(readme_file)
            # readme_text = "\n".join(lines)

            ## parse the json files
            json_parsed = []
            json_section = []
            json_section_start_enable = False
            for line in lines:
                # if "```json" in line:
                #     json_section = []
                #     json_section_start_enable = True
                
                if "```" in line:
                    # change ending 
                    if json_section_start_enable:
                        # eno of json lines
                        json_str = "".join(json_section)
                        if json_str != "":
                            json_obj = parse_clean_json_object(json_str)
                            if isinstance(json_obj, dict) and len(json_obj) > 0:
                                json_parsed.append(json_obj)
                        # clean variable
                        json_str = ""
                        json_section = []
                        json_section_start_enable = not json_section_start_enable
                    else:
                        # start new code section 
                        json_section_start_enable = not json_section_start_enable

                else:
                    if json_section_start_enable:
                        json_section.append(line)
                    else:
                        continue
            content_json_dict[sub_folder] = json_parsed
        else:
            continue
    ## print 
    # kv, key: str, value: list of str
    return content_json_dict



def read_file_json(input_file):
    """
        clean json string
    """
    lines = read_file(input_file)
    lines_strip = [line.strip() for line in lines]
    merge_str = "".join(lines_strip)
    return merge_str

def parse_mcp_tools_json(folder_path):
    """
    """
    json_extension = ".json"

    ## key: server_id, value: json string of tools
    server_tools_dict = {}
    for file in os.listdir(folder_path):
        input_file = os.path.join(folder_path, file)
        if json_extension not in input_file:
            continue
        pairs = file.split(".")
        if len(pairs) != 2:
            continue
        server_id = pairs[0]
        json_str = read_file_json(input_file)
        server_tools_dict[server_id] = json_str
    print ("DEBUG: parse_mcp_tools_json processing file count %d" % len(server_tools_dict))
    return server_tools_dict

def parse_content_from_line(line):
    """
    """
    # clean content
    item_content = re.sub(r'\([^)]*\)', '', line)  # 输出：Hello  example 
    item_content = re.sub(r'<.*?>', '', item_content)
    ## set item
    item_content = item_content.replace("*", "")            
    item_content = item_content.replace("[", "")            
    item_content = item_content.replace("]", "")
    item_content = item_content.replace("-", "")            
    item_content = item_content.strip()
    return item_content

def process_mcp_readme_data():
    """
    """
    folder_path = "./data/mcp/github"
    input_file = "./data/mcp/config/mcp_server_README_20250605.md"
    lines = read_file(input_file)

    pattern = r'\[\s*(.*?)\s*\]\((.*?)\)([^[]+)'

    pattern_url = r'\[\s*(.*?)\s*\]\((.*?)\)'
    image_pattern = r"\<\s*src=\"(.*?)\"\s*\/>"

    base_url = "https://github.com/modelcontextprotocol/servers"
    # name_prefix = "**["
    img_pregix = "<img"

    # load git content
    content_dict = parse_git_readme(folder_path)
    content_json_list_dict = parse_git_readme_mcp_json(folder_path)
    pattern = r"https://github.com/([^/]+)/([^/]+)"    

    input_json_list = []
    cur_section_name = ""
    for line in lines:

        if is_section(line, "## ") or is_section(line, "### "):
            cur_section_name = line.replace("#", "")
            cur_section_name = cur_section_name.strip()
        else:
            ## each line contain one mcp server
            item_json = {}
            match_tuple_list = re.findall(pattern_url, line)

            item_name_list = []
            item_url_list = []
            for match in match_tuple_list:
                if len(match) < 2:
                    continue
                item_name_list.append(match[0])
                item_url_list.append(match[1])

            ## get all
            item_name = item_name_list[0] if len(item_name_list) > 0 else ""
            item_url = item_url_list[0] if len(item_url_list) > 0 else ""

            if item_name == "":
                # print ("DEBUG: Skipped line|%s" % line)
                continue

            abstract_content = parse_content_from_line(line)
            main_text = ""
            if "github" in item_url:
                repo = ""
                match_tuple_list = re.findall(pattern, item_url)
                for match in match_tuple_list:
                    if len(match) < 2:
                        continue
                    user_name = match[0]
                    repo = match[1]
                ## 
                main_text = content_dict[repo] if repo in content_dict else ""
            ## merge
            if main_text == "":
                main_text = abstract_content

            ## src/aws-kb-retrieval
            if item_url.startswith("src"):
                item_url = "https://github.com/modelcontextprotocol/servers/tree/main/" + item_url
            item_json["content_name"] = item_name
            item_json["website"] = item_url
            item_json["content"] = main_text
            item_json["abstract"] = abstract_content
            item_json[KEY_FIELD] = "MCP SERVER"
            item_json[KEY_SUBFIELD] = "MCP SERVER"
            item_json[KEY_CATEGORY] = "MCP SERVER"
            item_json[KEY_PUBLISHER_ID] = get_sug_by_name(item_name)

            ## tags
            content_tag_list = parse_content_tags(cur_section_name)
            content_tag_list_str = ",".join(content_tag_list)
            item_json[KEY_CONTENT_TAG_LIST] = content_tag_list_str

            ## image 
            if img_pregix in line:
                image_match = extract_image_src(line)
                if len(image_match) > 0:
                    image_src = image_match[0]
                    item_json[KEY_THUMBNAIL_PICTURE] = image_src
            ## append
            input_json_list.append(item_json)
    output_dict = {}
    output_dict["category"] = "MCP SERVER"
    output_dict["items"] = input_json_list    
    save_file("./data/markdown/mcp/mcp_server_README.json", [json.dumps(output_dict)])

    ## post
    output_json_list = []
    for item_json in input_json_list:
        output_json_list.append(json.dumps(item_json))
    save_file("./data/markdown/mcp/mcp_server_merge.json", mcp,output_json_list)



def get_unique_id(github_url):

    pattern_github_repo_path = r"https://github.com/([^/]+)/(\S+)"    

    owner_id = ""
    repo_name = ""
    match_tuple_list = re.findall(pattern_github_repo_path, github_url)
    
    for match in match_tuple_list:
        if len(match) < 2:
            continue
        owner_id = match[0]
        repo_name = match[1]
    unique_id = "%s/%s" % (owner_id, repo_name)
    return unique_id

def load_mcp_readme_data(input_file, output_mcp_file, output_mcp_file_merge, output_mcp_file_folder):
    """
        input_file = "./data/mcp/config/mcp_server_README_20250605.md"
    """
    folder_path = "./data/mcp/github"
    input_file = "./data/mcp/config/official_mcp_server_README_20250605.md"
    lines = read_file(input_file)

    pattern = r'\[\s*(.*?)\s*\]\((.*?)\)([^[]+)'

    pattern_url = r'\[\s*(.*?)\s*\]\((.*?)\)'
    image_pattern = r"\<\s*src=\"(.*?)\"\s*\/>"

    base_url = "https://github.com/modelcontextprotocol/servers"
    # name_prefix = "**["
    img_pregix = "<img"

    # load git content
    # content_dict = parse_git_readme(folder_path)
    # content_json_list_dict = parse_git_readme_mcp_json(folder_path)
    pattern = r"https://github.com/([^/]+)/([^/]+)"    

    pattern_github_repo_path = r"https://github.com/([^/]+)/(\S+)"    

    input_json_list = []
    cur_section_name = ""

    # List of (url, repo_path)
    result_list = []
    for line in lines:
        if is_section(line, "## ") or is_section(line, "### "):
            cur_section_name = line.replace("#", "")
            cur_section_name = cur_section_name.strip()
        else:
            ## each line contain one mcp server
            item_json = {}
            match_tuple_list = re.findall(pattern_url, line)

            item_name_list = []
            item_url_list = []
            for match in match_tuple_list:
                if len(match) < 2:
                    continue
                item_name_list.append(match[0])
                item_url_list.append(match[1])

            for item_url in item_url_list:
                if "github" in item_url:
                    repo = ""
                    match_tuple_list = re.findall(pattern_github_repo_path, item_url)
                    if len(match_tuple_list) > 0:
                        for match in match_tuple_list:

                            if len(match) == 2:
                                repo = match[0]
                                abs_path = match[1]

                                match_clean = abs_path.replace("tree/master/", "")
                                result = (item_url, match_clean)
                                result_list.append(result)
    ## match
    print ("DEBUG: Processed Github Readme Repo Count %d" % len(result_list))

    ## fetch_readme
    content_json_dict = {}
    for (github_url, repo_path) in result_list:
        unique_id = get_unique_id(github_url)
        full_repo_path = os.path.join(folder_path, repo_path)
        readme_file = os.path.join(full_repo_path, "README.md")
        if os.path.exists(readme_file):
            lines = read_file(readme_file)
            # readme_text = "\n".join(lines)

            ## parse the json files
            json_parsed = []
            json_section = []
            json_section_start_enable = False
            for line in lines:
                # if "```json" in line:
                #     json_section = []
                #     json_section_start_enable = True
                if "```" in line:
                    if json_section_start_enable:
                        json_str = "".join(json_section)
                        if json_str != "":
                            json_obj = parse_clean_json_object(json_str)
                            if len(json_obj) > 0:
                                json_parsed.append(json_obj)
                        # clean variable
                        json_str = ""
                        json_section = []
                        json_section_start_enable = not json_section_start_enable
                    else:
                        json_section_start_enable = not json_section_start_enable
                else:
                    if json_section_start_enable:
                        json_section.append(line)
                    else:
                        continue
            content_json_dict[unique_id] = json_parsed

    ## load existing mcp_config
    output_list = read_file(output_mcp_file)
    for key, value in content_json_dict.items():
        output_dict = {}
        output_dict["id"] = key
        output_dict["config"] = value
        output_list.append(json.dumps(output_dict))
    save_file(output_mcp_file_merge, output_list)

    ## output
    merge_mcp_json = {}
    mcp_file_prefix = "mcp_config_"
    for line in output_list:
        item_json = json.loads(line)
        item_id = item_json["id"] if "id" in item_json else ""
        server_id_norm = server_unique_id_to_filename(item_id)
        mcp_config_list = item_json["config"] if "config" in item_json else []
        if len(mcp_config_list) == 1:
            mcp_config = mcp_config_list[0]

            mcp_config_clean = {}
            if "mcpServers" in mcp_config:
                mcp_config_clean = mcp_config["mcpServers"]
            elif "mcp" in mcp_config:
                mcp_config_clean = mcp_config["mcp"]
            else:
                print ("Not Valid MCP %s" % str(mcp_config))
            merge_mcp_json.update(mcp_config_clean)
            if not is_valid_mcp_json(mcp_config):
                continue
            subfolder = server_id_norm[0]
            file_name = os.path.join(output_mcp_file_folder, subfolder, mcp_file_prefix + server_id_norm + ".json")
            if not os.path.exists(os.path.dirname(file_name)):
                os.mkdir(os.path.dirname(file_name))

            merge_mcp_json.update(mcp_config)
            save_file(file_name, [json.dumps(mcp_config)])
        else:
            for i, mcp_config in enumerate(mcp_config_list):
                if not is_valid_mcp_json(mcp_config):
                    continue
                command = mcp_config["command"] if "command" in mcp_config else ""
                file_name = ""
                subfolder = server_id_norm[0]

                if command == "" or "/" in command:
                    file_name = os.path.join(output_mcp_file_folder, subfolder, mcp_file_prefix + server_id_norm + "_%d" % i + ".json")
                else:
                    file_name = os.path.join(output_mcp_file_folder, subfolder, mcp_file_prefix + server_id_norm + "_%s" % command + ".json")

                mcp_config_clean = {}
                if "mcpServers" in mcp_config:
                    mcp_config_clean = mcp_config["mcpServers"]
                elif "mcp" in mcp_config:
                    mcp_config_clean = mcp_config["mcp"]
                else:
                    print ("Not Valid MCP %s" % str(mcp_config))
                merge_mcp_json.update(mcp_config_clean)
                if not os.path.exists(os.path.dirname(file_name)):
                    os.mkdir(os.path.dirname(file_name))
                save_file(file_name, [json.dumps(mcp_config)])
    print ("DEBUG: MCP Config Size %d" % len(merge_mcp_json))
    output_merge_mcp_json = {}
    output_merge_mcp_json["mcpServers"] = merge_mcp_json
    # ./data/config/merge_mcp_config.json
    merge_file_name = os.path.join(os.path.dirname(output_mcp_file_folder), "merge_mcp_config.json")
    save_file(merge_file_name, [json.dumps(output_merge_mcp_json)])

def is_valid_mcp_json(mcp_config_json):
    """
    """
    if "mcpServers" in mcp_config_json or "mcp" in mcp_config_json:
        return True 
    else:
        return False

def convert_sug_to_name(item_sug):
    items = item_sug.split("-")
    item_name = " ".join(items)
    return item_name




def get_arg_path_norm(project_folder, argument, project_name):
    """
    """
    if "path" in argument.lower():
        # change to absolute path
        argument_norm = argument.lower()
        items = argument_norm.split("/")
        match_index = -1
        for i, item in enumerate(items):
            if item.lower() == project_name.lower():
                match_index = i 
                break 
        # original
        items_original = argument.split("/")
        file_path = "/".join(items_original[match_index:]) # /project_name/xxx.js
        abs_file_path = os.path.join(project_folder, file_path)
        return abs_file_path
    else:
        return argument


valid_command_list = ["uv", "uvx", "python", "node", "npm", "npx", "ruby"]

def get_clean_value(value):
    """ value list
        value = "fsfd${yourkey}"
    """
    if isinstance(value, str):
        value_clean = value.replace("$", "")
        pattern1 = r'<.*?>'
        value_clean = re.sub(pattern1, 'key123', value_clean)

        pattern2 = r'{.*?}'
        value_clean = re.sub(pattern2, 'key123', value_clean)

        pattern3 = r'[.*?]'
        value_clean = re.sub(pattern3, 'key123', value_clean)

        return value_clean
    else:
        return value

def get_command_norm(command):
    """
        command_norm
    """
    match_command = ""
    for cmd in  valid_command_list:
        if cmd.lower() in command.lower():
            match_command = cmd
    if match_command != "":
        return match_command
    else:
        return command

def load_mcp_tools_command_line(input_file, output_cmd_file, output_cmd_file_v2, output_config_folder):
    """
    """
    lines = read_file(input_file)
    server_id_to_config_dict = {}
    for line in lines:
        item_json = {}
        try:
            item_json = json.loads(line)
        except Exception as e:
            print (e)
        server_id = item_json["id"] if "id" in item_json else ""
        config_list = item_json["config"] if "config" in item_json else []
        server_id_to_config_dict[server_id] = config_list

    ## output mcp tools command lines
    # valid_command_list = ["uv", "uvx", "python", "node", "npm", "npx", "ruby"]

    cli_full_template_schema = "nohup npx @modelcontextprotocol/inspector --cli {cli} --method tools/list > {output_folder_schema}/{output_file} 2>&1 &"
    cli_full_template = "nohup npx @modelcontextprotocol/inspector --cli {cli} --method tools/list > {output_folder}/{output_file} 2>&1 &"
    # cli_full_template = "npx @modelcontextprotocol/inspector --cli {cli} --method tools/list > {output_folder}/{output_file}"

    set_env_template = "export {kvmap} ;"

    github_project_folder = "./data/mcp/github"

    # generate command lines
    output_command_list = []
    output_command_list_v2 = []

    for server_id, config_list in server_id_to_config_dict.items():

        owner_name = ""
        project_name = ""
        server_tuples = server_id.split("/")
        if len(server_tuples) == 2:
            owner_name = server_tuples[0]
            project_name = server_tuples[1]
        server_id_norm = server_unique_id_to_filename(server_id)
        
        # output_mcp_config
        mcp_config_folder = os.path.join(output_config_folder, server_id_norm)
        tools_schema_folder = os.path.join(output_config_folder, "schema")
        # print (f"DEBUG: tools_schema_folder is {tools_schema_folder}")

        if not os.path.exists(mcp_config_folder):
            os.mkdir(mcp_config_folder)

        for i, mcp_config in enumerate(config_list):
            mcp_file = "mcp_config.json"
            if "mcpServers" in mcp_config:
                mcp_file = os.path.join(mcp_config_folder, "mcp_config.json")
            else:
                mcp_file = os.path.join(mcp_config_folder, "mcp_config_%d.json" % i)

            output_line = json.dumps(mcp_config, indent=2)
            # print ("DEBUG: Saving MCP File to mcp_file %s and line %s" % (mcp_file, output_line))
            save_file(mcp_file, [output_line])

        # output tools.json
        # owner/project_repo/key .json
        output_file = "tool_" + project_name + ".json"

        # output_tools_command
        for mcp_config in config_list:
            ## multiple
            mcp_servers_config_map = {}
            if "mcpServers" in mcp_config:
                mcp_servers_config_map = mcp_config["mcpServers"] if "mcpServers" in mcp_config else {}
                if isinstance(mcp_servers_config_map, dict):
                    for key, config in mcp_servers_config_map.items():
                        command = config["command"] if "command" in config else ""
                        args = config["args"] if "args" in config else []
                        env = config["env"] if "env" in config else {}

                        cmd_norm = get_command_norm(command)
                        args_norm = [get_arg_path_norm(github_project_folder, arg, project_name) for arg in args]
                        run_server_line = " ".join([cmd_norm] + args_norm)

                        output_file = "tool_" + server_id_norm + "_" + key.lower() + ".json"
                        inspector_line = cli_full_template.format(cli=run_server_line, output_folder=mcp_config_folder, output_file=output_file)

                        inspector_line_v2 = cli_full_template_schema.format(cli=run_server_line, output_folder_schema=tools_schema_folder, output_file=output_file)


                        cur_line_item = ['%s="%s"' % (k, get_clean_value(v)) for k, v in env.items()] if isinstance(env, dict) else []                        
                        set_env_cmd_line = set_env_template.format(kvmap = " ".join(cur_line_item))
                        
                        if len(env) == 0:
                            output_command_list.append(inspector_line)
                            output_command_list_v2.append(inspector_line_v2)
                        else:
                            output_command_list.extend([set_env_cmd_line, inspector_line])
                            output_command_list_v2.extend([set_env_cmd_line, inspector_line_v2])

            elif "mcp" in mcp_config:
                mcp_servers_config_map = mcp_config["mcp"] if "mcp" in mcp_config else {}

                inputs = mcp_servers_config_map["inputs"] if "inputs" in mcp_servers_config_map else {}
                servers_dict = mcp_servers_config_map["servers"] if "servers" in mcp_servers_config_map else {}

                if isinstance(servers_dict, dict):
                    for key, config in servers_dict.items():
                        command = config["command"] if "command" in config else ""
                        args = config["args"] if "args" in config else []
                        env = config["env"] if "env" in config else {}

                        cmd_norm = get_command_norm(command)
                        args_norm = [get_arg_path_norm(github_project_folder, arg, project_name) for arg in args]
                        run_server_line = " ".join([cmd_norm] + args_norm)
                        
                        # project_name and current key mismatch
                        output_file = "tool_" + server_id_norm + "_" + key.lower() + ".json"
                        inspector_line = cli_full_template.format(cli=run_server_line, output_folder=mcp_config_folder, output_file=output_file)

                        inspector_line_v2 = cli_full_template_schema.format(cli=run_server_line, output_folder_schema=tools_schema_folder, output_file=output_file)

                        cur_line_item = ['%s="%s"' % (k, get_clean_value(v)) for k, v in env.items()] if isinstance(env, dict) else []                        
                        set_env_cmd_line = set_env_template.format(kvmap = " ".join(cur_line_item))
                        
                        if len(env) == 0:
                            output_command_list.append(inspector_line)
                            output_command_list_v2.append(inspector_line_v2)

                        else:
                            output_command_list.extend([set_env_cmd_line, inspector_line])
                            output_command_list_v2.extend([set_env_cmd_line, inspector_line_v2])

            else:
                continue
    print ("DEBUG: Generating Command Line size %d" % len(output_command_list))
    save_file(output_cmd_file, output_command_list)

    save_file(output_cmd_file_v2, output_command_list_v2)

def process_mcp_marketplace_json_data():
    """
        process mcp_marketplace main entrance
    """
    folder_path = "./data/mcp/github"
    input_file = "./data/mcp/config/mcp_server_x.json"
    tools_folder_path = "./data/mcp/tools/tmp"

    lines = read_file(input_file)

    mcp_server_dict = json.loads(lines[0])
    mcp_server_list_raw = mcp_server_dict["servers"] if "servers" in mcp_server_dict else []
    mcp_server_list = sorted(mcp_server_list_raw, key=lambda x:x["github_stars"] if "github_stars" in x and x["github_stars"] is not None else 0, reverse=True)
    print ("DEBUG: mcp_server_list size %d" % len(mcp_server_list))

    stars_threshhold = 5
    filter_cnt = 0
    for mcp in mcp_server_list:
        stars = mcp["github_stars"] if "github_stars" in mcp and mcp["github_stars"] is not None else 0
        if stars >= stars_threshhold:
            filter_cnt += 1
    print ("DEBUG: mcp_server_list meet threshold %d size %d" % (stars_threshhold, filter_cnt))

    # github_pattern = r'\[\s*(.*?)\s*\]\((.*?)\)([^[]+)'
    github_pattern = r"https://github.com/([^/]+)/([^/]+)"    

    # load git content
    content_dict = parse_git_readme(folder_path)

    # load git json dict
    content_json_list_dict = parse_git_readme_mcp_json(folder_path)

    ## debug
    server_id = "calvernaz/alphavantage"
    repo_name = "alphavantage"
    mcp_config_list = content_json_list_dict[repo_name] if repo_name in content_json_list_dict else []
    print (f"#### DEBUG: repo_name {repo_name} and mcp_config_list {mcp_config_list}")


    content_server_tools_dict = parse_mcp_tools_json(tools_folder_path)

    output_json_list = []
    output_json_str_list = []
    for mcp_server in mcp_server_list:
        name = mcp_server["name"] if "name" in mcp_server else ""
        url = mcp_server["url"] if "url" in mcp_server else ""
        ## none
        external_url = mcp_server["external_url"] if "external_url" in mcp_server else ""
        short_description = mcp_server["short_description"] if "short_description" in mcp_server else ""
        source_code_url = mcp_server["source_code_url"] if "source_code_url" in mcp_server else ""
        github_stars = mcp_server["github_stars"] if "github_stars" in mcp_server else ""
        package_registry = mcp_server["package_registry"] if "package_registry" in mcp_server else ""
        package_name = mcp_server["package_name"] if "package_name" in mcp_server else ""
        package_download_count = mcp_server["package_download_count"] if "package_download_count" in mcp_server else ""
        EXPERIMENTAL_ai_generated_description = mcp_server["EXPERIMENTAL_ai_generated_description"] if "EXPERIMENTAL_ai_generated_description" in mcp_server else ""
        ## parse main text
        main_text = ""
        config_json_str_list = []
        ## generate unique_id: github.git  /username/reponame
        publisher_id = ""
        content_name = ""
        if source_code_url is not None and "github" in source_code_url:
            repo = ""
            match_tuple_list = re.findall(github_pattern, source_code_url)
            for match in match_tuple_list:
                if len(match) < 2:
                    continue
                user_name = match[0]
                repo = match[1]
                ## update publisher_id from github/user_name
                publisher_id = user_name
                content_name = convert_sug_to_name(repo)
            ## 
            main_text = content_dict[repo] if repo in content_dict else ""
            # list of str json
            config_json_str_list = content_json_list_dict[repo] if repo in content_json_list_dict else []
        ## merge
        if main_text == "":
            main_text = short_description
        ## parse main config.json
        if publisher_id == "":
            publisher_id = get_sug_by_name(name)

        ## generate unique_id, github
        unique_id = ""
        if user_name != "" and repo != "":
            unique_id = "%s/%s" % (user_name, repo)
        ## update publisher_id and content_name
        server_id = server_unique_id_to_filename(unique_id)
        tools_json_str = content_server_tools_dict[server_id] if server_id in content_server_tools_dict else ""

        ## mpping
        item_json = {}
        item_json["id"] = unique_id
        item_json["content_name"] = content_name
        item_json["website"] = source_code_url ## github
        item_json["content"] = main_text
        item_json["abstract"] = short_description
        item_json[KEY_FIELD] = "MCP SERVER"
        item_json[KEY_SUBFIELD] = "MCP SERVER"
        item_json[KEY_CATEGORY] = "MCP SERVER"
        item_json[KEY_PUBLISHER_ID] = publisher_id
        item_json[KEY_THUMBNAIL_PICTURE] = ""
        ## external
        item_json["external_url"] = external_url
        item_json["package_registry"] = package_registry
        item_json["package_name"] = package_name
        item_json["package_download_count"] = package_download_count
        item_json["github"] = source_code_url
        ## VS mcp.json, claude_desktop_config.json
        item_json["mcp_server_config"] = json.dumps(config_json_str_list)
        item_json["tools"] = tools_json_str

        output_json_list.append(item_json)
        output_json_str_list.append(json.dumps(item_json))

    output_dict = {}
    output_dict["category"] = "MCP SERVER"
    output_dict["items"] = output_json_list    
    save_file("./data/mcp/config/mcp_server_x_output.json", [json.dumps(output_dict)])
    save_file("./data/mcp/config/mcp_server_merge_x.json", output_json_str_list)

    ## Github Json
    output_json_github_list = []
    for item_json in output_json_list:
        github_url = item_json["github"] if "github" in item_json else ""
        if github_url is None:
            github_url = ""
        if "github" in github_url:
            output_json_github_list.append(github_url)
    save_file("./data/mcp/config/mcp_server_x_github.txt", output_json_github_list)

    ## Process Github Readme, output_readme.
    update_readme_add_badge("./data/mcp/config/mcp_server_merge_x.json", "./data/mcp/config/README_ADD.md")


    ## 输出github 拉取
    convert_github_url("./data/mcp/config/mcp_server_x_github.txt", "./data/mcp/config/mcp_server_github_url_x.txt", "./data/mcp/config/mcp_server_github_url_x.sh")

    ## Get Tools Config From Source File
    ## output mcp_merge.json
    process_marketplace_mcp_json_config("./data/mcp/config/mcp_server_merge_x.json", "./data/mcp/config/mcp_list_tools_command.sh"
        , "./data/mcp/config/output_mcp_config.json"
        , "./data/mcp/config/mcp_server_config_list.json"
        , "./data/mcp/config/mcp_merge.json"
        , content_json_list_dict)


    ## merge readme and x json
    load_mcp_readme_data("./data/mcp/config/mcp_server_README_20250605.md", "./data/mcp/config/output_mcp_config.json"
        , "./data/mcp/config/output_mcp_config_merge.json", "./data/mcp/config/file/")

    ## 
    load_mcp_tools_command_line("./data/mcp/config/output_mcp_config_merge.json", "./data/mcp/config/mcp_list_tools_command.sh", 
        "./data/mcp/config/mcp_list_tools_command_v2.sh", "./data/mcp/tools/tmp")


def use_mcp_config():
    import mcp_marketplace as mcpm

    category = "search"
    result = mcpm.search(query=category, page_id=0, count_per_page=20, mode="dict")

    print ("DEBUG: run_setup_config_deepnlp result:")
    print (result)

    item_map = result['item_map'] if 'item_map' in result else {}
    items = item_map[category] if category in item_map else []
    count = len(items)

    print ("DEBUG: use_mcp_config count %d" % count)
    server_ids = [item["id"] if "id" in item else "" for item in items]
    
    ## Load Config
    mcp_config_result = mcpm.load_config_batch(server_ids, config_name="deepnlp_server")

    ## load Tools
    # result_id = mcpm.search(id="/puppeteer/puppeteer", mode="list", page_id=0, count_per_page=100, config_name="deepnlp")
    tools = mcpm.list_tools(id="/puppeteer/puppeteer", config_name="deepnlp_tool")


def process_github_badge_result():
    """
    """
    input_files = read_file("./data/markdown/mcp/mcp_server_merge_x.json")
    print ("DEBUG: process_github_badge_result Input Files %s" % len(input_files))
    output_dict_list = []
    for line in input_files:
        item_json = json.loads(line)
        github = item_json["website"] if "website" in item_json else ""
        publisher_id = item_json["publisher_id"] if "publisher_id" in item_json else ""
        content_name = item_json["content_name"] if "content_name" in item_json else ""
        field = item_json["field"] if "field" in item_json else ""
        subfield = item_json["subfield"] if "subfield" in item_json else ""

        content_url = "http://www.deepnlp.org/store/%s/%s/pub-%s/%s" % (get_sug_by_name(field), get_sug_by_name(subfield),
                get_sug_by_name(publisher_id), get_sug_by_name(content_name))

        ## add repo        
        svg_markdown = "![MCP Marketplace User Review Rating Badge](http://www.deepnlp.org/api/marketplace/svg?%s/%s)" % (get_sug_by_name(publisher_id), get_sug_by_name(content_name))
        output_dict = {}
        output_dict["github"] = github
        output_dict["svg_markdown"] = svg_markdown
        output_dict_list.append(json.dumps(output_dict))

    save_file("./data/markdown/mcp/mcp_server_merge_badge.json", output_dict_list)


def process_url():
    """
        agent github
    """
    import ai_agent_marketplace as aa

    url = ""
    ## list of category
    ## ai-agents index
    ## ai-agents url


    ## 
    # fetch category from 
    result = aa.search(q="Coding Agent", limit=20, timeout=5)
    print ("## DEBUG: search result is|%s" % str(result))
    items = result["items"] if "items" in result else []
    for item in items:
        content_name = item["content_name"] if "content_name" in item else ""
        bing_rank = item["Bing Rank"] if "Bing Rank" in item else []
        google_rank = item["Google Rank"] if "Google Rank" in item else []

        google_value = [rank['value'] for rank in google_rank]
        google_avg_value = sum(google_value)/len(google_value)

        bing_value = sum(bing_rank)/len(bing_rank)
        bing_avg_value = sum(bing_value)/len(bing_value)

def convert_github_url(github_path, output_path_txt, output_path_sh):
    """
        convert from github_path to git

        github_path:  format: https
        output_path_txt: "./data/markdown/mcp/mcp_server_github_url_x.txt"
        bash_output_file: "./data/markdown/mcp/mcp_server_github_url_x.sh"
    """
    # input_file = "./data/markdown/mcp/mcp_server_x_github.txt"
    lines = read_file(github_path)

    pattern = r"https://github.com/([^/]+)/([^/]+)"    
    git_pattern = "git@github.com:%s/%s.git"

    git_url_list = []
    for line in lines:
        match_tuple_list = re.findall(pattern, line)
        for match in match_tuple_list:
            if len(match) < 2:
                continue
            user_name = match[0]
            repo = match[1]
            git_url = git_pattern % (user_name, repo)
            git_url_list.append(git_url)
    # output_file = "./data/markdown/mcp/mcp_server_github_url_x.txt"
    save_file(output_path_txt, git_url_list)

    ## scripts
    bash_lines = []
    # bash_output_file = "./data/markdown/mcp/mcp_server_github_url_x.sh"
    bash_headers = "#!/bin/bash"
    for git_url in git_url_list:
        bash_line = "git clone %s" % git_url 
        bash_lines.append(bash_line)
    save_file(output_path_sh, bash_lines)


def select_match_config(config_list):
    """
        Choose Config according to users' python/js/sse/npx
    """
    if len(config_list) > 0:
        return config_list[0]
    return None



def server_unique_id_to_filename(server_id):
    """ convert unique server id to filename
        @A/B -> A_B
        /A/B -> A_B
    """
    server_id_clean = server_id
    if "/" in server_id:
        server_id_clean = server_id_clean.replace("/", "_")
    if "@" in server_id:
        server_id_clean = server_id_clean.replace("@", "")
    return server_id_clean

def process_marketplace_mcp_json_config(input_file, output_tools_cmd_line_file, output_mcp_config_file, mcp_json_list_file, mcp_json_merge_file,content_config_json_dict):
    """
        input_file: list of json string
        input_file = "./data/markdown/mcp/mcp_server_merge_x.json"
        
        mcp_json_list_file: "./data/mcp/config/mcp_server_config_list.json"
        mcp_json_merge_file:  "./data/mcp/config/mcp_merge.json"
    """
    lines = read_file(input_file)

    # key: server_id, value: list of name, google_map so many of them
    server_id_to_config_dict = {}

    server_config_list = []
    for line in lines:
        item_json = json.loads(line)

        unique_id = item_json["id"] if "id" in item_json else ""
        content_name = item_json["content_name"] if "content_name" in item_json else ""
        mcp_server_config = item_json["mcp_server_config"] if "mcp_server_config" in item_json else []

        ## str
        mcp_server_config_obj = []
        if isinstance(mcp_server_config, str):
            mcp_server_config_obj = json.loads(mcp_server_config)
        elif isinstance(mcp_server_config, dict):
            mcp_server_config_obj = mcp_server_config
        else:
            mcp_server_config_obj = mcp_server_config

        server_config_list.extend(mcp_server_config_obj)

        ## add to server_id to config files
        if unique_id in server_id_to_config_dict:
            config_list = server_id_to_config_dict[unique_id]
            config_list.extend(mcp_server_config_obj)
            server_id_to_config_dict[unique_id] = config_list
        else:
            server_id_to_config_dict[unique_id] = mcp_server_config_obj
    print ("DEBUG: Processing server_id_to_config_dict Size %d" % len(server_id_to_config_dict))

    ## output
    output_list = []
    for server_config in server_config_list:
        output_list.append(json.dumps(server_config))
    ## save
    save_file(mcp_json_list_file, output_list)

    ## merge mcp.json
    ## key: str, value list
    mcp_config_group = {}
    ## merge by group, {}
    for server_config in server_config_list:
        servers_dict = server_config["mcpServers"] if "mcpServers" in server_config else None
        if servers_dict is not None:
            if isinstance(servers_dict, dict):
                for key, config in servers_dict.items():
                    if key in mcp_config_group:
                        cur_list = mcp_config_group[key]
                        cur_list.append(config)
                        mcp_config_group[key] = cur_list
                    else:
                        mcp_config_group[key] = [config]
            else:
                print ("DEBUG: servers_dict incorrect format %s" % str(servers_dict))
    ## name -> choose environment
    mcp_config_merge = {}
    for key, config_list in mcp_config_group.items():
        config = select_match_config(config_list)
        if config is not None:
            mcp_config_merge[key] = config 
    print ("DEBUG: Merged mcp_config_merge size %d" % len(mcp_config_merge))

    mcp_config = {}
    mcp_config["mcpServers"] = mcp_config_merge
    save_file(mcp_json_merge_file, [json.dumps(mcp_config)])

    # ## output mcp tools command lines
    # valid_command_list = ["uv", "uvx", "python", "node", "npm", "npx", "ruby"]

    # # generate command lines
    # output_command_list = []
    # for server_id, config_list in server_id_to_config_dict.items():

    #     server_id_norm = server_unique_id_to_filename(server_id)
    #     for mcp_config in config_list:
    #         mcp_servers_config_map = mcp_config["mcpServers"] if "mcpServers" in mcp_config else {}
    #         mcp_servers_config_map_valid = {}
    #         if not isinstance(mcp_servers_config_map, dict):
    #             continue
    #         # valid_command_list = ["uv", "npx", "uvx", "python",]
    #         command_set = set()
    #         for key, config in mcp_servers_config_map.items():
    #             command = config["command"] if "command" in config else ""
    #             url = config["url"] if "url" in config else ""
    #             if command != "":
    #                 command_set.add(command)
    #             ## local or SSE
    #             if command in valid_command_list or url != "":
    #                 mcp_servers_config_map_valid[key] = config

    #         cli_full_template = "sudo npx @modelcontextprotocol/inspector --cli {cli} --method tools/list > ./tmp/{output_file}"
    #         for key, config in mcp_servers_config_map_valid.items():
    #             command = config["command"] if "command" in config else ""
    #             args = config["args"] if "args" in config else []
    #             env = config["env"] if "env" in config else []
                
    #             cli = " ".join([command] + args)
    #             output_file = server_id_norm + ".json"
    #             inspector_line = cli_full_template.format(cli=cli,output_file=output_file)
    #             output_command_list.append(inspector_line)
    # print ("DEBUG: Generating Command Line size %d" % len(output_command_list))
    # save_file(output_tools_cmd_line_file, output_command_list)

    # output config file
    output_mcp_config_list = []
    succ_cnt = 0
    # server_id: user_name/repo_name
    for server_id, config_list in server_id_to_config_dict.items():
        print (f"DEBUG: Processing server_id {server_id}")
        server_names = server_id.split("/")
        if len(server_names) < 2:
            print (f"DEBUG: Skipped Server ID {server_id}")
            continue
        user_name = server_names[0]
        repo = server_names[1]
        ## update publisher_id from github/user_name
        publisher_id = user_name
        content_name = convert_sug_to_name(repo)
        ## 
        # list of str json
        config_json_str_list = content_config_json_dict[repo] if repo in content_config_json_dict else []

        if len(config_json_str_list) > 0:
            succ_cnt += 1

        output_dict = {}
        output_dict["id"] = server_id
        output_dict["config"] = config_json_str_list

        output_mcp_config_list.append(json.dumps(output_dict))
    fill_rate = 1.0 * succ_cnt/len(output_mcp_config_list)
    print (f"DEBUG: mcp_config fill_rate {fill_rate}")
    save_file(output_mcp_config_file, output_mcp_config_list)


def update_readme_add_badge(input_file, output_file):
    """
        source: ./data/markdown/mcp/mcp_server_github_url_x.txt
        python process_ai_agent.py --data_file "./data/markdown/mcp/mcp_server_github_url_x.txt"
    """
    lines = read_file(input_file)

    ## demo unique id
    # demo_unique_id = "AI-Agent-Hub/ai_agent_index"

    github_cmd_line_prompt = """ 
repo='{github_repo}'
project_name='{repo_name}'

gh repo fork $repo
cd $project_name
git checkout -b dev_add_mcp_marketplace_support
## 


## modify README.md
git add README.md
git commit -m 'Add open mcp marketplace api support'
git push --set-upstream origin dev_add_mcp_marketplace_support

## create pr
gh pr create --base master --head dev_add_mcp_marketplace_support --title "Add Open MCP Marketplace API Support" --body "Hi, I would like to introduce MCP Marketplace Python and Typescript API and add support to your MCP Server, which allow any LLM AI Agent to integrate your MCP servers easily into the workflow, by searching relevant servers and tools meta and schemas, and give LLM more chances to know more about your MCP tools, increase usage from thousands of AI Agents or Applications. And here is a demo backend codes in python to integrate your servers tools for Claude function calls API..."
    """


    append_text_prompt = """
## Resources 

<details>
<summary><b>Open MCP Marketplace API Support</b></summary>

![MCP Marketplace User Review Rating Badge](http://www.deepnlp.org/api/marketplace/svg?{unique_id})|[Reviews](http://www.deepnlp.org/store/ai-agent/mcp-server/pub-{unique_id})|[GitHub](https://github.com/AI-Agent-Hub/mcp-marketplace)|[Doc](http://www.deepnlp.org/doc/mcp_marketplace)|[MCP Marketplace](http://www.deepnlp.org/store/ai-agent/mcp-server)

Allow AI/Agent/LLM to find this MCP Server via common python/typescript API, search and explore relevant servers and tools

***Example: Search Server and Tools***
```python
import anthropic
import mcp_marketplace as mcpm

result_q = mcpm.search(query="{target_query}", mode="list", page_id=0, count_per_page=100, config_name="deepnlp") # search server by category choose various endpoint
result_id = mcpm.search(id="{unique_id}", mode="list", page_id=0, count_per_page=100, config_name="deepnlp")      # search server by id choose various endpoint 
tools = mcpm.list_tools(id="{unique_id}", config_name="deepnlp_tool")
# Call Claude to Choose Tools Function Calls 

```

</details>
    """
    pattern = r"git@github.com:([^/]+)/([^/]+).git"

    doc_list = []
    for line in lines:
        item_json = json.loads(line)

        github_line = item_json["website"]
        unique_id = item_json["id"]
        
        pairs = unique_id.split("/")
        
        owner_name = pairs[0] if len(pairs) >= 2 else ""
        repo_name = pairs[1] if len(pairs) >= 2 else ""
        target_query = " ".join(repo_name.split("-"))

        print ("## DEBUG: Current unique_id %s" % unique_id)
        print ("## DEBUG: Current target_query %s" % target_query)

        github_cmd_line = github_cmd_line_prompt.format(github_repo=github_line, repo_name=repo_name)

        append_text = append_text_prompt.format(unique_id=unique_id, target_query=target_query)
        print(append_text)

        doc_list.append(github_cmd_line)
        doc_list.append("\n")
        doc_list.append(append_text)
    ## return
    # save_file("./data/markdown/mcp/README_ADD.md", doc_list)
    save_file(output_file, doc_list)
        # target repo folder
        # repo_abs_path = "../ai_agent_marketplace_hub/data/mcp/%s" % repo
        # if os.path.exists(repo_abs_path):
        #     with open(repo_abs_path, "a") as file:
        #         file.write("\n" + append_text + "\n")
        # else:
        #     print ("Data File Missing %s" % data_file)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, default="", help='Input Data File of list of Json ')
    parser.add_argument('--category', type=str, default="", help='category')
    parser.add_argument('--llm_summary_file', type=str, default="", help='llm summary file path')
    parser.add_argument('--output', type=str, default="", help='Output Data File of list of Json ')
    args = parser.parse_args()

    # process_ai_agents()
    # merge_all_data_ai_agent()
    # pre_process_merge_file_whitelist()
    # process_history_ai_agents_data()
    # process_main_text_body_and_images(args)
    # filter_merged_ai_agent_data()
    # process_history_ai_agents_data()
    ## MCP
    process_mcp_marketplace_json_data()
    # process_mcp_readme_data()
    # process_github_badge_result()
    # process_marketplace_mcp_json_config()
    # convert_github_url("./data/markdown/mcp/mcp_server_x_github.txt")

if __name__ == '__main__':
    main()    
