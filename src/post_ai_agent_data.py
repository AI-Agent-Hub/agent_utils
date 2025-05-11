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

def post_data_website_agent_demo():
    """
        HttpSession session = request.getSession();
            if (session == null) {
                return false;
            }
            String userId = (String) session.getAttribute(KEY_USER_ID);
            boolean ifAuthentificate = false;
    """
    import requests
    url = "http://localhost:8080/addAIServiceContent"

    user_id = "User 1"
    access_key = ""
    content_id = None # optional
    input_json = {"publisher_id": "my-publishser-1", "content_name": "My Service 2", "content": "This is My Service Content"
        , "field": "AI Agent", "subfield": "AI Agent", "content_tag_list": "tag1, tag2, tag3", "website": "http://www.website.org", "access_key": access_key, "user_id": user_id}
    try:
        res = requests.post(url=url,data=input_json)
    except Exception as e:
        print (e)

def get_sug_by_name(content_name):
    """
    """
    content_name_lower = content_name.lower()
    content_name_lower_seg = content_name_lower.split(" ")
    content_name_sug = "-".join(content_name_lower_seg)
    return content_name_sug

def get_date():
    """
    """
    import datetime
    now = datetime.datetime.now()
    # today = datetime.date.today()
    # datetimestr = str(today.year) + str(today.month) + str(today.day)
    datetimestr = str(now.year) + str(now.month) + str(now.day)
    return datetimestr

def post_add_data_ai_agent(args):
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
    url = "http://www.deepnlp.org/addAIServiceContent"
    user_id = "AI Hub Admin"
    access_key = ""
    access_key_personal = ""
    data_file = args.data_file 
    print ("DEBUG: post_add_data_ai_agent Input Data File %s" % data_file)
    data_file_list = [data_file]
    for data_file in data_file_list:
        lines = read_file(data_file)
        for i, line in enumerate(lines):
            ## add failed due to too long ext_info from html
            output_json = json.loads(line)
            if output_json is None:
                continue
            output_json[KEY_HTML] = ""
            output_json["user_id"] = user_id
            output_json["access_key"] = access_key
            output_json["status"] = 1
            output_json["ext_info"] = json.dumps({})

            try:
                content_name = output_json["content_name"] if "content_name" in output_json else ""
                output_json[KEY_PUBLISHER_ID] = get_sug_by_name(content_name)
                res = requests.post(url=url,data=output_json, timeout=5)                
                status_code = res.status_code
                print ("DEBUG: Line %d, %s, status %s" % (i, content_name, status_code))
            except Exception as e:
                print (e)
            time.sleep(2)

def post_update_data_ai_agent(args):
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
    url = "http://www.deepnlp.org/updateAIServiceContent"
    user_id = "AI Hub Admin"
    access_key = ""

    # data_str = get_date()
    data_file = args.data_file 
    print ("DEBUG: post_update_data_ai_agent Input Data File %s" % data_file)
    data_file_list = [data_file]

    ## content_name
    content_name_dict = {}
    for data_file in data_file_list:
        lines = read_file(data_file)
        print ("DEBUG: Total input lines Count %d" % len(lines))
        for i, line in enumerate(lines):
            input_json = json.loads(line)
            content_name = input_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in input_json else ""
            publisher_id = get_sug_by_name(content_name)
            input_json[KEY_PUBLISHER_ID] = publisher_id

            if content_name in content_name_dict:
                cur_list = content_name_dict[content_name]
                cur_list.append(input_json)
                content_name_dict[content_name] = cur_list
            else:
                content_name_dict[content_name] = [input_json]

    # updated_keys_list = [KEY_CONTENT, KEY_UPLOAD_IMAGE_FILES, KEY_THUMBNAIL_PICTURE]
    updated_keys_list = [KEY_CONTENT, KEY_THUMBNAIL_PICTURE]
    # updated_keys_list = [KEY_CONTENT, KEY_UPLOAD_IMAGE_FILES]
    for content_name in content_name_dict.keys():
        cur_list = content_name_dict[content_name]
        cur_list_sorted = sorted(cur_list, key=lambda x:len(x[KEY_UPLOAD_IMAGE_FILES] if KEY_UPLOAD_IMAGE_FILES in x else ""), reverse=True)
        if len(cur_list_sorted) > 0:
            input_json = cur_list_sorted[0]

            ## update by content name and sug
            output_json = {}
            output_json[KEY_CONTENT_NAME] = input_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in input_json else ""
            output_json[KEY_PUBLISHER_ID] = input_json[KEY_PUBLISHER_ID] if KEY_PUBLISHER_ID in input_json else ""
            for key in updated_keys_list:
                output_json[key] = input_json[key] if key in input_json else ""
            output_json[KEY_STATUS] = 1
            output_json["ext_info"] = json.dumps({})
            # if output_json[KEY_CONTENT_NAME] != "newo ai":
            #     continue
            if output_json is None:
                continue
            output_json["user_id"] = user_id
            output_json["access_key"] = access_key
            # print ("DEBUG: Post data output_json %s" % str(output_json))
            try:
                content_name = output_json[KEY_CONTENT_NAME] if KEY_CONTENT_NAME in output_json else ""
                res = requests.post(url=url,data=output_json, timeout=5)                
                status_code = res.status_code
                print ("DEBUG: %s, status %s" % (content_name, status_code))
                # print ("DEBUG: %s, status %s, output_json %s" % (content_name, status_code, str(output_json)))
            except Exception as e:
                print (e)
            time.sleep(3)

