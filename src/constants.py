# -*- coding: utf-8 -*-

KEY_THUMBNAIL_PICTURE = "thumbnail_picture"
KEY_UPLOAD_IMAGE_FILES = "upload_image_files"
## meta
KEY_FIELD = "field"
KEY_SUBFIELD = "subfield"
KEY_CATEGORY = "category"
KEY_CONTENT_TAG_LIST = "content_tag_list"

KEY_CONTENT = "content"
KEY_TAGS = "tags"
KEY_CATEGORY = "category"
KEY_WEBSITE = "website"
KEY_PUBLISHER_ID = "publisher_id"
KEY_STATUS = "status"
KEY_DESCRIPTION = "description"
KEY_RANK = "rank"
KEY_REPO_STAR = "repo_star"
KEY_DOMAIN = "domain"
KEY_METRIC = "metric"
KEY_STATISTIC = "statistic"

KEY_GOOGLE_CONTENT_NAME = "content_name"
KEY_GOOGLE_CONTENT_META = "content_meta"
KEY_GOOGLE_IMAGE   = "thumbnail_picture"
KEY_GOOGLE_CONTENT = "content"
KEY_GOOGLE_WEBSITE = "website"
KEY_GOOGLE_RANK = "rank"
KEY_SOURCE = "source"
KEY_DT = "dt"
KEY_QUERY = "query"
KEY_MONTH = "month"

DATA_SOURCE_GOOGLE = "google"
DATA_SOURCE_BING = "bing"
DATA_SOURCE_GITHUB = "github"
DATA_SOURCE_ARXIV = "arxiv"

KEY_BING_CONTENT_NAME = "content_name"
KEY_BING_CONTENT_META = "content_meta"
KEY_BING_IMAGE   = "thumbnail_picture"
KEY_BING_CONTENT = "content"
KEY_BING_WEBSITE = "website"
KEY_BING_RANK = "rank"

KEY_HTML = "html"
KEY_MAIN_TEXT = "main_text"

KEY_CONTENT_NAME = "content_name"

GOOGLE_PAGE_RANK_BASE_OFFSET = 50
BING_PAGE_RANK_BASE_OFFSET = 50

RETRY_INTERVAL = 30
RETRY_INTERVAL_BING = 10

RETRY_INTERVAL_GOOGLE = 30

DEFAULT_RANK = 200

FETCH_TIMEOUT = 20
REQUESTS_TIMEOUT = 10

## BING 
CHANNEL_BING_CATEGORY = "bing_category"
## category + whitelist name, dict category
CHANNEL_BING_WHITELIST = "bing_whitelist_query"
## category_offline history + website history
CHANNEL_BING_HISTORY_ITEM = "bing_history_item"
CHANNEL_WHITELIST_META = "bing_whitelist_meta"



CHANNEL_GOOGLE_CATEGORY = "google_category"
CHANNEL_GOOGLE_WHITELIST_QUERY = "google_whitelist_query"
CHANNEL_GOOGLE_HISTORY_ITEM = "google_history_item"
CHANNEL_GOOGLE_WHITELIST_META = "google_whitelist_meta"


### METRIC
METRIC_GOOGLE_RANK = "Google Rank"
METRIC_BING_RANK = "Bing Rank"
METRIC_GITHUB_STAR = "GitHub Star"
METRIC_ARXIV_REFERENCE = "Arxiv Reference"


### KEY
FIELD_STATISTIC = "statistic"

### 
CONTENT_NAME_GITHUB = "github"

FILL_EXTINFO_ENABLE = "fill_extinfo_enable"
KEY_CHANNELS = "channels"


### URL 

# from bs4 import BeautifulSoup
#### Google Search Engine

GOOGLE_base_query_template_en = "https://www.google.com/search?q=%s"
GOOGLE_base_query_template_param = "&sca_esv=c4730c0d5f6ba8e9&sxsrf=AHTn8zr7R5XzZRHO-63biYMgI6RRYo8W3A%3A1743465506939&source=hp&ei=IizrZ6urN87akPIP-oTd4QI&iflsig=ACkRmUkAAAAAZ-s6Mp-2MI_-GiiSs-Omu9ocHuG2VqJ0&oq=f&gs_lp=Egdnd3Mtd2l6GgIYASIBZioCCAAyBBAjGCcyChAjGIAEGCcYigUyChAjGIAEGCcYigUyBRAAGIAEMgsQLhiABBjRAxjHATIFEAAYgAQyCBAAGIAEGIsDMhQQLhiABBjRAxjSAxjHARioAxiLAzIIEAAYgAQYiwMyBRAAGIAESIULUNgCWNgCcAF4AJABAJgBoQKgAaECqgEDMi0xuAEByAEA-AEBmAICoAKtAqgCCsICBxAjGCcY6gLCAgoQIxjwBRgnGOoCmAMJ8QVh2kaHLjVEApIHBTEuMC4xoAfgCQ&sclient=gws-wiz"

# base_query_template_en = "https://www.bing.com/search?q=%s&form=QBLHCN&sp=-1&lq=0&sc=12-9&qs=n&sk=&cvid=AA2C705F2B504D6E825F3BD1CFABE444&ghsh=0&ghacc=0&ghpl="
base_query_template_en = "https://www.bing.com/search?q=%s"
base_query_template_en_param = "&qs=HS&pq=a&sc=12-1&cvid=2050401D88214FAD91F41AAE8B83BC87&FORM=QBLH&sp=1&lq=0"

base_query_template_cn = "https://cn.bing.com/search?q=%s"
base_query_template_cn_param = "&form=QBLH&sp=-1&lq=0&pq=ai+age&sc=12-6&qs=n&sk=&cvid=3EED489FEBE74BBBA54EE64A28CC7EC2&ghsh=0&ghacc=0&ghpl="



BING_DEFAULT_ICON_URL = "https://th.bing.com/th?id=ODLS.A2450BEC-5595-40BA-9F13-D9EC6AB74B9F&w=32&h=32&qlt=90&pcl=fffffa&o=6&pid=1.2"


