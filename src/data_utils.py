# -*- coding: utf-8 -*-

import codecs
import json
from constants import *

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

bing_search_result_filter_url_set = set(["blog", "news", "press", "post", "article"])
bing_search_result_domain_filter_set = set(read_file("./data/agent_meta/fetch_exclude_domain.txt"))
sites_filter_set = set(["Forbes", "Accenture", "Yahoo Finance", "Analytics Vidhya", "Medium", "segmentfault", "tieba"])
domain_ending_filter = set([".edu", ".gov"])

agent_schema = read_file("./data/agent_meta/agent_schema.json")[0]
agent_schema_dict = json.loads(agent_schema)

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

def normalize_url(url):
    """
    """
    last_token = url[len(url) - 1]
    clean_url = ""
    if last_token == "/":
        clean_url = url[0: len(url) - 1]
    else:
        clean_url = url
    return clean_url

def normalize_content_name(content_name):
    """
    """
    content_name_norm = content_name.lower()
    return content_name_norm

def get_sug_by_name(content_name):
    """
        seperator: " ", "."
        normalize content_name
    """
    import re
    content_name_lower = content_name.lower()
    content_name_lower_seg = re.split(r'[ .]+', content_name_lower)

    content_name_sug = "-".join(content_name_lower_seg)
    return content_name_sug

def get_domain(url):
    """
        url="http://www/google.xyz"
        get_domain(url) 'www.google.xyz'
        ads.google.com
    """
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    return parsed_url.netloc

def filter_no_agent_json_bing(input_json):
    """ fill json information of Bing
        content_name
        content_meta
        content
        website
        thumbnail_picture
        required files: rank, source:bing
    """
    if len(input_json) == 0:
        return True
    content_name = input_json["content_name"] if "content_name" in input_json else ""
    content_meta = input_json["content_meta"] if "content_meta" in input_json else ""
    content = input_json["content"] if "content" in input_json else ""
    website = input_json["website"] if "website" in input_json else ""
    thumbnail_picture = input_json["thumbnail_picture"] if "thumbnail_picture" in input_json else ""
    if_match_url_tag = False
    for tag in bing_search_result_filter_url_set:
        if tag in website:
            if_match_url_tag = True
            # print ("DEBUG: input_json %s skipped match url tag| %s" % (str(input_json), tag))
            break 
    if if_match_url_tag:
        return True

    if_match_content_name_filter = False 
    content_name_norm = content_name.lower()
    content_norm = content.lower()
    for tag in sites_filter_set:
        tag_norm = tag.lower()
        if tag in content_name_norm or tag in content:
            if_match_content_name_filter = True 
            # print ("DEBUG: input_json %s skipped match content tag| %s" % (str(input_json), tag))            
            break 
    if if_match_content_name_filter:
        return True 

    if_match_domain_filter = False 
    for domain in bing_search_result_domain_filter_set:
        website_domain = get_domain(website)
        if domain in website_domain:
            if_match_domain_filter = True
            break
    if if_match_domain_filter:
        return True 

    if_match_year_filter = False 
    for tag in ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]:
        if tag in website or tag in content_name:
            if_match_year_filter = True
            break
    if if_match_year_filter:
        return True

    if_match_domain_ending = False 
    for tag in domain_ending_filter:
        if tag in website:
            if_match_domain_ending = True 
            break 
    if if_match_domain_ending:
        return True

    ## don't filter
    return False


def clean_bing_content_text(text):
    """
    """
    import re
    # date_pattern = r"\d{4}年\d{2}月\d{2}日"
    date_pattern = r"\d{4}\\u5e74\d{2}\\u6708\d{2}\\u65e5\\u00a0\\u00b7"
    replacement_text = ""
    text_clean = re.sub(date_pattern, replacement_text, text)

    day = "\u65e5\u00a0\u00b7"

    if "\u5e74" in text_clean and "\u6708" in text_clean and day in text_clean:
        index = text_clean.find("\u65e5\u00a0\u00b7")
        text_clean = text_clean[index:]
        text_clean = text_clean.replace(day, "")
    text_clean = text_clean.strip()
    return text_clean