def row_mapper_article(input_json, tag_list):
    """
        ## ICML source
        {'abs': 'https://proceedings.mlr.press/v235/abad-rocamora24a.html',
         'Download PDF': 'https://raw.githubusercontent.com/mlresearch/v235/main/assets/abad-rocamora24a/abad-rocamora24a.pdf',
         'OpenReview': 'https://openreview.net/forum?id=AZWqXfM6z9',
         'title': 'Revisiting Character-level Adversarial Attacks for Language Models',
         'url': 'https://proceedings.mlr.press/v235/abad-rocamora24a.html',
         'authors': 'Elias Abad Rocamora, Yongtao Wu, Fanghui Liu, Grigorios Chrysos, Volkan Cevher',
         'detail_url': 'https://proceedings.mlr.press/v235/abad-rocamora24a.html',
         'tags': 'ICML 2024',
         'abstract': 'Adversarial attacks in Natural Language Processing apply perturbations in the character or token levels. Token-level attacks, gaining prominence for their use of gradient-based methods, are susceptible to altering sentence semantics, leading to invalid adversarial examples. While character-level attacks easily maintain semantics, they have received less attention as they cannot easily adopt popular gradient-based methods, and are thought to be easy to defend. Challenging these beliefs, we introduce Charmer, an efficient query-based adversarial attack capable of achieving high attack success rate (ASR) while generating highly similar adversarial examples. Our method successfully targets both small (BERT) and large (Llama 2) models. Specifically, on BERT with SST-2, Charmer improves the ASR in $4.84$% points and the USE similarity in $8$% points with respect to the previous art. Our implementation is available in https://github.com/LIONS-EPFL/Charmer.'}

        ## NIPS source
        {'title': 'Modelling Cellular Perturbations with the Sparse Additive Mechanism Shift Variational Autoencoder',
         'url': 'https://papers.nips.cc/paper_files/paper/2023/hash/0001ca33ba34ce0351e4612b744b3936-Abstract-Conference.html',
         'authors': 'Michael Bereket, Theofanis Karaletsos',
         'detail_url': 'https://papers.nips.cc/paper_files/paper/2023/hash/0001ca33ba34ce0351e4612b744b3936-Abstract-Conference.html',
         'Bibtex': 'https://papers.nips.cc/paper_files/paper/20165-/bibtex',
         'Paper': 'https://papers.nips.cc/paper_files/paper/2023/file/0001ca33ba34ce0351e4612b744b3936-Paper-Conference.pdf',
         'Supplemental': 'https://papers.nips.cc/paper_files/paper/2023/file/0001ca33ba34ce0351e4612b744b3936-Supplemental-Conference.pdf',
         'abstract': 'Generative models of observations under interventions have been a vibrant topic of interest across machine learning and the sciences in recent years. For example, in drug discovery, there is a need to model the effects of diverse interventions on cells in order to characterize unknown biological mechanisms of action. We propose the Sparse Additive Mechanism Shift Variational Autoencoder, SAMS-VAE, to combine compositionality, disentanglement, and interpretability for perturbation models. SAMS-VAE models the latent state of a perturbed sample as the sum of a local latent variable capturing sample-specific variation and sparse global variables of latent intervention effects. Crucially, SAMS-VAE sparsifies these global latent variables for individual perturbations to identify disentangled, perturbation-specific latent subspaces that are flexibly composable. We evaluate SAMS-VAE both quantitatively and qualitatively on a range of tasks using two popular single cell sequencing datasets.In order to measure perturbation-specific model-properties, we also introduce a framework for evaluation of perturbation models based on average treatment effects with links to posterior predictive checks. SAMS-VAE outperforms comparable models in terms of generalization across in-distribution and out-of-distribution tasks, including a combinatorial reasoning task under resource paucity, and yields interpretable latent structures which correlate strongly to known biological mechanisms. Our results suggest SAMS-VAE is an interesting addition to the modeling toolkit for machine learning-driven scientific discovery.'}        

        map row:

            "title", "detail_url", "author_list", "abstract"
    """
    title = input_json["title"] if "title" in input_json else ""
    detail_url = input_json["detail_url"] if "detail_url" in input_json else ""
    authors = input_json["authors"] if "authors" in input_json else ""
    abstract = input_json["abstract"] if "abstract" in input_json else ""

    ## 
    input_tags = input_json["tags"] if "tags" in input_json else ""
    all_tag_list = []
    ## append first tags
    all_tag_list.append(input_tags)
    ## extend tag list
    all_tag_list.extend(tag_list)
    tags = ",".join(all_tag_list)

    # content
    output_content_dict = {"abstract": abstract, 
                    "url": detail_url, 
                    "authors": authors, 
                    "tags": tags, 
                    "title": title
                    }
    ## other fields
    # openreview
    for key in ["OpenReview", "Download PDF", "pdf", "Bibtex", "Paper", "Supplemental"]:
        if key in input_json:
            value = input_json[key]
            key_norm = ""
            if key == "OpenReview":
                key_norm = "openreview"
            elif key == "Download PDF" or key == "pdf" or key == "Paper" or key == "arXiv":
                ## download pdf
                key_norm = "url_pdf_download"
            elif key == "Bibtex" or key == "bibtex":
                key_norm = "bibtex"
            elif key == "Supplemental" or key == "supp":
                key_norm = "supplemental"
            else:
                key_norm = ""
            if key_norm != "" and value != "":
                output_content_dict[key_norm] = value

    output_json = {}
    # output_json["user_id"] = user_id
    # output_json["user_name"] = user_name
    output_json["content"] = json.dumps(output_content_dict)
    output_json["content_name"] = title
    output_json["status"] = 1
    output_json["sug"] = get_sug_by_name(title)
    return output_json

