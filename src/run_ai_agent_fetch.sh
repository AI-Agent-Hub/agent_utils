### Update AI Service and Fetch from WebCrawler

## /data/merge/agent_github_data_%s.json
python3 fetch_ai_agent.py github

## /data/merge/${date}/merge_bing_data.json, turn on VPN
python3 fetch_ai_agent.py bing

## /data/merge/${date}/merge_arxiv_data.json
python3 fetch_ai_agent.py arxiv


python3 fetch_ai_agent.py google


## Post Data and Statistic
python3 post_ai_agent_data.py

## Post Statistic Data
python3 post_ai_statistic.py


## process
python3 fetch_ai_agent.py google
python3 fetch_ai_agent.py bing


##  process meta 
python3 process_ai_agent.py

## google Legal
python3 fetch_ai_agent.py google --restart_from_category "Legal" --date "20250303"

## bing
python3 fetch_ai_agent.py bing --restart_from_category "Healthcare" --date "20250303"

## merge
python3 fetch_ai_agent.py google --date "20250306" --mode "merge"
