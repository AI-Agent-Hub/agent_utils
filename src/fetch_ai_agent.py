# -*- coding: utf-8 -*-

import codecs
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import os
import traceback
import io
import random
import time
from func_timeout import func_set_timeout, FunctionTimedOut

from constants import *
from data_utils import *
from requests_utils import *

def is_github_url(url):
    """
    """
    if_github_url = False
    if "github" in url:
        if_github_url = True
    return if_github_url

def get_github_icon():
    """
        output_json["thumbnail_picture"] = image
        output_json["upload_image_files"] = image
    """
    image_dict = {}
    image_dict[KEY_THUMBNAIL_PICTURE] = "https://github.githubassets.com/assets/pinned-octocat-093da3e6fa40.svg"
    image_dict[KEY_UPLOAD_IMAGE_FILES] = ",".join([
        # "https://github.com/fluidicon.png"
        "https://github.githubassets.com/assets/github-mark-57519b92ca4e.png"
        , "https://github.githubassets.com/assets/github-logo-55c5b9a1fe52.png"
        # , "https://github.githubassets.com/favicons/favicon.svg"]
    ])
    return image_dict

def is_arxiv_url(url):
    """
    """
    if_arxiv_url = False
    if "arxiv.org" in url:
        if_arxiv_url = True
    return if_arxiv_url

def get_arxiv_icon():
    """
        output_json["thumbnail_picture"] = image
        output_json["upload_image_files"] = image
    """
    image_dict = {}
    image_dict[KEY_THUMBNAIL_PICTURE] = "https://arxiv.org/static/browse/0.3.4/images/icons/favicon-32x32.png"
    image_dict[KEY_UPLOAD_IMAGE_FILES] = ",".join([
        "https://arxiv.org/static/browse/0.3.4/images/icons/favicon-32x32.png"
    ])
    return image_dict

def process_main_page_aigc_content(data_file_folder):
    """
        data_folder = "./data/merge/maintext/"
        markdown_file_path = "./data/merge/maintext/coding_agent_main.md"
        mardown: each domain get one list of sections
    """
    input_file_path_list = []
    for sub_file in os.listdir(data_file_folder):
        sub_file_path = os.path.join(data_file_folder, sub_file)
        if ".md" in sub_file_path:
            input_file_path_list.append(sub_file_path)
    sections_dict = {}
    domain_dict = {}
    for data_file in input_file_path_list:
        # data_file = "./data/merge/maintext/coding_agent_main.md"
        lines = read_file(data_file)
        sections = []
        cur_section = []
        cur_line = ""
        main_url = ""
        domain = ""
        for line in lines:
            if line == "":
                continue
            if line.startswith("# "):
                ## start_new section
                if len(cur_section) > 0:
                    sections.append(cur_section)
                    section_content = " ".join(cur_section)
                    sections_dict[main_url] = section_content
                    cur_section_list = domain_dict[domain] if domain in domain_dict else []
                    cur_section_list.append(section_content)
                    domain_dict[domain] = cur_section_list
                ## new content
                cur_section = []
                main_url = normalize_url(line.replace("# ", ""))
                domain = get_domain(main_url)
            else:
                cur_section.append(line)
        ## process last one
        if len(cur_section) > 0:
            sections.append(cur_section)
            if main_url not in sections_dict:

                section_content = " ".join(cur_section)
                sections_dict[main_url] = section_content

                cur_section_list = domain_dict[domain] if domain in domain_dict else []
                cur_section_list.append(section_content)
                domain_dict[domain] = cur_section_list
            else:
                print ("DEBUG: process_main_page_aigc_content main_url duplicate %s" % main_url)
    print ("DEBUG: Sections Processed Count %d" % len(sections_dict))
    return sections_dict, domain_dict

def test_fetch_website_maintext(url, driver):
    url = "https://www.workday.com/"
    from bs4 import BeautifulSoup
    from selenium import webdriver
    driver = webdriver.Chrome()
    maintext_dict = fetch_website_maintext(url, driver)
    print (maintext_dict)

def fetch_agent_github_demo():

    output_file = "./data/raw/raw_agent_education.json"
    q = "education+ai+agent"
    q_type = "repositories"
    base_url = "https://github.com/search?q=%s&type=%s&p=%s"
    total_pages = 3 
    total_list = []
    for p in range(total_pages):
        detail_url = base_url % (q, q_type, (p+1))
        output_json_list, pagination_url_list, max_page_number = fetch_agent_github_detail(detail_url, get_date())
        print ("DEBUG: Fetch Query q %s, page %d, cnt %d" % (q, p, len(output_json_list)))
        total_list.extend(output_json_list)
    print ("Total List Size %d" % len(total_list))
    save_file(output_file, total_list)

def get_search_keyword(query, separator):
    """
    """
    query_norm = query.lower()
    keywords = query_norm.split(" ")
    query_merge = separator.join(keywords)
    return query_merge

def get_query_normalize(query, separator):
    """
    """
    query_norm = query.lower()
    keywords = query_norm.split(" ")
    query_merge = separator.join(keywords)
    return query_merge

def fetch_agent_from_github(query, output_file, driver, date):
    """
        Args:
            query = "teacher agent"
            output_file: save_output_file.json
            date: str

        output
            {
                "user_name": "xszyou",
                "repo_name": "Fay",
                "url": "https://github.com/xszyou/Fay",
                "description": "Fay is an open-source digital human framework integrating language models and digital characters. It offers retail, assistant, and agent \u2026",
                "repo_type": "JavaScript",
                "repo_star": "9.7k",
                "update": "Updated 8 days ago"
            }
    """
    time_sleep_interval = 5
    total_list = []
    base_url = "https://github.com/search?q=%s&type=%s"
    try:
        q = get_search_keyword(query, "+")
        q_type = "repositories"
        ## 1.0 Fetch Page 1
        main_url = base_url % (q, q_type)
        output_json_list, pagination_url_list, max_page_number = fetch_agent_github_detail(main_url, date)
        print ("DEBUG: Start Fetching Page %d from URL %s" % (1, main_url))
        print ("DEBUG: Fetch Query q %s, page %s, cnt %d" % (q, "1", len(output_json_list)))
        total_list.extend(output_json_list)
        ## 2.0 Fetch Page 2 to remain
        if max_page_number > 1:
            for i in range(max_page_number):
                cur_page_number = (i + 1)
                if cur_page_number == 1:
                    continue
                page_url = (base_url + "&p=%d") % (q, q_type, cur_page_number)
                output_json_list, pagination_url_list, cur_max_page_number = fetch_agent_github_detail(page_url, date)

                print ("DEBUG: Start Fetching Page %d from URL %s" % (cur_page_number, page_url))
                print ("DEBUG: Fetch Query q %s, page %s, cnt %d" % (q, cur_page_number, len(output_json_list)))
                total_list.extend(output_json_list)
                ## sleep
                time.sleep(time_sleep_interval)
        # statictics
        print ("Total List Size %d for query %s" % (len(total_list), query))
        save_file(output_file, total_list)
    except Exception as e:
        print ("### DEBUG: fetch_agent_from_github %s, %s failed" % (query, output_file) )
        print (e)
        traceback.print_exc()

def clean_arxiv_text(text):

    text_clean = text.strip()
    text_clean = text_clean.replace("\n", "")
    return text_clean

def fetch_agent_from_arxiv(query, output_file, driver, date):
    """
        ## API
        Doc: https://export.arxiv.org/api/query?search_query=all:AI+Agent&start=0&max_results=1000&sortBy=submittedDate
        
        ## Webpage
        https://arxiv.org/search/?searchtype=all&query=AI+Agent&abstracts=show&size=50&order=-submitted_date
        https://info.arxiv.org/help/api/user-manual.html
        Base API: http://export.arxiv.org/api/query?search_query=all:%s

        search_query = kwargs['search_query'] if 'search_query' in kwargs else ('search_query=all:%s' % topic)
        start = kwargs["start"] if "start" in kwargs else 0
        max_results = kwargs["max_results"] if "max_results" in kwargs else 10
        sort_by = kwargs["sortBy"] if "sortBy" in kwargs else "lastUpdatedDate"
        sort_order = kwargs["sortOrder"] if "sortOrder" in kwargs else "descending"
        
        AI Agent
    """
    # base_url = 'http://export.arxiv.org/api/query'
    url = 'http://export.arxiv.org/api/query?search_query=all:%s' % query
    # required fields
    params_dict = {}
    params_dict["start"] = 0
    params_dict["max_results"] = 1000
    params_dict["sortBy"] = "submittedDate"  ## 提交日志排到排
    params_dict["sortOrder"] = "descending"
    params_dict["search_query"] = get_query_normalize(query, "+")

    # output keys
    KEY_URL = "url"
    KEY_PDF_DOWNLOAD = "url_pdf_download"
    KEY_PRIMARY_CATEGORY = "primary_category"
    KEY_CATEGORY = "category"

    # optional fields
    for key in params_dict.keys():
        url = url + "&" + ("%s=%s" % (key, params_dict[key]))
    print ("### DEBUG: Calling ArxivPaperAPI input args is: %s, URL: %s" % (str(params_dict), url))

    # print ("DEBUG: Fetching Arxive Paper list from API %s" % url)
    custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    headers = {
        'User-Agent': custom_user_agent,
    }
    response = requests.get(url, params=params_dict, headers=headers, timeout=REQUESTS_TIMEOUT)
    soup = BeautifulSoup(response.text, features="html.parser")
    entries = soup.find_all('entry')
    print ("DEBUG: Getting Papers Entries size %d" % len(entries) )
    entry_keys = ["id", "updated", "published", "title", "summary", "author", "link", "category", "arxiv:comment", "arxiv:primary_category"]
    entry_json_list = []
    for entry in entries:
        try:
            entry_json = {}
            for key in entry_keys:
                value_list = entry.find_all(key)
                # special treatment
                if key == "link":
                    if len(value_list) == 2 and value_list[0] is not None and value_list[1] is not None:
                        html_url = value_list[0]["href"] if value_list[0].has_attr("href") else ""
                        pdf_url = value_list[1]["href"] if value_list[1].has_attr("href") else ""
                        entry_json[KEY_URL] = html_url
                        entry_json[KEY_PDF_DOWNLOAD] = pdf_url
                elif key == "arxiv:primary_category":
                    if len(value_list) > 0 and value_list[0] is not None:
                        category = value_list[0]["term"] if value_list[0].has_attr("term") else ""
                        entry_json[KEY_PRIMARY_CATEGORY] = category
                elif key == "category":
                    category_list = [value["term"] for value in value_list]
                    entry_json[KEY_CATEGORY] = category_list
                else:
                    # plain text
                    if len(value_list) == 1:
                        entry_json[key] = clean_arxiv_text(value_list[0].text)
                    else:
                        # e.g. author
                        value_text_list = [clean_arxiv_text(value.text) for value in value_list]
                        entry_json[key] = value_text_list
            ## add
            entry_json[KEY_SOURCE] = DATA_SOURCE_ARXIV 
            entry_json[KEY_DT] = date 
            entry_json_list.append(json.dumps(entry_json))
        except Exception as e:
            print (e)

    save_file(output_file, entry_json_list)
    return entry_json_list

