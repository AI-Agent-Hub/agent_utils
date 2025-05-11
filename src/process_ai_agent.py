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
from fetch_ai_agent import process_main_page_aigc_content, get_merge_all_data_ai_agent, read_fetch_whitelist_path

from bs4 import BeautifulSoup
from func_timeout import func_set_timeout, FunctionTimedOut
import ai_agent_marketplace

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
        content_id 关系
    """
    import requests
    data_file_folder = "./ai_agent_marketplace/data/merge"
    output_file = "./ai_agent_marketplace/data/merge/statistic/merge_ai_agent_statistic.json"
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

def parse_git_readme():
    folder_path = "./mcp_server_dev"
    content_dict = {}
    for sub_folder in os.listdir(folder_path):
        sub_folder_path = os.path.join(folder_path, sub_folder)
        readme_file = os.path.join(sub_folder_path, "README.md")
        if os.path.exists(readme_file):
            lines = read_file(readme_file)
            readme_text = "\n".join(lines)
            content_dict[sub_folder] = readme_text
    return content_dict

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
    input_file = "./data/markdown/mcp/mcp_server_README_20250414.md"
    lines = read_file(input_file)

    pattern = r'\[\s*(.*?)\s*\]\((.*?)\)([^[]+)'

    pattern_url = r'\[\s*(.*?)\s*\]\((.*?)\)'
    image_pattern = r"\<\s*src=\"(.*?)\"\s*\/>"

    base_url = "https://github.com/modelcontextprotocol/servers"
    # name_prefix = "**["
    img_pregix = "<img"

    # load git content
    content_dict = parse_git_readme()
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
    save_file("./data/markdown/mcp/mcp_server_merge.json", output_json_list)

def process_url():
    """
        agent github
    """
    import ai_agent_marketplace as aa

    url = ""
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

def convert_github_url(github_path):
    """
        convert from github_path to git
    """
    input_file = "./data/markdown/mcp/mcp_server_github.txt"
    lines = read_file(input_file)

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
    output_file = "./data/markdown/mcp/mcp_server_github_url.txt"
    save_file(output_file, git_url_list)

    ## scripts
    bash_lines = []
    bash_output_file = "./data/markdown/mcp/mcp_server_github_url.sh"
    bash_headers = "#!/bin/bash"
    bash_lines.append(bash_line)
    for git_url in git_url_list:
        bash_line = "git clone %s" % git_url 
        bash_lines.append(bash_line)
    save_file(bash_output_file, bash_lines)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, default="", help='Input Data File of list of Json ')
    parser.add_argument('--category', type=str, default="", help='category')
    parser.add_argument('--llm_summary_file', type=str, default="", help='llm summary file path')
    parser.add_argument('--output', type=str, default="", help='Output Data File of list of Json ')
    args = parser.parse_args()

    process_mcp_readme_data()

if __name__ == '__main__':
    main()    
