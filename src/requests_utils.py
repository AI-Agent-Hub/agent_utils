# -*- coding: utf-8 -*-

import codecs
import re
import json
import os
import random
import traceback
import requests

from bs4 import BeautifulSoup
from func_timeout import func_set_timeout, FunctionTimedOut
import ai_agent_marketplace

from constants import *
from data_utils import *

def is_image_url(url):
    """
    """
    if_contain_image_url = False
    for postfix in ["png", "jpg", "jpeg", "webp", "gif", "ico"]:
        if postfix in url:
            if_contain_image_url = True 
    return if_contain_image_url

def is_github_url(url):
    """
    """
    if_github_url = False
    if "github" in url:
        if_github_url = True
    return if_github_url

def append_url(base_url, uri):
    """
    """
    final_uri = ""
    schema = "https://"
    try:
        if "http" in uri:
            final_uri = uri
        else:
            base_url_clean = schema + get_domain(base_url)
            # get base domain
            final_uri = base_url_clean + uri
    except Exception as e:
        print ("DEBUG: Appending URL Failed %s, %s" % (base_url, uri))
        print (e)
    return final_uri

def test_normalize_url():
    url = "https://www.gocodeo.com/"
    normalize_url = normalize_url(url)
    print (normalize_url)


def merge_bing_image_icon_src(image_src_list):
    """
        bing default
    """
    image_src_own_domain = []
    image_src_bing = []
    for image_src in image_src_list:
        if "bing.com" in image_src:
            image_src_bing.append(image_src)
        else:
            image_src_own_domain.append(image_src)
    image_src_merge = []
    image_src_merge.extend(image_src_own_domain)
    image_src_merge.extend(image_src_bing)

    final_image_src = image_src_merge[0] if len(image_src_merge) > 0 else ""
    return final_image_src

@func_set_timeout(FETCH_TIMEOUT)
def function_timeout_wrapper(driver, url):
    try:
        driver.get(url)
    except Exception as e:
        print (e)
        driver.execute_script("window.stop()")               
    return

@func_set_timeout(FETCH_TIMEOUT)
def fetch_website_html(url, driver):
    """
        e.g. url = "https://www.workday.com"
    """
    if driver is None:
        return {}
    html = ""
    try:
        headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}        
        head = None
        body = None
        try:
            function_timeout_wrapper(driver, url)
            html = driver.page_source
            print ("DEBUG: Fetch URL Succeed|%s " % url)            
        except FunctionTimedOut as e1:
            print ("DEBUG: Fetch URL Timeout|%s" % url)
        return html
    except Exception as e:
        traceback.print_exc()
        print (e)
    return html

def clean_main_text(paragraph):
    paragraph_clean = paragraph.replace("\n", "").strip()
    return paragraph_clean

def process_main_page_content(html):
    """
        input: html str
    """
    main_text = ""
    item_info_dict = {}
    if html == "":
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        head = soup.select("head")[0] if len(soup.select("head")) > 0 else None
        body = soup.select("body")[0] if len(soup.select("body")) > 0 else None
        if body is None:
            return ""
        main_text_paragraph = []
        span_list = body.select("span")
        p_list = body.select("p")
        if span_list is not None:
            for span in span_list:
                span_text = span.text
                main_text_paragraph.append(span_text)
        if p_list is not None:
            for p in p_list:
                p_text = p.text
                main_text_paragraph.append(p_text)
        main_text = " ".join([clean_main_text(paragraph) for paragraph in main_text_paragraph])        
        
        item_info_dict[KEY_MAIN_TEXT] = main_text
    except Exception as e:
        print ("DEBUG: process_main_page_content failed...")
        print (e)
    return item_info_dict