def get_fetch_whitelist_google(query, category_name, query_append_list, metric, rank_offset, date, driver, kwargs):
    """
        Inputs: 
            query, 
            category_name,
            fetch_whitelist_path
            driver
        Output:
            list: []
    """
    if len(query_append_list) == 0:
        print ("DEBUG: get_fetch_whitelist empty...")
        return []
    fill_extinfo_enable = kwargs[FILL_EXTINFO_ENABLE] if FILL_EXTINFO_ENABLE in kwargs else False
    start_page_id = 0
    max_results_topk = 3
    max_retry_cnt = 3
    output_data_list = []
    try:
        for query in query_append_list:
            ## interval
            time.sleep(RETRY_INTERVAL_GOOGLE)
            
            merge_query = category_name + " " + query
            ## save current data_json
            data_json = {}
            retry_cnt = 0
            ## html == "" is not a good criteria for google verification, using result is None instead
            # html = ""
            results = None
            ## retry multiple times
            while (results is None and retry_cnt < max_retry_cnt):
                retry_cnt += 1
                time.sleep(RETRY_INTERVAL)
                query_encode_en = get_search_keyword(merge_query, "+")
                url = GOOGLE_base_query_template_en % query_encode_en + GOOGLE_base_query_template_param

                # fetch first page
                url_param = {}
                url_param["start"] = 0
                for key, value in url_param.items():
                    url = url + "&" + "%s=%s" % (key, str(value))

                print ("DEBUG: Start Query %s, Fetching URL Page ID %d, from Google URL %s, Retry Times %d" % (merge_query, 0, url, retry_cnt))
                custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                headers = {
                    'User-Agent': custom_user_agent,
                    'Accept': '*/*'
                }
                html = ""
                try:
                    # driver.get(url)
                    function_timeout_wrapper(driver, url)
                    print ("DEBUG: Fetch URL Succeed|%s" % url)
                except FunctionTimedOut as e1:
                    print ("DEBUG: Fetch URL Timeout|%s" % url)
                html = driver.page_source
                ## fetch second time for evaluation
                soup = BeautifulSoup(html, "html.parser")
                results = soup.select('div[id="rso"]')[0] if len(soup.select('div[id="rso"]')) > 0 else None

                if results is None:
                    print ("###### DEBUG: Current Page RSO result is None...")
                    continue
            if results is None:
                print ("###### DEBUG: Current Page RSO result is None after retring times|%d" % retry_cnt)
                continue

            div_results_list = results.findChildren("div" , recursive=False)
            valid_rank = start_page_id
            for div_result in div_results_list:
                if valid_rank >= max_results_topk:
                    print ("Already Fetching Enough Items Under current page...")
                    break
                data_json = process_google_search_result_algo(div_result, valid_rank, fill_extinfo_enable, driver)
                if len(data_json) > 0:
                    valid_rank += 1
                    ## fix new content_name to make it more reasonable
                    ## e.g. OpenAI AI Search Agent
                    content_name = data_json["content_name"] if "content_name" in data_json else ""
                    # data_json["content_name"] = content_name + " " + category_name
                    data_json["content_name"] = content_name
                    data_json["field"] = "AI AGENT"
                    data_json["subfield"] = category_name
                    data_json["category"] = category_name
                    data_json["content_tag_list"] = category_name + ",AI AGENT"
                    data_json[KEY_SOURCE] = DATA_SOURCE_GOOGLE
                    data_json[KEY_DT] = date
                    # update Rank
                    cur_rank = data_json[metric] if metric in data_json else 0
                    cur_rank += rank_offset
                    data_json[metric] = cur_rank
                    ## add current page, current item
                    output_data_list.append(json.dumps(data_json))
    except Exception as e:
        print ("DEBUG: get_fetch_whitelist failed...")
        print (e)
    print ("DEBUG: output_data_list return size|%d" % len(output_data_list))
    return output_data_list

def fetch_agent_from_google_by_category(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs):
    """
        Only Fetch Agent From Bing By Category, Withough fill specific website
    """
    import requests
    from urllib.parse import quote
    from bs4 import BeautifulSoup

    if_search_en = True 
    fill_extinfo_enable = kwargs[FILL_EXTINFO_ENABLE] if FILL_EXTINFO_ENABLE in kwargs else False

    output_data_list = []
    output_data_json_list = []

    url = ""
    start_page_id_list = [1, 11, 21, 31, 41, 51]
    item_per_page = 10
    ## Each Page Max Retry Cnt
    max_retry_cnt = 3
    try:
        ## Each Page Max Retry Cnt
        for start_page_id in start_page_id_list:
            
            sleep_interval = RETRY_INTERVAL_GOOGLE + random.randint(0, 10)
            time.sleep(sleep_interval)

            query_encode_en = get_search_keyword(query, "+")
            url = GOOGLE_base_query_template_en % query_encode_en + GOOGLE_base_query_template_param

            url_param = {}
            url_param["start"] = start_page_id
            for key, value in url_param.items():
                url = url + "&" + "%s=%s" % (key, str(value))

            print ("DEBUG: Start Query %s, Fetching URL Page ID %d, from Google URL %s" % (query, start_page_id, url))

            custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
            headers = {
                'User-Agent': custom_user_agent,
                'Accept': '*/*'
            }

            ## retry 3 times
            results = None
            retry_cnt = 0
            while (results is None and retry_cnt < max_retry_cnt):
                time.sleep(RETRY_INTERVAL)
                retry_cnt += 1
                html = ""
                try:
                    function_timeout_wrapper(driver, url)
                    html = driver.page_source
                    print ("DEBUG: Fetch URL Succeed|%s" % url)                
                except FunctionTimedOut as e1:
                    print ("DEBUG: Fetch URL Timeout|%s" % url)

                soup = BeautifulSoup(html, "html.parser")
                results = soup.select('div[id="rso"]')[0] if len(soup.select('div[id="rso"]')) > 0 else None
            ## check if results is still None after max_retry times
            if results is None:
                print ("DEBUG: Current Page RSO result is None...")
                continue
            div_results_list = results.findChildren("div" , recursive=False)
            valid_rank = start_page_id
            for div_result in div_results_list:
                data_json = process_google_search_result_algo(div_result, valid_rank, fill_extinfo_enable, driver)
                if len(data_json) > 0:
                    valid_rank += 1
                    data_json["field"] = "AI AGENT"
                    data_json["subfield"] = category_name
                    data_json["category"] = category_name
                    data_json["content_tag_list"] = category_name + ",AI AGENT"
                    data_json[KEY_SOURCE] = DATA_SOURCE_GOOGLE
                    data_json[KEY_DT] = date
                    output_data_list.append(json.dumps(data_json))
                    output_data_json_list.append(data_json)

        print ("DEBUG: fetch_agent_from_google Processing Page Size %d" % len(output_data_list))
        
    except Exception as e:
        print (e)

    print ("DEBUG: fetch_agent_from_google_by_category Processing output_data_json_list total size %d" % len(output_data_json_list))
    return output_data_json_list

def fetch_agent_from_google(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs):
    """ 
        query search
        
        query = "AI AGENT Coding"
        query = "https://www.google.com/search?q=AI+Coding+Agent&sca_esv=71db54fb86614d0a&sxsrf=AHTn8zp43NUyTOi0S7aH3TidYHQHJhQYXw%3A1739691549541&source=hp&ei=HZaxZ7vWHo6U0PEP96zvOQ&iflsig=ACkRmUkAAAAAZ7GkLcbvNO6dx13nH118bQPoeoalRQM0&ved=0ahUKEwj72M6G2MeLAxUOCjQIHXfWOwcQ4dUDCBc&uact=5&oq=AI+Coding+Agent&gs_lp=Egdnd3Mtd2l6Ig9BSSBDb2RpbmcgQWdlbnQyCBAAGIAEGMsBMggQABiABBjLATIIEAAYgAQYywEyCBAAGIAEGMsBMggQABiABBjLATIEEAAYHjIGEAAYBRgeMgYQABgFGB4yBhAAGAUYHjIGEAAYBRgeSK8VUABYlBNwAHgAkAEAmAH-AqABhiKqAQYyLTEzLjK4AQPIAQD4AQGYAg-gArUiwgIKECMYgAQYJxiKBcICBBAjGCfCAgsQLhiABBjRAxjHAcICBRAAGIAEmAMAkgcGMi0xMy4yoAePUQ&sclient=gws-wiz"
        
        format: https://www.google.com/search?q=AI+Coding+Agent&start=0
    
        category_whitelist_dict: dict, key cateogory_name, value list of content dict
        optional fields
            "subfield", "category", "rank", "content_tag_list"
    """
    import requests
    from urllib.parse import quote
    from bs4 import BeautifulSoup

    if_search_en = True 
    url = ""

    fill_extinfo_enable = kwargs[FILL_EXTINFO_ENABLE] if FILL_EXTINFO_ENABLE else False

    start_page_id_list = [0, 10, 20, 30, 40, 50]
    item_per_page = 10

    # output_data_list = []
    output_data_json_list = []

    ## switch_between mode
    channels = [CHANNEL_GOOGLE_CATEGORY, CHANNEL_GOOGLE_WHITELIST_QUERY, CHANNEL_GOOGLE_HISTORY_ITEM, CHANNEL_GOOGLE_WHITELIST_META]
    # google_search_channel = [CHANNEL_WHITELIST_SEARCH, CHANNEL_WHITELIST]
    print ("DEBUG: google_search_channel enable|" + str(channels))

    if CHANNEL_GOOGLE_CATEGORY in channels:
        output_data_json_category_list = fetch_agent_from_google_by_category(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs)
        output_data_json_list.extend(output_data_json_category_list)

    if CHANNEL_GOOGLE_HISTORY_ITEM in channels:
        
        skipped_item = get_history_secondary_fetched_item(category_name, output_data_json_list, category_directory_dict)
        ## fetch  whitelist sources with meta images
        print ("DEBUG: fetch_agent_from_google CHANNEL_GOOGLE_HISTORY_ITEM category_name %s append query list %s" % (category_name, str(",".join(skipped_item))))
        history_fetch_data_list = get_fetch_whitelist_google(query, category_name, skipped_item, KEY_GOOGLE_RANK, GOOGLE_PAGE_RANK_BASE_OFFSET, date, driver, kwargs)
        if len(history_fetch_data_list) > 0:
            print ("DEBUG: fetch_agent_from_google Append history_fetch_data_list Size %d" % len(history_fetch_data_list))
            # output_data_list.extend(whitelist_fetch_data_list)
            output_data_json_list.extend(history_fetch_data_list)

    # step 2. fetch category name + history item + append search query
    ## calculate historical directory, not exist in current list item
    if CHANNEL_GOOGLE_WHITELIST_QUERY in channels:

        ## fetch from whitelist sources with meta images
        query_append_list = query_append_dict[category_name] if category_name in query_append_dict else []
        print ("DEBUG: fetch_agent_from_google CHANNEL_BING_WHITELIST category_name %s append query list %s" % (category_name, str(",".join(query_append_list))))
        whitelist_fetch_data_list = get_fetch_whitelist_google(query, category_name, query_append_list, KEY_GOOGLE_RANK, GOOGLE_PAGE_RANK_BASE_OFFSET, date, driver, kwargs)
        if len(whitelist_fetch_data_list) > 0:
            print ("DEBUG: fetch_agent_from_google Append whitelist_fetch_data_list Size %d" % len(whitelist_fetch_data_list))
            # output_data_list.extend(whitelist_fetch_data_list)
            output_data_json_list.extend(whitelist_fetch_data_list)

    if CHANNEL_GOOGLE_WHITELIST_META in channels:
        ## append whitelist
        whitelist_content_list = category_whitelist_dict[category_name] if category_name in category_whitelist_dict else []
        for content_json in whitelist_content_list:
            output_data_json_list.append(content_json)

    ## if fill_ext_info
    output_data_list = []
    fill_extinfo_enable = kwargs[FILL_EXTINFO_ENABLE] if FILL_EXTINFO_ENABLE in kwargs else False
    print ("DEBUG: fetch_agent_from_google enable|" + str(fill_extinfo_enable))    
    if fill_extinfo_enable:
        output_data_json_list_filled = fill_ext_info_data(output_data_json_list, driver)
        for data_json in output_data_json_list_filled:
            output_data_list.append(json.dumps(data_json))
    else:
        for data_json in output_data_json_list:
            output_data_list.append(json.dumps(data_json))

    ## save 
    output_file_folder = os.path.dirname(output_file)
    if not os.path.exists(output_file_folder):
        os.mkdir(output_file_folder)
    save_file(output_file, output_data_list)

