# -*- coding: utf-8 -*-

import codecs
import re
import json
from bs4 import BeautifulSoup
import requests
import time
import json
import codecs
import time
import os, sys
import numpy as np
import random
import traceback

from constants import *

def read_file(file_path):
    lines = []
    with codecs.open(file_path, "r", "utf-8") as file:
        lines = file.readlines()
    return lines

def save_file(file_path, lines):
    with codecs.open(file_path, "w", "utf-8") as file:
        for line in lines:
            file.write(line + "\n")
    file.close()

def read_data(data_file):
    file = codecs.open(data_file, "r", "utf-8")
    l = []
    for line in file:
        line = line.replace("\n", "")
        l.append(line)
    return l

def save_data(data_file, l):
    file = codecs.open(data_file, "w", "utf-8")
    for line in l:
        file.write(line + "\n")
    file.close()

def parse_star_float(github_star_str):
    if github_star_str == "":
        return 0.0
    if isinstance(github_star_str, float):
        return github_star_str
    if isinstance(github_star_str, int):
        return float(github_star_str)
    try:
        if "k" in github_star_str:
            github_star_int = github_star_str.replace("k", "")
            value = 1000.0 * float(github_star_int)
            return value
        else:
            value = float(github_star_str)
            return value
    except Exception as e:
        print (e)
        traceback.print_exc()
        return 0.0

def parse_float(float_str):
    """
        support 10.0,  3.2k e.g.
    """
    if float_str == "":
        return 0.0
    if isinstance(float_str, float):
        return float_str
    if isinstance(float_str, int):
        return float(float_str)
    try:
        if "k" in float_str:
            float_str = float_str.replace("k", "")
            float_str = float_str.strip()
            value = 1000.0 * float(float_str)
            return value
        else:
            value = float(float_str)
            return value
    except Exception as e:
        print (e)
        traceback.print_exc()
        return 0.0

def get_date():
    """
    """
    import datetime
    now = datetime.datetime.now()
    # today = datetime.date.today()
    # datetimestr = str(today.year) + str(today.month) + str(today.day)
    datetimestr = str(now.year) + str(now.month) + str(now.day)
    return datetimestr

def get_sug_by_name(content_name):
    """
        seperator: " ", "."
    """
    import re
    content_name_lower = content_name.lower()
    content_name_lower_seg = re.split(r'[ .]+', content_name_lower)

    content_name_sug = "-".join(content_name_lower_seg)
    return content_name_sug

def post_data_statistic_fill_all_data():
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
        content_id
    """
    import requests
    url = "http://www.deepnlp.org/addEntityStatistic"
    user_id = "AI Hub Admin"
    access_key = ""
    data_file_list = [
        # ("./data/merge/%s/merge_github_data.json" % date_str, "GitHub Star"),
        "./data/merge/statistic/merge_ai_agent_statistic.json"
    ]
    
    post_data_list = []
    for data_file in data_file_list:
        lines = read_file(data_file)
        for i, line in enumerate(lines):
            input_data = json.loads(line)
            ## category
            category = input_data["category"] if "category" in input_data else ""
            data_dict = input_data["data"] if "data" in input_data else ""

            for content_name in data_dict.keys():
                data_json = data_dict[content_name]
                publisher_id = get_sug_by_name(content_name)

                for metric in data_json.keys():
                    values_list = data_json[metric]
                    for (dt, value) in values_list:

                        ds_json = {}
                        ds_json["entity_id"] = ""
                        ds_json["entity_type"] = "ai_service"
                        ds_json["dt"] = str(dt)
                        ds_json["metric"] = metric
                        ds_json["value"] = value
                        ds_json["publisher_id"] = publisher_id
                        ds_json["content_name"] = content_name

                        ds_json["user_id"] = user_id
                        ds_json["access_key"] = access_key
                        
                        post_data_list.append(ds_json)
    print ("DEBUG: post_data_list Total Size %d" % len(post_data_list))

    for ds_json in post_data_list:
        try:
            print ("DEBUG: Request Output Json %s" % str(ds_json))            
            # existing url update:
            res = requests.post(url=url,data=ds_json)                
            status_code = res.status_code
            print ("DEBUG: Line %d, status %s" % (i, status_code))
        except Exception as e:
            print (e)
            traceback.print_exc()
        time.sleep(1)

def post_data_statistic(args):
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
        content_id
    """
    import requests
    url = "http://www.deepnlp.org/addEntityStatistic"
    user_id = "AI Hub Admin"
    access_key = ""
    date_str = get_date()
    data_file = args.data_file
    data_file_list = [(data_file)]

    for data_file in data_file_list:
        lines = read_file(data_file)
        for i, line in enumerate(lines):
            output_json = json.loads(line)

            content_name = output_json["content_name"] if "content_name" in output_json else ""
            publisher_id = output_json["publisher_id"] if "publisher_id" in output_json else ""
            if publisher_id == "":
                publisher_id = get_sug_by_name(content_name)
            dt = output_json["dt"] if "dt" in output_json else date_str
            ## source区分metric
            source = output_json[KEY_SOURCE] if KEY_SOURCE in output_json else ""
            metric = ""
            if source == DATA_SOURCE_BING:
                metric = METRIC_BING_RANK
            elif source == DATA_SOURCE_GOOGLE:
                metric = METRIC_GOOGLE_RANK
            elif source == DATA_SOURCE_GITHUB:
                metric = METRIC_GITHUB_STAR
            elif source == DATA_SOURCE_ARXIV:
                metric = METRIC_ARXIV_REFERENCE
            else:
                metric = ""

            value = 0.0
            if metric == METRIC_GITHUB_STAR:
                value = parse_float(output_json[KEY_REPO_STAR]) if KEY_REPO_STAR in output_json else 0.0
            elif (metric == METRIC_BING_RANK or metric == METRIC_GOOGLE_RANK):
                # value_str = output_json[metric] if metric in output_json else ""
                value_str = output_json[KEY_RANK] if KEY_RANK in output_json else ""
                value = parse_float(value_str)
            else:
                print ("DEBUG: value not supported...")
                continue

            ds_json = {}
            ds_json["entity_id"] = ""
            ds_json["entity_type"] = "ai_service"
            ds_json["dt"] = dt
            ds_json["metric"] = metric
            ds_json["value"] = value
            ds_json["publisher_id"] = publisher_id
            ds_json["content_name"] = content_name
            if ds_json is None:
                continue
            ds_json["user_id"] = user_id
            ds_json["access_key"] = access_key
            try:
                print ("DEBUG: Request Output Json %s" % str(ds_json))            
                # existing url update:
                res = requests.post(url=url,data=ds_json, timeout=10)               
                status_code = res.status_code
                print ("DEBUG: Line %d, status %s" % (i, status_code))
            except Exception as e:
                print (e)
                traceback.print_exc()
            time.sleep(2)
            
def main():
    """
        python3 post_ai_statistic.py --data_file "./data/merge/maintext/merge_ai_agent_meta_coding_agent.json" --metric "Bing Rank"
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, default="", help='Input Data File of list of Json ')
    # parser.add_argument('--metric', type=str, default="", help='metric')
    args = parser.parse_args()

    post_data_statistic(args)
    # post_data_statistic_fill_all_data()

if __name__ == '__main__':
    main()