def fetch_meta_image_from_url(driver, website):
    """
    """
    updated_data = {}
    updated_data[KEY_WEBSITE] = website
    try:
        html = ""
        try:
            html = fetch_website_html(website, driver)
        except FunctionTimedOut as e:
            print (e)
        if html == "":
            print ("DEBUG: Failed to fill_ext_info_data fetch html from website %s" % website)
            return updated_data
        ## check if image is default 
        image_src_list = []
        image_data_dict = fetch_website_icon_data_from_html(website, html)
        if image_data_dict is not None and len(image_data_dict) > 0:
            image_src = image_data_dict[KEY_THUMBNAIL_PICTURE] if KEY_THUMBNAIL_PICTURE in image_data_dict else ""
            image_src_list.append(image_src)
            print ("DEBUG: process_bing_search_result_algo fetch_website_icon_data_v2 ReFetch Image URL %s From website %s" % (image_src, website))
        ## Merge Image Src
        final_image_src = merge_bing_image_icon_src(image_src_list)
        ## fill maintext
        main_text_dict = process_main_page_content(html)
        main_text = main_text_dict[KEY_MAIN_TEXT] if KEY_MAIN_TEXT in main_text_dict else ""

        updated_data[KEY_THUMBNAIL_PICTURE] = final_image_src
        updated_data[KEY_UPLOAD_IMAGE_FILES] = image_data_dict[KEY_UPLOAD_IMAGE_FILES] if KEY_UPLOAD_IMAGE_FILES in image_data_dict else ""
        updated_data[KEY_CONTENT] = main_text
        updated_data[KEY_HTML] = html
        return updated_data
    except Exception as e:
        print (e)
        return updated_data

def fetch_website_icon_data_from_html(url, html):
    """ read website image icon data
        <link rel="icon" type="image/vnd.microsoft.icon" href="http://example.com/image.ico"> 
        <link rel="shortcut icon" href="http://sstatic.net/so/favicon.ico">
        <link rel="apple-itouch-icon" href="http://sstatic.net/so/apple-touch-icon.png">
        <link rel="" href="http://www.google.com/favicon.ico" type="image/x-icon"/>
        url = "https://superagi.com/"

        image_dict = fetch_website_icon_data_v2(url)
        e.g. https://www.workday.com/content/dam/web/zz/images/logos/workday/workday-logo.svg

    """
    ## 1.0 
    # import requests
    # from bs4 import BeautifulSoup
    # from selenium import webdriver

    thumbnail_image_url = ""
    icon_url_list = []
    image_id_list = []
    image_dict = {}

    ## append default icon of the website url
    default_icon_url = get_http_prefix_domain(url) + "/favicon.ico"
    icon_url_list.append(default_icon_url)

    try:
        soup = BeautifulSoup(html, "html.parser")
        head = soup.select("head")[0] if len(soup.select("head")) > 0 else None

        # req = requests.get(url, headers=headers, timeout=10)
        # soup = BeautifulSoup(req.text, "html.parser")
        # head = soup.select("head")[0] if len(soup.select("head")) > 0 else None
        if head is not None:
            links = head.select("link")
            if links is not None:
                for i, link in enumerate(links):
                    if link is None:
                        continue
                    # link
                    rel = link["rel"] if link.has_attr("rel") else None
                    link_type = link["type"] if link.has_attr("type") else None
                    href = link["href"] if link.has_attr("href") else None
                    # print ("DEBUG: Link %d link %s" % (i, str(link)))
                    ## rel
                    if rel is not None and "shortcut" in rel or "icon" in rel or link_type == "image/x-icon":
                        if href is not None:
                            full_href = append_url(url, href)
                            icon_url_list.append(full_href)
                    ## normal link
                    if href is not None and is_image_url(href):
                        full_href = append_url(url, href)
                        if full_href != thumbnail_image_url:
                            image_id_list.append(full_href)
            ## other image
            images = head.select("img")
            if images != None:
                for image in images:
                    image_src = image["src"] if "src" in image.attrs else ""
                    if image_src != "":
                        image_id_list.append(image_src)
            ## meta <meta>
            meta_list = head.select("meta")
            if meta_list != None:
                for meta_tag in meta_list:
                    meta_content = meta_tag["content"] if "content" in meta_tag.attrs else ""
                    meta_property = meta_tag["property"] if "property" in meta_tag.attrs else ""
                    if is_image_url(meta_content):
                        image_id_list.append(meta_content)

    except Exception as e:
        traceback.print_exc()
        print (e)
    ## find the largest
    try:
        thumbnail_image_url = get_largest_icon_file(icon_url_list)
    except FunctionTimedOut as e:
        print (e)
    ## add information
    image_dict[KEY_THUMBNAIL_PICTURE] = thumbnail_image_url
    image_dict[KEY_UPLOAD_IMAGE_FILES] = ",".join(image_id_list)
    return image_dict