def test_google_search_result():

    query = "AI Coding Agent"
    category_name = "Coding Agent"
    output_file = "./data/google/test_coding_agent.json"
    fetch_agent_from_google(query, category_name, output_file)

def process_google_search_result_algo(div_result, cur_page_rank, fill_extinfo_enable, driver):
    """
        valid_rank: int
    """
    data_json = {}
    try:
            ## 
            title = ""
            url = ""
            header_text = ""
            cite_text = "" # e.g. a > b >c
            description_text = ""

            # data-snhf = 0, data-snhf = 1, data-snhf = 2
            # row 1: data-snhf = '0'
            div_row_header = div_result.select('div[data-snhf="0"]')[0] if len(div_result.select('div[data-snhf="0"]')) > 0 else None
            div_span_list = div_row_header.select('span')
            ## 
            for div_span in div_span_list:
                if len(div_span.select("a")) > 0 and len(div_span.select("h3")) > 0:
                    ## header
                    div_title_a = div_span.select("a")[0] 
                    url = div_title_a["href"]
                    title = div_span.select("h3")[0].text
                    # cite
                    div_summary = div_title_a.findChildren("div" , recursive=False)
                    if div_summary is not None:

                        cite = div_summary[0].select("cite") if len(div_summary) > 0 else None
                        cite_text = cite[0].text if (cite is not None and len(cite) > 0) else ""

                        summary_span_list = div_summary[0].findChildren("span" , recursive=True)

                        # find first root span
                        span_text_list = []
                        for div_summary_span in summary_span_list:
                            if len(div_summary_span.select("div")) == 0:
                                span_text_list.append(div_summary_span.text)
                        ## add 
                        header_text = span_text_list[0] if len(span_text_list) > 0 else ""
                        cite_text = span_text_list[1] if len(span_text_list) > 1 else ""
                else:
                    continue

            # row 2:  data-sncf = '1'
            div_row_content = div_result.select('div[data-sncf="1"]')[0] if len(div_result.select('div[data-sncf="1"]')) > 0 else None
            description_text = div_row_content.text if div_row_content is not None else ""

            data_json[KEY_GOOGLE_CONTENT_NAME] = header_text
            data_json[KEY_GOOGLE_CONTENT_META] = title
            data_json[KEY_GOOGLE_CONTENT] = description_text
            data_json[KEY_GOOGLE_WEBSITE] = url
            data_json[KEY_GOOGLE_RANK] = cur_page_rank
            data_json[KEY_SOURCE] = DATA_SOURCE_GOOGLE

    except Exception as e:
        print (e)
    return data_json

def fetch_from_google_verification(driver):
        
    try:
        query = "AI Agent"
        
        query_encode_en = get_search_keyword(query, "+")
        url = GOOGLE_base_query_template_en % query_encode_en + GOOGLE_base_query_template_param

        url_param = {}
        start_page_id = 0
        url_param["start"] = start_page_id
        for key, value in url_param.items():
            url = url + "&" + "%s=%s" % (key, str(value))

        print ("DEBUG: Start Query %s, Fetching URL Page ID %d, from Google URL %s" % (query, start_page_id, url))
        custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
        headers = {
            'User-Agent': custom_user_agent,
            'Accept': '*/*'
        }
        html = ""
        try:
            print ("DEBUG: Fetching URL from %s" % url)
            driver.get(url)   
            html = driver.page_source
        except Exception as e:
            print (e)

        time.sleep(30)    
    except Exception as e:
        print (e)

#### Bing Search Engine

def get_fetch_whitelist_bing(query, category_name, query_append_list, metric, rank_offset, date, driver, kwargs):
    """
        tag_path: 
            ol[id='b_results']
            li

        Inputs: 
            query, 
            category_name,
            query_append_list:  list of [content_name] to top 1
            fetch_whitelist_path
            driver
            query_append_list: Open

        Output:
            list: []
        ## retry maximum times
    """
    if len(query_append_list) == 0:
        print ("DEBUG: get_fetch_whitelist empty...")
        return []
    fill_extinfo_enable = kwargs[FILL_EXTINFO_ENABLE] if FILL_EXTINFO_ENABLE in kwargs else False
    start_page_id = 0
    max_results_topk = 3
    max_retry_cnt = 3
    output_data_list = []
    output_data_list_json = []
    if_search_en = True
    try:
        for query in query_append_list:
            merge_query = category_name + " " + query
            ## save current data_json
            data_json = {}
            retry_cnt = 0
            
            results = None
            ## retry multiple times
            while (results is None and retry_cnt < max_retry_cnt):
                retry_cnt += 1
                time.sleep(RETRY_INTERVAL_BING)
                
                url = ""
                if if_search_en:
                    # base_query_template_en = "https://www.bing.com/search?q=%s&form=QBLHCN&sp=-1&lq=0&sc=12-9&qs=n&sk=&cvid=AA2C705F2B504D6E825F3BD1CFABE444&ghsh=0&ghacc=0&ghpl="
                    query_encode_en = get_search_keyword(merge_query, "+")
                    url = base_query_template_en % (query_encode_en) + base_query_template_en_param

                    url_param = {}
                    url_param["first"] = start_page_id
                    url_param["FORM"] = "PERE"
                    for key, value in url_param.items():
                        url = url + "&" + "%s=%s" % (key, str(value))
                else:
                    query_encode = quote(merge_query)
                    query_norm_encode = quote(merge_query.lower())
                    url = base_query_template_cn % (query_encode) + base_query_template_cn_param
                    url_param = {}
                    url_param["ensearch"] = 1
                    for key, value in url_param.items():
                        url = url + "&" + "%s=%s" % (key, str(value))

                print ("DEBUG: Start Query %s, Fetching URL Page ID %d, from Bing URL %s" % (merge_query, start_page_id,url))

                custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                headers = {
                    'User-Agent': custom_user_agent,
                    'Accept': '*/*'
                }

                html = ""
                try:
                    function_timeout_wrapper(driver, url)
                    html = driver.page_source
                    print ("DEBUG: Fetch URL Succeed|%s" % url)                                
                except FunctionTimedOut as e1:
                    print ("DEBUG: Fetch URL Timeout|%s" % url)
                # each merged query fetch max_time
                soup = BeautifulSoup(html, "html.parser")
                ## srp zh
                results = soup.select("ol[id='b_results']")[0] if len(soup.select("ol[id='b_results']")) > 0 else None 
                if results is None:
                    print ("###### DEBUG: Current Page RSO result is None...")
                    continue
            ## after trials
            if results is None:
                print ("###### DEBUG: Current Page RSO result is None after retrying times|%d" % retry_cnt)
                continue

            # div_results_list = results.findChildren("div" , recursive=False)
            div_results_list = results.findChildren("li" , recursive=False)
            valid_rank = start_page_id
            for div_result in div_results_list:
                if valid_rank >= max_results_topk:
                    print ("Already Fetching Enough Items Under current page...")
                    break
                data_json = process_bing_search_result_algo(div_result, valid_rank, fill_extinfo_enable, driver)
                if data_json is not None and len(data_json) > 0:
                    valid_rank += 1
                    ## fix new content_name to make it more reasonable
                    ## e.g. OpenAI AI Search Agent
                    content_name = data_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in data_json else ""
                    # data_json["content_name"] = content_name + " " + category_name
                    data_json[KEY_CONTENT_NAME] = content_name
                    data_json[KEY_FIELD] = "AI AGENT"
                    data_json[KEY_SUBFIELD] = category_name
                    data_json[KEY_CATEGORY] = category_name
                    data_json[KEY_CONTENT_TAG_LIST] = category_name + ",AI AGENT"
                    data_json[KEY_SOURCE] = DATA_SOURCE_BING
                    data_json[KEY_DT] = date
                    data_json[KEY_QUERY] = merge_query
                    # update Rank
                    cur_rank = data_json[metric] if metric in data_json else 0
                    cur_rank += rank_offset
                    data_json[metric] = cur_rank

                    ## 1 to multiple split item, 
                    ## item 1: fetched content_name
                    ## item 2: query (whitelist content name) -> fetched content name
                    
                    ## append new item, merge top 3 items
                    output_data_list.append(json.dumps(data_json))
                    output_data_list_json.append(data_json)

                    if valid_rank == 1:
                        """
                            e.g. query = OpenAI Deep Research
                            category = "AI Search Agent"
                            use top 1 item to copy one item and transform to original query, need to pass similarity check
                        """
                        data_json_transform = data_json
                        data_json_transform[KEY_CONTENT_NAME] = query
                        output_data_list.append(json.dumps(data_json_transform))
                        output_data_list_json.append(data_json_transform)

    except Exception as e:
        print ("DEBUG: get_fetch_whitelist_bing failed...")
        print (e)
    print ("DEBUG: get_fetch_whitelist_bing output_data_list return size|%d" % len(output_data_list))
    return output_data_list_json

