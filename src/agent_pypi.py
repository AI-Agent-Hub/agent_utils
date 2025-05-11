import os
import codecs
import time

from process_ai_agent import process_merge_ai_agent_file

def read_file(file_path):
    if not os.path.exists(file_path):
        print ("DEBUG: file_path not exists %s" % file_path)
        return []
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

def get_current_timestamp():
    timestamp = int(time.time())
    return timestamp

def get_current_datetime():
    import datetime    
    now = datetime.datetime.now()
    datetime = now.strftime('%Y-%m-%d %H:%M:%S')
    return datetime

readme_file_template = '''# {} AI Agent Directory to Host All {} related AI Agents Web Traffic Data, Search Ranking, Community, Reviews and More.

This is the official github repo for pypi package "{}" {}. You can use this package to download and get statistics (Google/Bing Search Ranking/Github Stars/Website Traffic) of AI agents on website from AI Agent Marketplace AI Agent Directory and AI Agent Search Portal by Deepnlp AI Agent Marketplace, is the directory for more than 5000+ AI Agents and Apps covering various types of AI agents, such as autonomous agent, chatbots, Computer and Mobile phone use agents, robotic agents, and various industries such as business, finance, law, medical or healthcare, etc. The directory are updated to websites from both public repo (github/huggingface) as well as AI Agent services in cloud service provider (Microsoft Azure AWS, Copilot, GPT Store, Google Cloud, etc). 

### AI Agent Search Engine

Website : http://www.deepnlp.org/search/agent

Find the AI Agent in any category and get the realtime search/app store/github ranking data

![AI Agent Marketplace Directory Search](https://raw.githubusercontent.com/AI-Agent-Hub/AI-Agent-Marketplace/refs/heads/main/AI%20Agent%20Marketplace%20Search.jpg)

Register and list your AI agent For Free through (http://www.deepnlp.org/workspace/my_ai_services)

### AI Agent Directory

Website: http://www.deepnlp.org/store/ai-agent

![AI Agent Marketplace AI Agent Directory](https://raw.githubusercontent.com/AI-Agent-Hub/AI-Agent-Marketplace/refs/heads/main/docs/ai_agents_navigation.jpg)

#### Track Google/Bing Search Ranking Data

For example, if you want to know the AI coding agent traffic data, you can visit (http://www.deepnlp.org/store/ai-agent#section_Coding%20Agent)

You can track vanna.ai, Cody and Cline bot, etc.

- cline bot (http://www.deepnlp.org/store/ai-agent/coding-agent/pub-cline-bot/cline-bot) has google search ranking 37.0 and bing search ranking 15.0, and under search keywords such as "AI Coding Agent, AI Coding, etc.", it got 22.8k Github stars 
- vanna.ai (http://www.deepnlp.org/store/ai-agent/ai-agent/pub-vanna-ai/vanna-ai)
- Cody Sourcegraph (http://www.deepnlp.org/store/ai-agent/ai-agent/pub-cody-by-sourcegraph/cody-by-sourcegraph)
- Taskade.com (http://www.deepnlp.org/store/ai-agent/finance/pub-taskade/taskade)

![AI Coding Agent](https://raw.githubusercontent.com/AI-Agent-Hub/AI-Agent-Marketplace/refs/heads/main/docs/image_coding_agent_v2.jpg)


### AI Agent List

{}


## Install


```
pip install {}

```

## Usage
python 

```
import {}
from {}.utils import function_to_schema

```


### Related
#### AI Agent Marketplace and Search
[AI Agent Marketplace and Search](http://www.deepnlp.org/search/agent) <br>
[AI Robot Search](http://www.deepnlp.org/search/robot) <br>
[Equation and Academic search](http://www.deepnlp.org/search/equation) <br>
[AI & Robot Comprehensive Search](http://www.deepnlp.org/search) <br>
[AI & Robot Question](http://www.deepnlp.org/question) <br>
[AI & Robot Community](http://www.deepnlp.org/community) <br>
##### AI Agent
[AI Agent Marketplace Reviews](http://www.deepnlp.org/store/ai-agent) <br>
[AI Agent Marketplace and Search Portal Reviews 2025](http://www.deepnlp.org/blog/ai-agent-marketplace-and-search-portal-reviews-2025) <br>
[AI Agent Publisher](http://www.deepnlp.org/store/pub?category=ai-agent) <br>
[Microsoft AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-microsoft-ai-agent) <br>
[Claude AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-claude-ai-agent) <br>
[OpenAI AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-openai-ai-agent) <br>
[AgentGPT AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-agentgpt) <br>
[Saleforce AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-salesforce-ai-agent) <br>
[AI Agent Builder Reviews](http://www.deepnlp.org/store/ai-agent/ai-agent-builder) <br>
##### Robotics
[Tesla Cybercab Robotaxi](http://www.deepnlp.org/store/pub/pub-tesla-cybercab) <br>
[Tesla Optimus](http://www.deepnlp.org/store/pub/pub-tesla-optimus) <br>
[Figure AI](http://www.deepnlp.org/store/pub/pub-figure-ai) <br>
#### Equation
[DeepNLP Equation Database](http://www.deepnlp.org/equation) <br>
'''