def get_http_prefix_domain(url):
    """
        args: 
            url: http://www.workday.com/abcd
        return:
            http://www.workday.com
    """
    full_url = ""
    if "https://" in url:
        full_url = "https://" + get_domain(url)
    elif "http://" in url:
        full_url = "http://" + get_domain(url)
    else:
        full_url = "https://" + get_domain(url)
    return full_url


@func_set_timeout(REQUESTS_TIMEOUT)
def fetch_website_icon_data(url):
    """ read website image icon data
        <link rel="icon" type="image/vnd.microsoft.icon" href="http://example.com/image.ico"> 
        <link rel="shortcut icon" href="http://sstatic.net/so/favicon.ico">
        <link rel="apple-itouch-icon" href="http://sstatic.net/so/apple-touch-icon.png">
        <link rel="" href="http://www.google.com/favicon.ico" type="image/x-icon"/>

        url = "https://superagi.com/"
    """
    ## 1.0 
    import requests
    from bs4 import BeautifulSoup

    thumbnail_image_url = ""
    icon_url_list = []
    image_id_list = []
    image_dict = {}   

    default_icon_url = get_http_prefix_domain(url) + "/favicon.ico"
    icon_url_list.append(default_icon_url)

    try:
        headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}        
        head = None
        try:
            req = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
            soup = BeautifulSoup(req.text, "html.parser")
            head = soup.select("head")[0] if len(soup.select("head")) > 0 else None
        except Exception as e:
            print (e)
            print ("DEBUG: Timeout %s" % url)
        if head is not None:

            ## <link>
            links = head.select("link")
            if links is not None:
                for i, link in enumerate(links):
                    # link
                    rel = link["rel"] if link.has_attr("rel") else None
                    link_type = link["type"] if link.has_attr("type") else None
                    href = link["href"] if link.has_attr("href") else None
                    # print ("DEBUG: Link %d link %s" % (i, str(link)))
                    ## rel
                    if "shortcut" in rel or "icon" in rel or link_type == "image/x-icon":
                        if href is not None:
                            full_href = append_url(url, href)
                            icon_url_list.append(full_href)
                    ## normal link
                    if href is not None and is_image_url(href):
                        full_href = append_url(url, href)
                        if full_href != thumbnail_image_url:
                            image_id_list.append(full_href)
            
            ## <img> other image, e.g. <img> <meta property="og:image" content="https://www.workday.com/content/dam/web/en-us/images/social/workday-og-theme.png">
            images = head.select("img")
            if images != None:
                for image in images:
                    image_src = image["src"] if "src" in image.attrs else ""
                    if image_src != "":
                        image_id_list.append(image_src)

            ## meta <meta>
            meta_list = head.select("meta")
            if meta_list != None:
                for meta_tag in meta_list:
                    meta_content = meta_tag["content"] if "content" in meta_tag.attrs else ""
                    meta_property = meta_tag["property"] if "property" in meta_tag.attrs else ""
                    if is_image_url(meta_content):
                        image_id_list.append(meta_content)
            ## <src>
            ## <meta content>
    except Exception as e:
        traceback.print_exc()
        print (e)
    ## find the largest
    try:
        thumbnail_image_url = get_largest_icon_file(icon_url_list)   
    except FunctionTimedOut as e:
        print (e)

    ## add information
    image_dict[KEY_THUMBNAIL_PICTURE] = thumbnail_image_url
    image_dict[KEY_UPLOAD_IMAGE_FILES] = ",".join(image_id_list)
    return image_dict