def fetch_agent_from_bing_by_category(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs):
    """
        Only Fetch Agent From Bing By Category, Withough fill specific website
        
        category_whitelist_dict:  key: content_name, value: list of json objects
    """
    import requests
    from urllib.parse import quote
    from bs4 import BeautifulSoup

    if_search_en = True 
    fill_extinfo_enable = kwargs["fill_extinfo_enable"] if "fill_extinfo_enable" in kwargs else False

    output_data_list = []
    output_data_json_list = []

    url = ""

    start_page_id_list = [1, 11, 21, 31, 41, 51]
    item_per_page = 10

    ## Each Page Max Retry Cnt
    max_retry_cnt = 3

    for start_page_id in start_page_id_list:

        time.sleep(3)

        if if_search_en:
            # base_query_template_en = "https://www.bing.com/search?q=%s&form=QBLHCN&sp=-1&lq=0&sc=12-9&qs=n&sk=&cvid=AA2C705F2B504D6E825F3BD1CFABE444&ghsh=0&ghacc=0&ghpl="
            query_encode_en = get_search_keyword(query, "+")
            url = base_query_template_en % (query_encode_en) + base_query_template_en_param

            url_param = {}
            url_param["first"] = start_page_id
            url_param["FORM"] = "PERE"
            for key, value in url_param.items():
                url = url + "&" + "%s=%s" % (key, str(value))
        else:
            query_encode = quote(query)
            query_norm_encode = quote(query.lower())
            url = base_query_template_cn % (query_encode) + base_query_template_cn_param
            url_param = {}
            url_param["ensearch"] = 1
            for key, value in url_param.items():
                url = url + "&" + "%s=%s" % (key, str(value))

        print ("DEBUG: Start Query %s, Fetching URL Page ID %d, from Bing URL %s" % (query, start_page_id,url))

        custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
        headers = {
            'User-Agent': custom_user_agent,
            'Accept': '*/*'
        }
        html = ""

        results = None
        retry_cnt = 0

        while (results is None and retry_cnt < max_retry_cnt):
            time.sleep(RETRY_INTERVAL)

            retry_cnt += 1
            html = ""
            try:
                function_timeout_wrapper(driver, url)
                html = driver.page_source
                print ("DEBUG: Fetch URL Succeed|%s" % url)                                
            except FunctionTimedOut as e1:
                print ("DEBUG: Fetch URL Timeout|%s" % url)

            soup = BeautifulSoup(html, "html.parser")
            ## srp zh
            results = soup.select("ol[id='b_results']")[0] if len(soup.select("ol[id='b_results']")) > 0 else None 


        if results is not None:
            item_list = results.select('li')
            if item_list is not None:

                ## current page start, 1, 11, 21 item index
                valid_rank = start_page_id

                for i, item in enumerate(item_list):
                    # different card
                    item_cls_list = item["class"] if item.has_attr("class") else ""
                    if "b_algo" in item_cls_list:
                        ## algo result
                        ## image and url
                        valid_rank += 1
                        data_json = process_bing_search_result_algo(item, valid_rank, fill_extinfo_enable, driver)

                        if data_json is not None:
                            ## fill fields, query: category
                            data_json["field"] = "AI AGENT"
                            data_json["subfield"] = category_name
                            data_json["category"] = category_name
                            data_json["content_tag_list"] = category_name + ",AI AGENT"
                            data_json[KEY_SOURCE] = DATA_SOURCE_BING
                            data_json[KEY_DT] = date
                            data_json[KEY_QUERY] = query

                            # list of str
                            output_data_list.append(json.dumps(data_json))
                            # list of dict
                            output_data_json_list.append(data_json)
    print ("DEBUG: Processing output_data_list total size %d" % len(output_data_list))
    return output_data_json_list

def get_history_secondary_fetched_item(category_name, output_data_json_list, category_directory_dict):
    """
        output_data_json_list: fetched items
        category_directory_dict: history item
            key: category, value: list of items
    """
    try:
        fetched_content_name_list = [data_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in data_json else "" for data_json in output_data_json_list]
        fetched_content_name_list_clean = [normalize_content_name(content_name) for content_name in fetched_content_name_list]
        
        directory_listed_item = category_directory_dict[category_name] if category_name in category_directory_dict else []
        directory_listed_item_name_list_raw = [item_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in item_json else "" for item_json in directory_listed_item]
        ## remove duplicate
        directory_listed_item_name_list = list(set(directory_listed_item_name_list_raw))
        directory_listed_item_name_list_clean = [normalize_content_name(content_name) for content_name in directory_listed_item_name_list]

        ## not_included_item 
        skipped_item = []
        covered_item = []
        for item_name in directory_listed_item_name_list_clean:
            if item_name != "" and item_name not in fetched_content_name_list_clean:
                skipped_item.append(item_name)
            else:
                covered_item.append(item_name)
        print ("DEBUG: Category %s Total listed %d| Current Batch Fetched %d| Current Batch Covered %s| More Secondary Search Cnt %d" % (category_name, len(directory_listed_item), len(fetched_content_name_list_clean), len(covered_item), len(skipped_item)) )
        print ("DEBUG: directory_listed_item %s" % str(directory_listed_item))
        print ("DEBUG: fetched_content_name_list_clean %s" % str(fetched_content_name_list_clean))
        print ("DEBUG: skipped_item %s" % str(skipped_item))
        return skipped_item
    except Exception as e:
        print (e)
        return []

def fetch_agent_from_bing(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs):
    """ 
        query search

        category_directory_dict:
            k1: category, v1: list of already listed history items
        category_whitelist_dict:  key: content_name, value: list of json objects
        
        query = "AI AGENT Coding"
        query = "https://cn.bing.com/search?q=AI%20Agent%20Coding&qs=n&form=QBRE&sp=-1&lq=0&pq=ai%20agent%20coding&sc=5-15&sk=&cvid=E8CEAF7A88A04BEAB99DA4C9076B4B89&ghsh=0&ghacc=0&ghpl="

        optional fields
            "subfield", "category", "rank", "content_tag_list"
        
            get_fetch_from_bing_web   process main content
            get_fetch_whitelist_bing

        Fetch Plan

        1. Bing Page: 5 URLS, 50 items
        2. History Item: Up to 100 URLs
        3. Whitelist: 10 URLs, fill meta content

        Fill Ext Info
        1. get Image and Meta
    """
    ## data json
    output_data_json_list = []


    channels_str = kwargs[KEY_CHANNELS] if KEY_CHANNELS in kwargs else ""
    channels = []
    if channels_str == "":
        channels = [CHANNEL_BING_CATEGORY, CHANNEL_BING_WHITELIST, CHANNEL_BING_HISTORY_ITEM, CHANNEL_WHITELIST_META]
    else:
        channels = channels_str.split(",")
    # channels = [CHANNEL_WHITELIST_META]
    
    # step 1. fetch category name 
    if CHANNEL_BING_CATEGORY in channels:
        ## local file history, q search pattern: category
        output_data_json_category_list = fetch_agent_from_bing_by_category(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs)
        output_data_json_list.extend(output_data_json_category_list)
    
    if CHANNEL_BING_HISTORY_ITEM in channels:
        ## fetch history item from the web
        ## local file history, q search pattern: category + content name
        ## not_included_item 
        skipped_item = get_history_secondary_fetched_item(category_name, output_data_json_list, category_directory_dict)
        ## fetch  whitelist sources with meta images
        print ("DEBUG: fetch_agent_from_bing CHANNEL_BING_HISTORY_ITEM category_name %s append query list %s" % (category_name, str(",".join(skipped_item))))
        history_fetch_data_list = get_fetch_whitelist_bing(query, category_name, skipped_item, KEY_BING_RANK, BING_PAGE_RANK_BASE_OFFSET, date, driver, kwargs)
        if len(history_fetch_data_list) > 0:
            print ("DEBUG: fetch_agent_from_bing Append history_fetch_data_list Size %d" % len(history_fetch_data_list))
            # output_data_list.extend(whitelist_fetch_data_list)
            output_data_json_list.extend(history_fetch_data_list)

    # step 2. fetch category name + history item + append search query
    ## calculate historical directory, not exist in current list item
    if CHANNEL_BING_WHITELIST in channels:

        ## fetch from whitelist sources with meta images
        query_append_list = query_append_dict[category_name] if category_name in query_append_dict else []
        print ("DEBUG: fetch_agent_from_bing CHANNEL_BING_WHITELIST category_name %s append query list %s" % (category_name, str(",".join(query_append_list))))
        whitelist_fetch_data_list = get_fetch_whitelist_bing(query, category_name, query_append_list, KEY_BING_RANK, BING_PAGE_RANK_BASE_OFFSET, date, driver, kwargs)
        if len(whitelist_fetch_data_list) > 0:
            print ("DEBUG: fetch_agent_from_bing Append whitelist_fetch_data_list Size %d" % len(whitelist_fetch_data_list))
            # output_data_list.extend(whitelist_fetch_data_list)
            output_data_json_list.extend(whitelist_fetch_data_list)

    # step 3. 
    ## append whitelist, no rank data
    if CHANNEL_WHITELIST_META in channels:
        whitelist_content_list = category_whitelist_dict[category_name] if category_name in category_whitelist_dict else []
        for content_json in whitelist_content_list:
            output_data_json_list.append(content_json)

    ## output_data_list, same content_name, multiple search records, from multiple querys, save to average
    ## if fill_ext_info
    output_data_list = []
    fill_extinfo_enable = kwargs[FILL_EXTINFO_ENABLE] if FILL_EXTINFO_ENABLE in kwargs else False
    print ("DEBUG: fetch_agent_from_bing enable|" + str(fill_extinfo_enable))    
    if fill_extinfo_enable:
        output_data_json_list_filled = fill_ext_info_data(output_data_json_list, driver)
        for data_json in output_data_json_list_filled:
            output_data_list.append(json.dumps(data_json))
    else:
        for data_json in output_data_json_list:
            output_data_list.append(json.dumps(data_json))

    ## process to json string
    ## save 
    output_file_folder = os.path.dirname(output_file)
    if not os.path.exists(output_file_folder):
        os.mkdir(output_file_folder)
    save_file(output_file, output_data_list)

def fill_ext_info_data(input_data_json_list, driver):
    """
        Input Data Json List
    """
    output_list = []
    merged_key_list = [KEY_THUMBNAIL_PICTURE, KEY_UPLOAD_IMAGE_FILES, KEY_CONTENT]
    append_key_list = [KEY_HTML]
    # separator shows mutiple images KEY_THUMBNAIL_PICTURE KEY_UPLOAD_IMAGE_FILES seperator by commas
    separator = ","
    for input_data in input_data_json_list:
        try:
            ## keep updated input_data
            input_data_updated = input_data
            website = input_data[KEY_WEBSITE] if KEY_WEBSITE in input_data else ""
            updated_data = fetch_meta_image_from_url(driver, website)

            ## content/image use merge strategy
            for key in updated_data.keys():
                if key in merged_key_list:
                    value_list = []
                    updated_value = updated_data[key]
                    original_value = input_data[key] if key in input_data else ""
                    if updated_value != "":
                        value_list.append(updated_value)
                    if original_value != "":
                        value_list.append(original_value)
                    ## updated_data + input_data > input_data_updated
                    merge_value = separator.join(value_list)
                    input_data_updated[key] = merge_value
                elif key in append_key_list:
                    input_data_updated[key] = updated_data[key]
                else:
                    continue
            output_list.append(input_data_updated)
        except Exception as e:
            print ("DEBUG: Failed to Process %s" % str(input_data))
            print (e)
            output_list.append(input_data)
    return output_list

def get_merge_all_data_ai_agent():
    """
        Post Data AI Agent
        content_name,content_url,Image,Documentation,Discord,GitHub,content

        directory: kkv
            k1: category
            k2: content_name
            v2: list-value data serie duplicate
    """
    import requests
    data_file_folder = "./data/merge"
    data_file_list = []
    for sub_folder in os.listdir(data_file_folder):
        sub_folder_path = os.path.join(data_file_folder, sub_folder)
        if os.path.isdir(sub_folder_path):
            for file in os.listdir(sub_folder_path):
                data_file = os.path.join(sub_folder_path, file)
                if ".DS_Store" in data_file:
                    continue 
                if ".md" in data_file:
                    continue
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
    
    total_content_cnt = 0
    for category in directory.keys():
        data_map = directory[category]
        content_cnt = len(data_map)
        total_content_cnt += content_cnt

    print ("DEBUG: Total Rows Before Duplicate %d, category cnt %d, content_name cnt %d" % (total_kv_cnt, len(directory), total_content_cnt))
    return directory