def post_article():
    """
        HttpSession session = request.getSession();
            if (session == null) {
                return false;
            }
            String userId = (String) session.getAttribute(KEY_USER_ID);
            boolean ifAuthentificate = false;

        SELECT * FROM dp_entity_content WHERE user_id = "AI Hub Admin"
    """
    import requests
    url = "http://www.deepnlp.org/addArticleContent"
    user_id = "Article Admin"
    user_name = "Article Admin"
    access_key = ""
    files_list = [
            ("./data/cvpr_2023.json", [])   
            , ("./data/cvpr_2022.json", []) 
            , ("./data/cvpr_2021.json", [])   
            , ("./data/cvpr_2020_1.json", [])    
            , ("./data/cvpr_2020_2.json", [])    
            , ("./data/cvpr_2020_3.json", [])    
    ]
    for (file_path, tag_list) in files_list:
        lines = read_file(file_path)
        print ("DEBUG: Start Reading file path %s" % file_path)
        for i, line in enumerate(lines):
            input_json = json.loads(line)
            output_json = row_mapper_article(input_json, tag_list)
            if output_json is None:
                continue
            output_json["user_id"] = user_id
            output_json["user_name"] = user_name
            output_json["access_key"] = access_key
            print (output_json)
            ## post
            try:
                res = requests.post(url=url,data=output_json)
                title = input_json["title"] if "title" in input_json else ""
                print ("DEBUG:Status Code: %d| title %s | file path %s" % (res.status_code, title, file_path))
                # print (output_json)
            except Exception as e:
                print (e)
                title = output_json["title"] if "title" in output_json else ""
                print ("DEBUG: Error processing title|" + title + '|path|' + file_path)
            time.sleep(2)

def main():
    """
        python3 post_ai_agent_data.py --data_file "./data/merge/maintext/merge_ai_agent_meta_ai_employee.json"
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, default="", help='Input Data File of list of Json ')
    parser.add_argument('--mode', type=str, default="", help='Mode of Processing')
    args = parser.parse_args()

    mode = args.mode
    if mode == "add":
        post_add_data_ai_agent(args)
    elif mode == "update":
        post_update_data_ai_agent(args)
    else:
        print ("DEBUG: mode not supported %s" % mode)

if __name__ == '__main__':
    main()