def match_black_item(query):
    """
    """
    black_item_list = ["dictatorship"]
    query_norm = query.lower()
    if_match = False
    for black_item in black_item_list:
        black_item_lower = black_item.lower()
        if black_item_lower in query_norm:
            if_match = True
            break 
    return if_match

def get_sug_by_name(content_name):
    """
        seperator: " ", "."
    """
    import re
    content_name_lower = content_name.lower()
    content_name_lower_seg = re.split(r'[ .]+', content_name_lower)

    content_name_sug = "-".join(content_name_lower_seg)
    return content_name_sug

def clean_content_name(content_name):
    """
        content_name
        input: google.com
        output: Google Com
        seperator: " ", "."
    """
    import re
    content_name_lower = content_name.lower()
    content_name_lower_seg = re.split(r'[ .]+', content_name_lower)
    content_name_sug = " ".join(content_name_lower_seg)
    return content_name_sug

def row_mapper_website(input_json):
    website = ""
    for key in ["website", "github", "paper", "content_url"]:
        if key in input_json and input_json[key] != "" and input_json[key] != "-":
            website = input_json[key]
            break
    return website

def fill_bing_data_json(input_json):    
    """
        # fill keys:
        metric
        Bing Rank
        content
        domain
    """
    # bing: Github -> Content Name
    try:
        content_name = input_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in input_json else ""
        website = input_json[KEY_WEBSITE] if KEY_WEBSITE in input_json else ""
        ## update content field, filter data
        content = input_json[KEY_CONTENT] if KEY_CONTENT in input_json else ""
        content_clean = clean_bing_content_text(content)
        rank = input_json[KEY_RANK] if KEY_RANK in input_json else DEFAULT_RANK
        ## Bing Data Unique ID: Domain get uniqe 
        domain = get_domain(website)
        if normalize_content_name(content_name) == CONTENT_NAME_GITHUB:
            input_json[KEY_CONTENT_NAME] = website
        input_json[KEY_CONTENT] = content_clean
        input_json[METRIC_BING_RANK] = float(rank)
        input_json[KEY_DOMAIN] = domain
        input_json[KEY_METRIC] = METRIC_BING_RANK
        return input_json
    except Exception as e:
        print (e)
        print ("DEBUG: Input Json is %s" % str(input_json))
        return {}

def fill_google_data_json(input_json):
    """
    """
    # bing: Github -> Content Name
    try:
        content_name = input_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in input_json else ""
        website = input_json[KEY_WEBSITE] if KEY_WEBSITE in input_json else ""
        ## update content field, filter data
        content = input_json[KEY_CONTENT] if KEY_CONTENT in input_json else ""
        content_clean = clean_bing_content_text(content)
        rank = input_json[KEY_RANK] if KEY_RANK in input_json else DEFAULT_RANK
        domain = get_domain(website)

        
        if normalize_content_name(content_name) == CONTENT_NAME_GITHUB:
            input_json[KEY_CONTENT_NAME] = website
        input_json[KEY_CONTENT] = content_clean
        input_json[METRIC_GOOGLE_RANK] = float(rank)
        input_json[KEY_DOMAIN] = domain
        input_json[KEY_METRIC] = METRIC_GOOGLE_RANK
        return input_json

    except Exception as e:
        print (e)
        print ("DEBUG: fill_google_data_json failed input Json is %s" % str(input_json))
        return {}