@func_set_timeout(FETCH_TIMEOUT)
def fetch_website_icon_data_v2(url, driver):
    """ read website image icon data
        <link rel="icon" type="image/vnd.microsoft.icon" href="http://example.com/image.ico"> 
        <link rel="shortcut icon" href="http://sstatic.net/so/favicon.ico">
        <link rel="apple-itouch-icon" href="http://sstatic.net/so/apple-touch-icon.png">
        <link rel="" href="http://www.google.com/favicon.ico" type="image/x-icon"/>
        url = "https://superagi.com/"

        image_dict = fetch_website_icon_data_v2(url)
        

        e.g. https://www.workday.com/content/dam/web/zz/images/logos/workday/workday-logo.svg

    """
    ## 1.0 icon url
    thumbnail_image_url = ""
    icon_url_list = []
    image_id_list = []
    image_dict = {}

    default_icon_url = get_http_prefix_domain(url) + "/favicon.ico"
    icon_url_list.append(default_icon_url)

    try:
        headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}        
        head = None
        html = ""
        try:
            # driver.get(url)
            function_timeout_wrapper(driver, url)
            html = driver.page_source
            print ("DEBUG: Fetch URL Succeed|%s " % url)
        except FunctionTimedOut as e1:
            print ("DEBUG: Fetch URL Timeout|%s" % url)
            driver.execute_script("window.stop()")               
        
        soup = BeautifulSoup(html, "html.parser")
        head = soup.select("head")[0] if len(soup.select("head")) > 0 else None
        if head is not None:
            links = head.select("link")
            if links is not None:
                for i, link in enumerate(links):
                    if link is None:
                        continue
                    # link
                    rel = link["rel"] if link.has_attr("rel") else None
                    link_type = link["type"] if link.has_attr("type") else None
                    href = link["href"] if link.has_attr("href") else None
                    # print ("DEBUG: Link %d link %s" % (i, str(link)))
                    ## rel
                    if "shortcut" in rel or "icon" in rel or link_type == "image/x-icon":
                        if href is not None:
                            full_href = append_url(url, href)
                            icon_url_list.append(full_href)
                    ## normal link
                    if href is not None and is_image_url(href):
                        full_href = append_url(url, href)
                        if full_href != thumbnail_image_url:
                            image_id_list.append(full_href)
            ## other image
            images = head.select("img")
            if images != None:
                for image in images:
                    image_src = image["src"] if "src" in image.attrs else ""
                    if image_src != "":
                        image_id_list.append(image_src)
            ## meta <meta>
            meta_list = head.select("meta")
            if meta_list != None:
                for meta_tag in meta_list:
                    meta_content = meta_tag["content"] if "content" in meta_tag.attrs else ""
                    meta_property = meta_tag["property"] if "property" in meta_tag.attrs else ""
                    if is_image_url(meta_content):
                        image_id_list.append(meta_content)

    except Exception as e:
        traceback.print_exc()
        print (e)
    ## find the largest
    try:
        thumbnail_image_url = get_largest_icon_file(icon_url_list)
    except FunctionTimedOut as e:
        print (e)
    ## add information
    image_dict[KEY_THUMBNAIL_PICTURE] = thumbnail_image_url
    image_dict[KEY_UPLOAD_IMAGE_FILES] = ",".join(image_id_list)
    return image_dict