setup_file_template = '''# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

install_requires = [
    "requests>=2.17.0"
]

extras = dict()
extras["dev"] = []
extras["test"] = extras["dev"] + []

setup(
    name="{}",   # Required
    version="{}",    # Required
    description="{} AI Agent Directory to Host All {} related AI Agents Services, Community, Reviews and More.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="AI Agent Hub",
    author_email="dingo0927@126.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="{}, AI Agent Marketplace,AI Agent Directory,AI Agents,Agentic AI",
    packages=find_packages(where="src"),  # Required
    install_requires=install_requires,    # Required    
'''

setup_file_template_b = '''
    package_dir={"": "src"},
    python_requires=">=3.4",
    project_urls={
        "homepage": "http://www.deepnlp.org/store/ai-agent",
        "repository": "https://github.com/AI-Agent-Hub/AI-Agent-Marketplace"
    },
)
'''

util_file_output = '''import os
import inspect
import codecs
import json
from typing import get_type_hints
import traceback

### Agent Function Conversion
def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }



def function_to_schema_claude(func) -> dict:
    """
        Compatible with Claude's function calling schema
        Ref: 
        https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "name" : func.__name__, 
        "description": (func.__doc__ or "").strip(),
        "input_schema": {
            "type": "object",
            "properties": parameters,
            "required": required
        }
    }

'''


toml_output = """
[build-system]
requires = ["setuptools >= 64.0"]
build-backend = "setuptools.build_meta"
"""

build_package_str = """python3 -m pip install twine

## install locally
python3 -m pip install -e .
python3 -m pip install -e . --no-deps

## package
python3 -m pip install build

### build wheel
python3 -m build --wheel
## build source

twine upload dist/*
"""

def get_normal_name(name):
    words = name.split(" ")
    words_norm = [w.lower() for w in words]
    output = "_".join(words_norm)
    return output

group_markdown_json, group_data_json = process_merge_ai_agent_file()

## update group markdown json norm
group_markdown_json_norm = {}
for key in group_markdown_json.keys():
    key_norm = key.lower()
    group_markdown_json_norm[key_norm] = group_markdown_json[key]
print ("DEBUG: group_markdown_json_norm keys List:")
for key in group_markdown_json_norm.keys():
    json_data = group_markdown_json_norm[key] if key in group_markdown_json_norm else []
    cnt = len(json_data)
    print (key + ":" + str(cnt))