def row_mapper_agent(input_json):
    """
        subfield: category

        map row
        schema
             'publisher_id'： required
             'content_name': required
             'content',  required
             'field', required
             'subfield', required
             'content_tag_list', required
             'website': required        
    """
    output_json = {}    
    # content_name = input_json["content_name"] if "content_name" in input_json else ""
    content_name = ""
    for key in ["content_name", "name"]:
        if key in input_json and input_json[key] != "":
            content_name = input_json[key]
    if content_name == "":
        return None, None
    ## 

    output_json["content_name"] = clean_content_name(content_name)
    output_json["publisher_id"] = get_sug_by_name(content_name)

    # content
    for key in ["field", "description", "content"]:
        if key in input_json and input_json[key] != "":
            output_json["content"] = input_json[key]
    # output_json["content"] = input_json["content"] if "content" in input_json else ""
    output_json["field"] = "AI AGENT"

    # default
    category = ""
    for key in ["subfield", "category"]:
        if key in input_json and input_json[key] != "":
            category = input_json[key]
    if category == "":
        category = "AI AGENT"
    output_json["subfield"] = category
    # tags: 包含了 subfield
    content_tag_list_raw = ""
    for key in ["tags", "content_tag_list"]:
        if key in input_json and input_json[key] != "":
            content_tag_list_raw = input_json[key]
    content_tag_list_raw = content_tag_list_raw + "," + category + "," + "AI AGENT"
    content_tag_list = clean_content_tag_list(content_tag_list_raw)
    output_json["content_tag_list"] = content_tag_list

    # url
    website = input_json["website"] if "website" in input_json else ""
    paper = input_json["paper"] if "paper" in input_json else ""
    github = input_json["github"] if "github" in input_json else ""
    content_url = input_json["content_url"] if "content_url" in input_json else ""

    # find first non-empty url
    output_json["website"] = row_mapper_website(input_json)

    # priority
    thumbnail_image_url = ""
    for key in [KEY_THUMBNAIL_PICTURE, "Image"]:
        if key in input_json and input_json[key] != "" and input_json[key] != "-":
            thumbnail_image_url = input_json[key]
            break
    ## call external url to fetch image
    output_json[KEY_THUMBNAIL_PICTURE] = thumbnail_image_url    

    # priority
    upload_image_files = ""
    for key in [KEY_UPLOAD_IMAGE_FILES, "Image"]:
        if key in input_json and input_json[key] != "" and input_json[key] != "-":
            upload_image_files = input_json[key]
            break
    output_json[KEY_UPLOAD_IMAGE_FILES] = upload_image_files
    ## image keys
    ## post set status to 0
    output_json["status"] = "1"

    ## input_json
    ext_info_json = {}
    for key in input_json.keys():
        value = input_json[key]
        if key not in output_json:
            ext_info_json[key] = value
            # update input_json
            output_json[key] = value
    ## merge ext_info
    ext_info = json.dumps(ext_info_json)
    output_json["ext_info"] = ext_info

    ## Check Required Fields
    if_missing = check_required_fields(output_json)
    return output_json, if_missing

def clean_content_tag_list(content_tag_list_raw):
    tag_list = content_tag_list_raw.lower().split(",")
    tag_set = set(tag_list)
    tag_list_unique = list(tag_set)

    content_tag_list = [tag.upper() for tag in tag_list_unique]
    content_tag_list_str = ",".join(content_tag_list)
    return content_tag_list_str

def test_clean_content_tag_list():
    content_tag_list_raw = "AI Agent,Raw,Haha,AI AGENT"
    content_tag_list = clean_content_tag_list(content_tag_list_raw)

def check_required_fields(input_json):
    required_fields = agent_schema_dict["required"]
    optional_fields = agent_schema_dict["optional"]
    missing_required_fields = []
    for field in required_fields:
        if field not in input_json or input_json[field] == "" or input_json[field] == "-":
            missing_required_fields.append(field)

    if_missing = False
    if len(missing_required_fields) > 0:
        content_name = input_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in input_json else ""
        print ("DEBUG: Input Json Missing Field %s, %s" % (",".join(missing_required_fields), content_name))
        if_missing = True 
    else:
        if_missing = False 
    return if_missing