def test_merge_all_data_ai_agent():
    ## key: cfategory, value: list of 
    data_map = get_merge_all_data_ai_agent()
    data_content_list_map = {}
    for category in data_map.keys():
        content_name_list = []
        ## key, list json
        content_dict = data_map[category]
        for key, item_json in content_dict.items():
            content_json = {}
            try:
                content_json = json.loads(item_json)
            except Exception as e:
                print (e)
            content_name = content_json["content_name"] if "content_name" in content_json else ""
            if content_name != "":
                content_name_list.append(content_name)
        content_name_list_clean = list(set(content_name_list))
        data_content_list_map[category] = content_name_list_clean
    total_cnt = 0
    for category in data_content_list_map.keys():
        name_list = data_content_list_map[category] 
        total_cnt += len(name_list)
    print ("DEBUG: data_map size %d, merge_all_data_ai_agent size %d" % (len(data_map), total_cnt))


def test_fetch_agent_from_bing():

    query = "AI Agent Coding"
    output_file = "./data/bing/ai_agent_coding.json"
    fetch_agent_from_bing(query, "", output_file)

def process_bing_search_result_algo(item, cur_page_rank, fill_extinfo_enable, driver):
    """
        only process search result,
        dont fetch exact url again
    """
    item_dict = {}
    try:
        ## algo result
        ## image and url
        content_name = ""
        content_meta = ""
        content = ""
        website = ""
        image_src = ""
        a_tilk = item.select('a[class="tilk"]')[0] if len(item.select('a[class="tilk"]')) > 0 else None
        if a_tilk is None:
            return item_dict
        # tpic tptxt
        image_src_list = []
        tpic = a_tilk.select('div[class="tpic"]')[0] if len(a_tilk.select('div[class="tpic"]')) > 0 else None
        if tpic is not None:
            image = tpic.select("img")[0] if len(tpic.select("img")) > 0 else None 
            if image is not None:
                image_alt = image["alt"] if image.has_attr("alt") else ""
                image_src = image["src"] if image.has_attr("src") else ""
                image_src_list.append(image_src)
        ## rms_iac
        div_rms = item.select('div[class="rms_iac"]')[0] if len(item.select('div[class="rms_iac"]')) > 0 else None 
        if div_rms is not None:
            image_src = div_rms["data-src"] if div_rms.has_attr("data-src") else ""
            image_alt = div_rms["data-alt"] if div_rms.has_attr("data-alt") else ""
            image_src_list.append(image_src)

        ## tptxt.tptt DEV Community
        content_name = item.select('div[class="tptt"]')[0].text if len(item.select('div[class="tptt"]')) > 0 else ""
        ## tpmeta: https://dev.to › webscraping › extract-goog…
        content_meta = item.select('div[class="tpmeta"]')[0].text if len(item.select('div[class="tpmeta"]')) > 0 else ""

        ## header
        div_title = item.select("h2")[0] if len(item.select("h2")) > 0 else None 
        if div_title is not None:
            website = div_title.a["href"]
            item_title =  div_title.a.text 

        ## main content 
        p_tag = item.select("p")[0] if len(item.select("p")) > 0 else None 
        if p_tag is not None:
            content = p_tag.text 

        ## url processing a.com
        item_dict[KEY_BING_CONTENT_NAME] = clean_content_name(content_name)
        item_dict[KEY_BING_CONTENT_META] = content_meta
        item_dict[KEY_BING_CONTENT] = content
        item_dict[KEY_BING_WEBSITE] = website
        item_dict[KEY_BING_RANK] = cur_page_rank
        return item_dict
    except Exception as e:
        print (e)
        traceback.print_exc()
        return item_dict

def crap_bing_search_result_demo():
    """
    """
    from urllib.parse import urlencode, urlunparse
    from urllib.request import urlopen, Request
    from bs4 import BeautifulSoup

    query = "programming"
    url = urlunparse(("https", "www.bing.com", "/search", "", urlencode({"q": query}), ""))
    custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    req = Request(url, headers={"User-Agent": custom_user_agent})
    page = urlopen(req)
    # Further code I've left unmodified
    soup = BeautifulSoup(page.read())
    links = soup.findAll("a")
    for link in links:
        print(link["href"])

def get_datetime():
    """
    """
    import datetime
    now = datetime.datetime.now()
    # today = datetime.date.today()
    # datetimestr = str(today.year) + str(today.month) + str(today.day)
    datetimestr = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)
    return datetimestr

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

def convert_category_to_keywords(category_name):
    category_name_norm = category_name
    if "agent" not in category_name.lower():
        category_name_norm = category_name + " " + "AI AGENT"
    return category_name_norm

def whitelist_row_mapper(site, category_name):
    """
        site is a dict
    """
    content_name = site["content_name"] if "content_name" in site else ""
    website = site["website"] if "website" in site else ""

    output_entity_dict = {}
    output_entity_dict.update(site)
    output_entity_dict["content_name"] = content_name
    output_entity_dict["website"] = website

    for key in ["content_meta", "thumbnail_picture", "content"]:
        if key not in output_entity_dict:
            output_entity_dict[key] = ""

    output_entity_dict["field"] = "AI AGENT"
    output_entity_dict["subfield"] = category_name
    output_entity_dict["category"] = category_name
    output_entity_dict["content_tag_list"] = category_name
    return output_entity_dict

def read_fetch_whitelist_path(fetch_whitelist_path):
    """
        output: dict
            k1: query, k2: append query list

        query: k1: category, k2: content_name, e.g. OpenAI DeepResearch

        category_whitelist_dict:
            key: str
            value: list of dict
    """
    lines = read_file(fetch_whitelist_path)
    
    search_query_append_dict = {}
    category_content_name_dict = {}

    output_data_list = []
    for line in lines:
        line_json = json.loads(line)
        category = line_json["category"] if "category" in line_json else ""
        sites = line_json["items"] if "items" in line_json else ""
        
        append_query_list = []
        for site in sites:
            content_name = site["content_name"] if "content_name" in site else ""
            merge_query = category + " " + content_name    
            append_query_list.append(merge_query)
            search_query_append_dict[category] = append_query_list

        content_whitelist = []
        content_set = set()
        for site in sites:
            # remove duplicate
            content_name = site["content_name"] if "content_name" in site else ""
            if content_name not in content_set:
                content_whitelist.append(whitelist_row_mapper(site, category))
                content_set.add(content_name)
            else:
                continue
        category_content_name_dict[category] = content_whitelist

    ## statistic
    category_cnt = len(category_content_name_dict.keys())
    category_content_name_cnt = 0
    for category in category_content_name_dict.keys():
        content_name_list = category_content_name_dict[category]
        category_content_name_cnt += len(content_name_list)
    print ("DEBUG: read_fetch_whitelist_path category cnt %d, no dup content list cnt %d" % (category_cnt, category_content_name_cnt))

    return search_query_append_dict, category_content_name_dict

def read_fetch_category_directory_list():
    """
        read all the content name data series in the directory
        output:
            k1: category,
            v1: list
    """
    directory = get_merge_all_data_ai_agent()
    category_list_dict = {}
    ## kv, k1: category_name, v1: list of [{"content_name":"", "website": ""}]
    for category in directory.keys():
        content_dict = directory[category]

        content_list = []
        for content_name in content_dict.keys():
            item_list = content_dict[content_name]
            # get first 
            if len(item_list) > 0:
                item_json = item_list[0]
                item_json_clean = {}

                item_json_clean["content_name"] = item_json["content_name"] if "content_name" in item_json else ""
                item_json_clean["website"] = item_json["website"] if "website" in item_json else ""
                content_list.append(item_json_clean)
        ## clean 
        category_list_dict[category] = content_list

    ## calculate
    total_list_cnt = 0
    for category in category_list_dict:
        content_list = category_list_dict[category]
        total_list_cnt += len(content_list)
    print ("DEBUG: read_fetch_category_directory_list total_list_cnt size %d" % total_list_cnt)
    print ("DEBUG: read_fetch_category_directory_list total_category_cnt size %d" % len(category_list_dict))
    return category_list_dict

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


def merge_query_append_dict(dict_a, dict_b):
    """
        dict_a: key str, value list of str
        dict_b: key str, value list of str
    """
    merge_keys = []
    merge_keys.extend(dict_a.keys())
    merge_keys.extend(dict_b.keys())

    merge_keys_list_clean = list(set(merge_keys))
    merge_dict = {}
    for key in merge_keys_list_clean:

        list_a = dict_a[key] if key in dict_a else []
        list_b = dict_b[key] if key in dict_b else []
        
        list_merge = []
        list_merge.extend(list_a)
        list_merge.extend(list_b)
        list_merge_nodup = list(set(list_merge))
        merge_dict[key] = list_merge_nodup
    return merge_dict