def get_markdown_content(category):
    """
    """
    # markdown_file = "./markdown/%s" %  agent_package_name + "_agent_list.md"
    # markdown_file_lines = read_file(markdown_file)
    # markdown_content = "\n".join(markdown_file_lines)
    readme_markdown = []

    category_norm = category.lower().strip()
    category_clean = category_norm.replace("agent", "").strip()  ## "email writing agent" -> "email writing " -> "email writing"
    category_agent = category_norm + " agent" if "agent" not in category_norm else category_norm
    category_list = [category_norm, category_clean.lower(), category_agent]
    
    if_fetch_markdown = False

    for key in category_list:
        if key in group_markdown_json_norm:
            print ("DEBUG: category supported %s" % key)
            readme_markdown = group_markdown_json_norm[key]
            if_fetch_markdown = True
            break
        else:
            print ("DEBUG: category is not support %s" % key)
    if not if_fetch_markdown:
        print ("DEBUG: if_fetch_markdown false category|" + category)
    else:
        print ("DEBUG: if_fetch_markdown true category|" + category)
    return readme_markdown

def get_markdown_content_api(category):
    """
    """

    import ai_agent_marketplace
    readme_markdown = []
    
    category_norm = category.lower().strip()
    category_clean = category_norm.replace("agent", "").strip()  ## "email writing agent" -> "email writing " -> "email writing"
    category_agent = category_norm + " agent" if "agent" not in category_norm else category_norm
    category_list = [category_norm, category_clean.lower(), category_agent]
    
    if_fetch_markdown = False

    for key in category_list:
        if key in group_markdown_json_norm:
            print ("DEBUG: category supported %s" % key)
            readme_markdown = group_markdown_json_norm[key]
            if_fetch_markdown = True
            break
        else:
            print ("DEBUG: category is not support %s" % key)
    if not if_fetch_markdown:
        print ("DEBUG: if_fetch_markdown false category|" + category)
    else:
        print ("DEBUG: if_fetch_markdown true category|" + category)
    return readme_markdown


def create_pypi_package(category, agent_package_name, package_dir):
    """
        category: kw1, kw2
    """
    if not os.path.exists(package_dir):
        os.mkdir(package_dir)
    else:
        print ("DEBUG: package_dir Exists %s" % package_dir)

    save_file(os.path.join(package_dir, "__init__.py"), [""])

    dist_path = os.path.join(package_dir, "dist")
    if not os.path.exists(dist_path):
        os.mkdir(dist_path) 

    ## write readme_file
    version = "0.0.2"
    
    # markdown_file = "./markdown/%s" %  agent_package_name + "_agent_list.md"
    markdown_file_lines = get_markdown_content(category)
    markdown_content = "\n".join(markdown_file_lines)
    
    package_name_norm = get_normal_name(agent_package_name)
    pypi_url = "https://pypi.org/project/%s" % agent_package_name
    readme_file_str = readme_file_template.format(category, category, package_name_norm, pypi_url, markdown_content, version, package_name_norm, package_name_norm, package_name_norm)
    readme_file_path = os.path.join(package_dir, "README.md")
    save_file(readme_file_path, [readme_file_str])

    ## setuo file
    setup_file_str = setup_file_template.format(agent_package_name, version, category, category, category) + setup_file_template_b
    setup_file_path = os.path.join(package_dir, "setup.py")
    save_file(setup_file_path, [setup_file_str])

    ## src
    os.mkdir(os.path.join(package_dir, "src"))
    os.mkdir(os.path.join(package_dir, "src/{}".format(package_name_norm)))

    init_file_path = os.path.join(package_dir, "src/{}/__init__.py".format(package_name_norm))
    save_file(init_file_path, [""])

    utils_file_path = os.path.join(package_dir, "src/{}/utils.py".format(package_name_norm))
    save_file(utils_file_path, [util_file_output])

    toml_output_path = os.path.join(package_dir, "pyproject.toml")
    save_file(toml_output_path, [toml_output])

    build_package_path = os.path.join(package_dir, "build_package.sh")
    save_file(build_package_path, [build_package_str])

def main():
    input_files = read_file("./pypi_agent_name_list.txt")
    workspace = "./agent_pypi"
    for category in input_files:
        category = category.strip()
        package_name_norm = get_normal_name(category)
        package_dir = os.path.join(workspace, package_name_norm)
        print ("DEBUG: Creating Package from category %s" % category)
        create_pypi_package(category, package_name_norm, package_dir)

if __name__ == '__main__':
    main()