@func_set_timeout(REQUESTS_TIMEOUT * 10)
def get_image_file_sorted_by_size(image_url_list, topk):
    """
        get_largest_icon_file

        if image url not exist, don't append
    """
    import io
    if len(image_url_list) == 0:        
        return ""
    # filter small icon
    min_image_bytes = 2560
    requests_image_timeout = 10
    try:
        image_size_list = []
        for image_url in image_url_list:
            size = 0
            try:
                image = requests.get(image_url, timeout=5).content 
                image_b = io.BytesIO(image).read()
                size = len(image_b) ## B 
                print ("DEBUG: Processing Image image_url Success %s" % image_url)
            except Exception as e2:
                print (e2)
                size = 0
                print ("DEBUG: Processing Image image_url Failed %s" % image_url)                
            ## if not exist, don't append
            if size > min_image_bytes:
                image_size_list.append((size, image_url))
        image_size_list_sorted = sorted(image_size_list, key=lambda x:x[0], reverse=True)
        image_url_sorted = [pair[1] for pair in image_size_list_sorted]
        if len(image_url_sorted) > topk:
            image_url_sorted = image_url_sorted[0:topk]
        return image_url_sorted
    except Exception as e:
        print (e)
        traceback.print_exc()
        return image_url_list

@func_set_timeout(REQUESTS_TIMEOUT)
def get_largest_icon_file(image_url_list):
    """
        get_largest_icon_file

        if image url not exist, don't append
    """
    import io
    if len(image_url_list) == 0:        
        return ""
    final_image_url = ""
    requests_image_timeout = 10
    try:
        image_size_list = []
        for image_url in image_url_list:
            size = 0
            try:
                image = requests.get(image_url, timeout=REQUESTS_TIMEOUT).content 
                image_b = io.BytesIO(image).read()
                size = len(image_b) ## B 
            except Exception as e2:
                print (e2)
                size = 0
            ## if not exist, don't append
            if size > 0:
                image_size_list.append((size, image_url))
        image_size_list_sorted = sorted(image_size_list, key=lambda x:x[0], reverse=True)
        image_largest = image_size_list_sorted[0]
        final_image_url = image_largest[1]
    except Exception as e:
        print (e)
    return final_image_url


def get_ai_agent_by_category(category):
    """
        url
    """
    API_AI_AGENT_MARKETPLACE_ENDPOINT = "http://www.deepnlp.org/api/ai_agent_marketplace/v1"
    data = {}
    try:
        # required param
        input_param = {}
        input_param["category"] = category
        input_param["limit"] = 1000 
        input_param["return_fields"] = FIELD_STATISTIC
        timeout = 5
        url = API_AI_AGENT_MARKETPLACE_ENDPOINT
        kwparam_list = []
        for key, value in input_param.items():
            cur_kvparam = "%s=%s" % (str(key), str(value))
            kwparam_list.append(cur_kvparam)
        # print ("DEBUG: kwparam_list is %s" % str(kwparam_list))
        kvparam = "&".join(kwparam_list)
        if kvparam != "":
            url = url + "?" + kvparam
        try:
            print ("DEBUG: SearchFunctionAPI fetch url from %s" % url)
            result = requests.get(url, timeout=timeout)
            if result.status_code == 200:
                data = result.json()
            else:
                data = {}
            # print ("DEBUG: Response status %d" % (result.status_code))                
        except Exception as e2:
            print ("ERROR: requests.get url failed %s" % url)
            print (e2)
    except Exception as e:
        print (e)  
    return data

def test_get_largest_icon_file():
    image_url_list = ["https://static.canva.cn/static/images/android-192x192-2.png", "https://static.canva.cn/static/images/favicon-1.ico"]
    image_file = get_largest_icon_file(image_url_list)
    print ("DEBUG: Largest Image File %s" % image_file)

def test_fetch_url_from_driver():

    timeout = 60
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(timeout)
    driver.implicitly_wait(timeout);
    driver.set_script_timeout(timeout);

    urls = ["https://www.accio.com/"
        , "https://zeroagent.io"
        , "https://relevanceai.com/agent-templates-tasks/e-commerce-ai-agents"]

    fetch_data_list = []
    for url in urls:
        updated_data_dict = fetch_meta_image_from_url(driver, url)
        fetch_data_list.append(json.dumps(updated_data_dict))
    # print (fetch_data_list)
    save_file("./data/test_requests_util.json", fetch_data_list)

def main():
    test_fetch_url_from_driver()

if __name__ == '__main__':
    main()