def merge_directory_dict_list(directory_dict_list):
    """
        directory_dict_list list of dict

        dict: key: category, value: list of data json
    """

    keyset = set()
    for directory_dict in directory_dict_list:
        keyset.update(directory_dict.keys())

    merge_dict = {}
    total_cnt = 0

    content_name_set = set()
    for key in keyset:
        merge_item_list = []
        for directory_dict in directory_dict_list:
            cur_item_list = directory_dict[key] if key in directory_dict else []
            merge_item_list.extend(cur_item_list)
            total_cnt += len(cur_item_list)

            for cur_item in cur_item_list:
                cur_content_name = cur_item[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in cur_item else ""
                content_name_set.add(cur_content_name)
        ## put 
        merge_dict[key] = merge_item_list

    ## duplicate content_name exist
    print ("DEBUG: merge_directory_dict_list total keys is %d, total_cnt is %d, nodup content cnt %d" % (len(merge_dict.keys()), total_cnt, len(content_name_set)))
    return merge_dict

def run_fetch_data(args, data_source):
    """
        # Todo, Agent Category -> Tags Keywords映射
    """

    # input args
    mode = args.mode
    date = args.date
    restart_from_category = args.restart_from_category
    fill_extinfo_enable_str = args.fill_extinfo_enable
    fill_extinfo_enable = True if fill_extinfo_enable_str == "true" else False
    channels = args.channels

    ## other params
    kwargs = {}
    kwargs[FILL_EXTINFO_ENABLE] = fill_extinfo_enable
    kwargs[KEY_CHANNELS] = channels

    mode = "all" if (mode == "" or mode is None) else mode
    date = get_date() if (date == "" or date is None) else date
    print ("DEBUG: run_fetch_data data_source|%s" % data_source)
    print ("DEBUG: run_fetch_data mode|%s" % mode)
    print ("DEBUG: run_fetch_data date|%s" % date)
    print ("DEBUG: fill_extinfo_enable| %s" % str(fill_extinfo_enable))

    input_file = "./data/agent_category_meta.json"
    # input_file = "./agent_category.txt"
    category_json_list, query_append_dict_category = read_category_meta(input_file)
    category_list = [category_json["category"] for category_json in category_json_list]

    ## k1: category, v1: list of query + name whitelist
    print ("### Loading Whitelist from Items in File")
    fetch_whitelist_path = "./data/agent_meta/fetch_missing_entity.json"
    query_append_dict_whitelist, category_whitelist_dict = read_fetch_whitelist_path(fetch_whitelist_path)
    
    print ("### Loading Whitelist from History Listed Items")
    history_listed_path = "./data/agent_meta/history_listed_items.json"
    history_append_dict_whitelist, category_history_dict = read_fetch_whitelist_path(history_listed_path)

    ## read category - history name list, key: category, value: list of json
    category_directory_dict_local = read_fetch_category_directory_list()
    ## Merge
    category_directory_dict = merge_directory_dict_list([category_history_dict, category_directory_dict_local])

    ## test_run_google
    query_append_dict = merge_query_append_dict(query_append_dict_category, query_append_dict_whitelist)
    print ("DEBUG: Processing query_append_dict size|%d" % len(query_append_dict))

    timeout = 60
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(timeout)
    driver.implicitly_wait(timeout);
    driver.set_script_timeout(timeout);
    # driver = None

    if data_source == DATA_SOURCE_GITHUB:

        data_file_folder = "./data/" + data_source + "/" + date
        if mode == "all" or mode == "fetch":
            ## Github Search Keywords different 
            if not os.path.exists(data_file_folder):
                os.mkdir(data_file_folder)
            for category_name in category_list:
                query = convert_category_to_keywords(category_name)
                print ("#### DEBUG: Github Processing Category %s" % category_name)
                output_file = data_file_folder + "/agent_github_%s.json" % get_query_normalize(category_name, "_")
                fetch_agent_from_github(category_name, output_file, driver, date)
        
        if mode == "all" or mode == "merge":
            ## Process Data
            output_merge_file = "./data/merge/" + date + "/" + "merge_github_data.json"
            process_github_data(data_file_folder, output_merge_file)

    elif data_source == DATA_SOURCE_BING:

        data_file_folder = "./data/" + data_source + "/" + date
        ## Bing Search Keywords different 
        if mode == "all" or mode == "fetch":
            if not os.path.exists(data_file_folder):
                os.mkdir(data_file_folder)

            # restart_from_category = ""
            category_list_final = category_list
            match_index = 0
            if restart_from_category != "":
                for i, category_name in enumerate(category_list):
                    if category_name == restart_from_category:
                        match_index = i 
                category_list_final = category_list[match_index:]
            else:
                category_list_final = category_list_final

            for category_name in category_list_final:
                query = convert_category_to_keywords(category_name)
                print ("#### DEBUG: Bing Processing Category %s" % category_name)
                output_folder = "./data/" + data_source + "/" + date       
                output_file = output_folder + "/agent_%s_%s.json" % (data_source, get_query_normalize(category_name, "_"))
                fetch_agent_from_bing(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs)
            
        if mode == "all" or mode == "merge":
            # merge_output_file_folder = "./data/merge/" + get_date()
            output_merge_file = "./data/merge/" + date + "/merge_bing_data.json"    
            if not os.path.exists(os.path.dirname(output_merge_file)): 
                os.mkdir("./data/merge/" + date)
            process_bing_data(data_file_folder, output_merge_file)

    elif data_source == DATA_SOURCE_GOOGLE:

        data_file_folder = "./data/" + data_source + "/" + date        
        ## Bing Search Keywords different 
        if mode == "all" or mode == "fetch":

            data_file_folder = "./data/" + data_source + "/" + date
            if not os.path.exists(data_file_folder):
                os.mkdir(data_file_folder)     

            fetch_from_google_verification(driver)

            # restart_from_category = ""
            category_list_final = category_list
            match_index = 0
            if restart_from_category != "":
                for i, category_name in enumerate(category_list):
                    if category_name == restart_from_category:
                        match_index = i 
                category_list_final = category_list[match_index:]
            else:
                category_list_final = category_list_final
            print ("DEBUG: Fetch Google Results from index %s, remaining list size %d" % (match_index, len(category_list_final)))

            for category_name in category_list_final:
                query = convert_category_to_keywords(category_name)
                print ("#### DEBUG: Bing Processing Category %s" % category_name)
                output_folder = "./data/" + data_source + "/" + date
                output_file = output_folder + "/agent_%s_%s.json" % (data_source, get_query_normalize(category_name, "_"))
                fetch_agent_from_google(query, category_name, output_file, driver, date, query_append_dict, category_directory_dict, category_whitelist_dict, kwargs)
        
        if mode == "all" or mode == "merge":  
            # merge_output_file_folder = "./data/merge/" + get_date()
            output_merge_file = "./data/merge/" + date + "/merge_google_data.json"    
            if not os.path.exists(os.path.dirname(output_merge_file)): 
                os.mkdir("./data/merge/" + date)
            process_google_data(data_file_folder, output_merge_file)

    elif data_source == DATA_SOURCE_ARXIV:

        data_file_folder = "./data/" + data_source + "/" + date
        if mode == "all" or mode == "merge":  
            if not os.path.exists(data_file_folder):
                os.mkdir(data_file_folder)        

            for category_name in category_list:
                query = convert_category_to_keywords(category_name)
                print ("#### DEBUG: Arxiv Processing Category %s" % category_name)
                output_file = data_file_folder + "/agent_arxiv_%s.json" % get_query_normalize(category_name, "_")
                fetch_agent_from_arxiv(category_name, output_file, driver, date)
           
        if mode == "all" or mode == "merge":  

            output_merge_file = "./data/merge/" + date + "/merge_arxiv_data.json"
            if not os.path.exists(os.path.dirname(output_merge_file)): 
                os.mkdir(os.path.dirname(output_merge_file))
            process_arxiv_data(data_file_folder, output_merge_file)

    else:
        print ("DEBUG: Input Data Source Not Supported %s" % data_source)

def row_mapper_github(item_json):
    """
    """
    output_json = {}  
    repo_name = item_json["repo_name"] if "repo_name" in item_json else ""
    user_name = item_json["user_name"] if "user_name" in item_json else ""
    content_name = repo_name + " " + user_name
    description = item_json["description"] if "description" in item_json else ""
    category = item_json["category"] if "category" in item_json else "AI AGENT"
    content_tag_list = "AI AGENT" + "," + category
    url = item_json["url"] if "url" in item_json else ""

    output_json["content_name"] = content_name
    output_json["publisher_id"] = get_sug_by_name(content_name)
    output_json["content"] = description
    output_json["field"] = "AI AGENT"
    output_json["subfield"] = category
    output_json["content_tag_list"] = content_tag_list
    output_json["website"] = url
    output_json[KEY_THUMBNAIL_PICTURE] = item_json[KEY_THUMBNAIL_PICTURE] if KEY_THUMBNAIL_PICTURE in item_json else ""
    output_json[KEY_UPLOAD_IMAGE_FILES] = item_json[KEY_UPLOAD_IMAGE_FILES] if KEY_UPLOAD_IMAGE_FILES in item_json else ""
    output_json[KEY_SOURCE] = DATA_SOURCE_GITHUB
    for key in item_json:
        if key not in output_json:
            output_json[key] = item_json[key]
    return output_json


def fill_readme_json(input_json, category):
    input_json_new = input_json
    if "field" not in input_json_new:
        input_json_new["field"] = "AI AGENT"
    if "subfield" not in input_json_new:
        input_json_new["subfield"] = category
    if KEY_THUMBNAIL_PICTURE not in input_json_new or input_json_new[KEY_THUMBNAIL_PICTURE] == "":
        # find first non-empty url
        website = row_mapper_website(input_json)
        image_dict = {}
        # p1
        if website != "":

            try:
                image_dict = fetch_website_icon_data_v2(website, driver)
            except FunctionTimedOut as e:
                print (e)
        ## github info
        if len(image_dict) == 0 and "github" in input_json_new and  input_json_new["github"] != "":
            image_dict = get_github_icon()
        ## fill arxiv
        if len(image_dict) == 0 and "content" in input_json_new and input_json_new["content"] != "" and "arxiv" in input_json_new["content"]:
            image_dict = get_arxiv_icon()
        input_json_new.update(image_dict)
    return input_json_new

def process_readme_data():

    data_file_list = [
        ("./data/markdown/final_agent_education.json", "EDUCATION")
        , ("./data/markdown/final_agent_employees.json", "AI EMPLOYEE")
        , ("./data/markdown/final_agent_finance.json", "FINANCE")
        , ("./data/markdown/final_agent_healthcare.json", "HEALTHCARE")
        , ("./data/markdown/final_agent_law.json", "LAW")
        , ("./data/markdown/final_ai_agent_benchmark.json", "BENCHMARK")
        , ("./data/markdown/final_awesome_ai_agents.json", "")
        , ("./data/markdown/final_gui_ai_agent.json", "GUI AGENT")
    ]

    data_list_merge = []
    data_list_merge_missing = []
    for data_file, category in data_file_list:
        lines = read_file(data_file)
        for i, line in enumerate(lines):
            input_json = fill_readme_json(json.loads(line), category)

            # print ("DEBUG: Input item_info_dict keys %s" % ",".join(list(input_json.keys())))
            output_json, if_missing = row_mapper_agent(input_json)
            # output_json = input_json
            if output_json is None:
                continue
            data_list_merge.append(json.dumps(output_json))
            if if_missing:
                data_list_merge_missing.append(json.dumps(output_json))
            time.sleep(5)
    output_file = "./data/markdown/merge_markdown_data.json"
    output_file_missing = "./data/markdown/merge_markdown_data_missing.json"

    save_file(output_file, data_list_merge)
    save_file(output_file_missing, data_list_merge_missing)
    return data_list_merge

def get_content_unique_id(output_json):
    content_name = output_json["content_name"] if "content_name" in output_json else ""
    field = output_json["field"] if "field" in output_json else ""
    unique_id = content_name + "_" + field
    return unique_id

def process_bing_data(data_file_folder, output_file):
    """ process bing data
        ## group by domain_data, -> <category, domain> joint keys
    """
    import os
    # data_path_folder_bing = "./data/bing/202529"
    data_file_list = []
    for filename in os.listdir(data_file_folder):
        data_file = os.path.join(data_file_folder, filename)
        data_file_list.append(data_file)
    # key: unique_id, value: list
    data_map = {}
    category_data_map = {}

    total_input_count = 0
    total_output_count = 0

    ## iterate over files
    for data_file in data_file_list:
        lines = read_file(data_file)
        total_input_count += len(lines)
        
        for i, line in enumerate(lines):
            input_json = json.loads(line)
            if filter_no_agent_json_bing(input_json):
                continue    
            # print ("DEBUG: Input item_info_dict keys %s" % ",".join(list(input_json.keys())))
            output_json, if_missing = row_mapper_agent(fill_bing_data_json(input_json))
            if output_json is None:
                continue
            
            ## group by unique id
            category = output_json["category"] if "category" in output_json else ""            
            # unique_id = output_json["domain"] if "domain" in output_json else ""
            unique_id = get_content_unique_id(output_json)


            ## add to kkv
            if unique_id != "":
                if unique_id in data_map:
                    item_json_list = data_map[unique_id]
                    item_json_list.append(output_json)
                    data_map[unique_id]  = item_json_list
                else:
                    data_map[unique_id] = [output_json]
                total_output_count += 1

            ## k1,v1, k1: unique_id, v1: list
            if unique_id in category_data_map:
                cur_list = category_data_map[unique_id]
                cur_list.append(output_json)
                category_data_map[unique_id] = cur_list
            else:
                category_data_map[unique_id] = [output_json]

    print ("DEBUG: Processing Bing Input Item Cnt %d, Output Pass Cnt %d" % (total_input_count, total_output_count))                
    print ("DEBUG: Processing Group By data_list size %d" % len(data_map))
    
    output_file_map = os.path.join(data_file_folder, "merge_bing_group_map_data.json")
    save_file(output_file_map, [json.dumps(data_map)])

    data_list_merge = []
    data_list_merge_missing = []
    data_list_merge_lite = []

    unique_id_set = set()
    for unique_id in category_data_map.keys():    
        ## same item under the unique keys
        item_json_list = category_data_map[unique_id]
        if len(item_json_list) == 0:
            continue
        # choose one of the best item, remove duplicate
        merge_item_json = get_best_item_json(item_json_list)
        if merge_item_json is None:
            continue

        ## key: content_tag_list, merge tags(search query)
        content_tag_list_list = [item_json["content_tag_list"] for item_json in item_json_list]
        unique_tags_set = set()
        for tags in content_tag_list_list:
            unique_tags_set.update(tags.split(","))
        content_tag_list_merge = ",".join(unique_tags_set)

        ## 默认获取第一个, 更新 merge的key
        merge_item_json["content_tag_list"] = content_tag_list_merge
            
        data_list_merge.append(json.dumps(merge_item_json))

        merge_item_json_lite = merge_item_json
        merge_item_json_lite["html"] = ""
        merge_item_json_lite["ext_info"] = ""
        data_list_merge_lite.append(json.dumps(merge_item_json_lite))
    # output_file = os.path.join(merge_output_file_folder, "/merge_bing_data.json")
    # output_file_missing = "./data/bing/merge_bing_data_missing.json"
    save_file(output_file, data_list_merge)
    output_file_lite_path = os.path.join(os.path.dirname(output_file), "merge_bing_data_lite.json")
    save_file(output_file_lite_path, data_list_merge_lite)
    # save_file(output_file_missing, data_list_merge_missing)
    return data_list_merge

def process_google_data(data_file_folder, output_file):
    """ process bing data
        unique_id: [content_name, field, subfield], 其实只有 content_name - sug,  
    """
    import os
    # data_path_folder_bing = "./data/bing/202529"
    data_file_list = []
    for filename in os.listdir(data_file_folder):
        data_file = os.path.join(data_file_folder, filename)
        data_file_list.append(data_file)
    data_map = {}
    category_data_map = {}
    total_input_count = 0
    total_output_count = 0
    for data_file in data_file_list:
        try:  
            lines = read_file(data_file)
            total_input_count += len(lines)
            for i, line in enumerate(lines):
                input_json = json.loads(line)
                if filter_no_agent_json_bing(input_json):
                    content_name = input_json["content_name"] if "content_name" in input_json else ""
                    print ("DEBUG: Input Json Skipped|%s" % content_name)
                    continue 
                # print ("DEBUG: Input item_info_dict keys %s" % ",".join(list(input_json.keys())))
                output_json, if_missing = row_mapper_agent(fill_google_data_json(input_json))
                if output_json is None:
                    continue
                ## group by unique id
                category = output_json["category"] if "category" in output_json else ""
                
                content_name = output_json["content_name"] if "content_name" in output_json else ""
                field = output_json["field"] if "field" in output_json else ""
                subfield = output_json["subfield"] if "subfield" in output_json else ""

                unique_id = content_name + "_" + field + "_" + subfield
                ## k1 map
                if unique_id != "":
                    if unique_id in data_map:
                        item_json_list = data_map[unique_id]
                        item_json_list.append(output_json)
                        data_map[unique_id]  = item_json_list
                    else:
                        data_map[unique_id] = [output_json]
                    total_output_count += 1
                ## joint key, k1: category, k2: unique_id
                ## joint key, k1: category, k2: unique_id
                if category in category_data_map:
                    cur_data_map = category_data_map[category]
                    if unique_id in cur_data_map:
                        cur_list = cur_data_map[unique_id]
                        cur_list.append(output_json)
                        cur_data_map[unique_id] = cur_list
                        category_data_map[category] = cur_data_map
                    else:
                        cur_data_map[unique_id] = [output_json]
                        category_data_map[category] = cur_data_map
                else:
                    cur_data_map = {}
                    cur_data_map[unique_id] = [output_json]
                    category_data_map[category] = cur_data_map

        except Exception as e:
            print ("DEBUG: Failed to process data_file %s" % data_file)
            print (e)

    print ("DEBUG: Processing Google Input Item Cnt %d, Output Pass Cnt %d" % (total_input_count, total_output_count))                
    print ("DEBUG: Processing Group By data_list size %d" % len(data_map))
    
    output_file_map = os.path.join(data_file_folder, "merge_google_group_map_data.json")
    save_file(output_file_map, [json.dumps(category_data_map)])

    data_list_merge = []
    ## without html
    data_list_merge_lite = []
    data_list_merge_missing = []

    for category in category_data_map.keys():
        data_map = category_data_map[category]
        for key in data_map.keys():
            item_json_list = data_map[key]
            if len(item_json_list) == 0:
                continue
            ## get top-0 of each domain
            merge_item_json = get_best_item_json(item_json_list)
            if merge_item_json is None:
                continue
            ## merge tags(search query)
            content_tag_list_list = [item_json["content_tag_list"] for item_json in item_json_list]
            unique_tags_set = set()
            for tags in content_tag_list_list:
                unique_tags_set.update(tags.split(","))

            content_tag_list_merge = ",".join(unique_tags_set)

            ## 默认获取第一个, 更新 merge的key
            merge_item_json["content_tag_list"] = content_tag_list_merge
            data_list_merge.append(json.dumps(merge_item_json))

            merge_item_json_lite = merge_item_json
            merge_item_json_lite["html"] = ""
            merge_item_json_lite["ext_info"] = ""
            data_list_merge_lite.append(json.dumps(merge_item_json_lite))

    save_file(output_file, data_list_merge)

    output_file_lite_path = os.path.join(os.path.dirname(output_file), "merge_google_data_lite.json")
    save_file(output_file_lite_path, data_list_merge_lite)
    # save_file(output_file_missing, data_list_merge_missing)
    return data_list_merge

def get_best_item_json(item_json_list):
    """
        domain same item, choose the ones with top content
    """
    item_list_meta_empty = []
    item_list_meta_full = []
    for item_json in item_json_list:
        category = item_json["category"] if "category" in item_json else ""
        content = item_json["content"] if "content" in item_json else ""
        if content == "":
            item_list_meta_empty.append(item_json)
        else:
            item_list_meta_full.append(item_json)

    item_list_sorted = []
    item_list_sorted.extend(item_list_meta_full)
    item_list_sorted.extend(item_list_meta_empty)

    item_json_top = item_list_sorted[0] if len(item_list_sorted) > 0 else None
    return item_json_top

def test_process_google_data():

    ## Bing Search Keywords different 
    data_file_folder = "./data/" + data_source + "/" + get_date()    
        # merge_output_file_folder = "./data/merge/" + get_date()
    output_merge_file = "./data/merge/" + get_date() + "/merge_google_data.json"    
    if not os.path.exists(os.path.dirname(output_merge_file)): 
        os.mkdir("./data/merge/" + get_date())
    process_google_data(data_file_folder, output_file)

def process_github_data(data_folder, output_file):
    """
        data_folder: /data/github/{date}
        output_folder:  output_folder = "./data/" + datetime_str
    """
    input_file = "./data/agent_category.txt"
    # input_file = "./agent_category.txt"
    category_list = read_file(input_file)
    category_list_clean = []
    for category_name in category_list:
        category_name_norm = category_name
        if "agent" not in category_name.lower():
            category_name_norm = category_name + " " + "agent"
        category_list_clean.append(category_name_norm)

    data_file_list = []
    for filename in os.listdir(data_folder):
        data_file = os.path.join(data_folder, filename)
        data_file_list.append(data_file)

    print ("DEBUG: Processing data_folder %s data_file_list List Size %d" % (data_folder, len(data_file_list)))
    
    output_lines = []
    min_repo_star = 10
    url_set = set()

    for data_file in data_file_list:
        ## merge过滤条件
        input_lines = read_file(data_file)

        ## process_category. e.g. agent_github_ai_docs_agent.json
        category_name_clean = os.path.basename(data_file)
        category_name_clean = category_name_clean.replace(".json", "")
        category_name_clean = category_name_clean.replace("agent_github_", "")
        category_tokens = category_name_clean.split("_")
        category_name = " ".join(category_tokens)

        lines_pass_filter = []
        for line in input_lines:
            ## replace uncommon char
            line_clean = line.replace("\u2026", "")
            # line_clean = line.encode('utf-8')
            if match_black_item(line_clean):
                print ("DEBUG: line_clean match black_item %s" % line_clean)
                continue

            item_json = json.loads(line_clean)
            url = item_json["url"]
            if url in url_set:
                continue
            else:
                url_set.add(url)

            ## 3. fill data_json
            # "tags": "marketing,design tool,social media", "category": "Workplace", "thumbnail_picture": "", "upload_image_files": ""
            item_json[KEY_CATEGORY] = category_name.upper()

            # item_json[KEY_TAGS] = category_name.upper()
            image_dict = get_github_icon()
            item_json.update(image_dict)
            ## output的 rowmapper
            item_output_json = row_mapper_github(item_json)

            ## 2.2k, 2
            repo_star = item_json["repo_star"] if "repo_star" in item_json else "0"
            repo_star_int = 0
            if "k" in repo_star:
                repo_star_int = int(float(repo_star.replace("k", "")) * 1000)
            else:
                repo_star_int = int(repo_star)

            ## e.g. "update": "Updated on Nov 21, 2024", "2024"/"2025 active" or "days" or "hours"
            update_time = item_json["update"] if "update" in item_json else ""

            if repo_star_int >= min_repo_star and ("2023" not in update_time and "2022" not in update_time and "2021" not in update_time and "2020" not in update_time and "2019" not in update_time):
                ## 确认添加

                lines_pass_filter.append(json.dumps(item_output_json))

        print ("DEBUG: %s Input Line size %d, pass size %d" % (category_name, len(input_lines), len(lines_pass_filter)))
        output_lines.extend(lines_pass_filter)
    print ("DEBUG: Output Lines Size %d" % len(output_lines))
    
    # datetime_str = get_date()
    # output_folder = "./data/" + datetime_str
    save_file(output_file, output_lines)

def fetch_ai_agent_data(data_file_folder, output_file):
    """ process arxiv data
        how to add citation data
    """
    import os
    data_file_list = []
    for filename in os.listdir(data_file_folder):
        data_file = os.path.join(data_file_folder, filename)
        data_file_list.append(data_file)
    data_map = {}
    total_input_count = 0
    total_output_count = 0
    for data_file in data_file_list:
        lines = read_file(data_file)
        total_input_count += len(lines)
        for i, line in enumerate(lines):
            input_json = json.loads(line)
            if filter_no_agent_json_bing(input_json):
                continue    
            # print ("DEBUG: Input item_info_dict keys %s" % ",".join(list(input_json.keys())))
            output_json, if_missing = row_mapper_agent(fill_bing_data_json(input_json))
            if output_json is None:
                continue
            ## group by unique id
            unique_id = output_json["domain"] if "domain" in output_json else ""
            if unique_id != "":
                if unique_id in data_map:
                    item_json_list = data_map[unique_id]
                    item_json_list.append(output_json)
                    data_map[unique_id]  = item_json_list
                else:
                    data_map[unique_id] = [output_json]
                total_output_count += 1
    print ("DEBUG: Processing Bing Input Item Cnt %d, Output Pass Cnt %d" % (total_input_count, total_output_count))                
    print ("DEBUG: Processing Group By data_list size %d" % len(data_map))
    
    output_file_map = os.path.join(data_file_folder, "merge_bing_group_map_data.json")
    save_file(output_file_map, [json.dumps(data_map)])

    data_list_merge = []
    data_list_merge_missing = []
    for key in data_map.keys():
        item_json_list = data_map[key]
        if len(item_json_list) == 0:
            continue
        merge_item_json = item_json_list[0]

        ## merge tags(search query)
        content_tag_list_list = [item_json["content_tag_list"] for item_json in item_json_list]
        unique_tags_set = set()
        for tags in content_tag_list_list:
            unique_tags_set.update(tags.split(","))

        content_tag_list_merge = ",".join(unique_tags_set)
        merge_item_json["content_tag_list"] = content_tag_list_merge
        data_list_merge.append(json.dumps(merge_item_json))

    # output_file = os.path.join(merge_output_file_folder, "/merge_bing_data.json")
    # output_file_missing = "./data/bing/merge_bing_data_missing.json"
    save_file(output_file, data_list_merge)
    # save_file(output_file_missing, data_list_merge_missing)
    return data_list_merge


def process_arxiv_data(data_file_folder, output_file):
    """ process_arxiv_data
    """
    import os
    # data_path_folder_bing = "./data/bing/202529"
    data_file_list = []
    for filename in os.listdir(data_file_folder):
        data_file = os.path.join(data_file_folder, filename)
        data_file_list.append(data_file)
    # data_file_list = [
    #     ("./data/bing/final_agent_education.json", "")
    # ]
    # key: unique_id, value: list
    data_map = {}
    total_input_count = 0
    total_output_count = 0
    for data_file in data_file_list:
        lines = read_file(data_file)
        total_input_count += len(lines)
        for i, line in enumerate(lines):
            input_json = json.loads(line)
            if filter_no_agent_json_bing(input_json):
                continue    
            # print ("DEBUG: Input item_info_dict keys %s" % ",".join(list(input_json.keys())))
            output_json, if_missing = row_mapper_agent(fill_bing_data_json(input_json))
            if output_json is None:
                continue
            ## group by unique id
            unique_id = output_json["domain"] if "domain" in output_json else ""
            if unique_id != "":
                if unique_id in data_map:
                    item_json_list = data_map[unique_id]
                    item_json_list.append(output_json)
                    data_map[unique_id]  = item_json_list
                else:
                    data_map[unique_id] = [output_json]
                total_output_count += 1
    print ("DEBUG: Processing Bing Input Item Cnt %d, Output Pass Cnt %d" % (total_input_count, total_output_count))                
    print ("DEBUG: Processing Group By data_list size %d" % len(data_map))
    
    output_file_map = os.path.join(data_file_folder, "merge_bing_group_map_data.json")
    save_file(output_file_map, [json.dumps(data_map)])

    data_list_merge = []
    data_list_merge_missing = []
    for key in data_map.keys():
        item_json_list = data_map[key]
        if len(item_json_list) == 0:
            continue
        merge_item_json = item_json_list[0]

        ## merge tags(search query)
        content_tag_list_list = [item_json["content_tag_list"] for item_json in item_json_list]
        unique_tags_set = set()
        for tags in content_tag_list_list:
            unique_tags_set.update(tags.split(","))

        content_tag_list_merge = ",".join(unique_tags_set)

        ## 默认获取第一个, 更新 merge的key
        merge_item_json["content_tag_list"] = content_tag_list_merge
        data_list_merge.append(json.dumps(merge_item_json))

    # output_file = os.path.join(merge_output_file_folder, "/merge_bing_data.json")
    # output_file_missing = "./data/bing/merge_bing_data_missing.json"
    save_file(output_file, data_list_merge)
    # save_file(output_file_missing, data_list_merge_missing)
    return data_list_merge

def merge_fetch_data():

    # process_readme_data()

    # process_github_data()

    process_bing_data()


def fetch_agent_github_detail(url, date):
    """
        fetch ai agent from github project
        
        url: https://github.com/search?q=education%20ai%20agent&type=repositories
        page2: 
        
        https://github.com/search?q=education+ai+agent&type=repositories&p=2

        data-testid="results-list"

        update_format: "2025-01-15T11:10:34Z"
    """
    output_json_list = []
    pagination_url_list = []
    max_page_number = 0

    page_number_list = []
    pagination_url_list = []

    timeout = 20

    try:
        import requests
        from bs4 import BeautifulSoup
        headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
        
        req = requests.get(url, headers = headers, timeout=REQUESTS_TIMEOUT)
        soup = BeautifulSoup(req.text, "html.parser")
        # get_nevigation
        navigation = soup.select('nav[aria-label="Pagination"]')[0] if len(soup.select('nav[aria-label="Pagination"]')) > 0 else None
        if navigation is not None:
            page_tag_list = navigation.select('a')

            for tag_a in page_tag_list:
                if tag_a is None:
                    continue
                href = tag_a["href"] if tag_a.has_attr("href") else ""
                page_text = tag_a.text
                if page_text == "Previous" or page_text == "Next":
                    continue
                if href != "":
                    pagination_url_list.append((page_text, href))
                
                cur_page_number = 0
                try:
                    cur_page_number = int(page_text)
                except Exception as e:
                    print ("DEBUG: Failed to process page number %s" % page_text)
                    print (e)
                if page_text != "" and isinstance(cur_page_number, int):
                    page_number_list.append(cur_page_number)
        max_page_number = max(page_number_list)

        ## Get Page Result
        results_list = soup.select('div[data-testid="results-list"]')[0]

        # h3, div, ul
        base_url = "https://github.com"

        for i, result in enumerate(results_list.children):
            # print ("DEBUG: Processing Result i %d" % i)
            data_json = {}
            user_name,repo_name, repo_url, description, repo_type, repo_star, repo_update   = "", "", "", "", "", "", ""

            # print (result)
            for div in result.children:
                #print (div)
                div_detail = div.find_all("div")[0]
                # print (div_detail)
                # div_detail = div2.find_all("div")[1]
                # print (div_detail)           
                # for div2 in div.find_all("div")[0]: 
                for element in div_detail.children:
                        # print (element.name)
                        if element.name == "h3":
                            # div title
                            div_title = element.find_all("div")[0].find_all("div")[1] if (len(element.find_all("div")) > 0) and (len(element.find_all("div")[0].find_all("div")) > 1) else ""
                            elem_a = div_title.find_all("a")[0]
                            # elem_a = elem_title.select("a")[0]
                            elem_href = elem_a["href"]
                            elem_span = elem_a.select("span")[0]
                            repo = elem_span.text
                            # e.g. aws-samples/AI-Agents-for-Education
                            items = repo.split("/")
                            # print (repo)                        
                            username = ""
                            reponame = ""
                            if len(items) == 2:
                                user_name = items[0]
                                repo_name = items[1]

                            repo_url = base_url + elem_href
                        elif element.name == "div":
                            div_span_list = element.find_all("span")
                            if len(div_span_list) > 0:
                                description = div_span_list[0].text
                        elif element.name == "ul":
                            # ul - li -> (type, star, update)
                            div_li_list = element.find_all("li")
                            if len(div_li_list) == 3:
                                # type, star, update
                                div_type = div_li_list[0]
                                div_star = div_li_list[1]
                                div_update = div_li_list[2]
                                repo_type = div_type.text 
                                repo_star = div_star.select("a")[0].select("span")[0].text if len(div_star.select("a")) >= 1 and (len(div_star.select("a")[0].select("span")) >= 1) else ""
                                repo_update = div_update.select("span")[0].text if len(div_update.select("span")) >= 1 else ""
                            elif len(div_li_list) == 2:
                                # ul - li -> (star, update)                            
                                # star, update
                                div_star = div_li_list[0]
                                div_update = div_li_list[1]
                                repo_type = ""
                                repo_star = div_star.select("a")[0].select("span")[0].text if len(div_star.select("a")) >= 1 and (len(div_star.select("a")[0].select("span")) >= 1) else ""
                                repo_update = div_update.select("span")[0].text if len(div_update.select("span")) >= 1 else ""
                        else:
                            print (element.name)

            data_json["user_name"] = user_name
            data_json["repo_name"] = repo_name
            data_json["url"] = repo_url
            data_json["description"] = description
            data_json["description"] = description
            data_json["repo_type"] = repo_type
            data_json["repo_star"] = repo_star
            data_json["update"] = repo_update
            data_json[KEY_SOURCE] = DATA_SOURCE_GITHUB
            data_json[KEY_DT] = date

            # website 获取展现缩略图
            website = repo_url
            image_dict = fetch_website_icon_data(website)
            data_json.update(image_dict)
            output_json_list.append(json.dumps(data_json))
    
    except Exception as e:
        traceback.print_exc()
        print (e)

    return output_json_list, pagination_url_list, max_page_number

def get_github_repo_detail_url(url):
    """
        fetch_github_url_data: https://github.com/AI-Agent-Hub/AI-Agent-Marketplace

        url = "https://github.com/AI-Agent-Hub/AI-Agent-Marketplace"
        
        # Todo 

        # field

        about
        website
    """
    timeout = 20
    try:
        import requests
        from bs4 import BeautifulSoup
        headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
        req = requests.get(url, headers = headers, timeout = REQUESTS_TIMEOUT)
        soup = BeautifulSoup(req.text, "html.parser")

    except Exception as e:
        raise
    else:
        pass
    finally:
        pass

def test_merge_github_data():

    data_file_folder = "./data/github/20250201/"
    if not os.path.exists(data_file_folder):
        os.mkdir(data_file_folder)
    
    ## Process Data
    output_merge_file = "./data/merge/20250201/merge_github_data.json"
    if not os.path.exists(os.path.dirname(output_merge_file)):
        os.mkdir(os.path.dirname(output_merge_file))

    process_github_data(data_file_folder, output_merge_file)

def test():
    test_process_google_data()

def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_source', type=str, help='Data Source ')
    parser.add_argument('--mode', type=str, default="all", help='Mode for Fetching such as fetch,merge,all ')
    parser.add_argument('--date', type=str, default="", help='date for the arguments')
    parser.add_argument('--restart_from_category', type=str, default="", help='restart from category')
    parser.add_argument('--fill_extinfo_enable', type=str, default="false", help='fill_extinfo_enable')
    parser.add_argument('--channels', type=str, default="", help='channelling for fetching')

    args = parser.parse_args()
    data_source = args.data_source
    print ("DEBUG: Input Data Source %s" % args.data_source)
    print ("DEBUG: Input mode %s" % args.mode)
    print ("DEBUG: Input date %s" % args.date)
    print ("DEBUG: restart_from_category %s" % args.restart_from_category)

    if data_source == "test":
        test()
    else:
        run_fetch_data(args, args.data_source)

if __name__ == '__main__':
    main()
