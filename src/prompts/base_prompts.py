category_prediction_prompts = '''
You are a question understanding and classification expert. Now you have to read a long text and assign a category tag to the long text.
Please follow the below steps:

### Tasks
1. Ignore the URLs and Htmls Tags in the Long Text.
2. Understand the main function of the introduction to the code repo, such as it's useful for financa API, automatic browsing, map route planning, etc.
3. Please classify the long text into only 1 categories from the blow category tags {category_tags}, and output in the "category" field of json object. For the detailed category description please follow {category_description_dict}
4. Please generate a "description" of the main features of the content, and output in the "description" field of json object.

### Requirements
1. For any content that may lies between the border of multiple categories, please sort the categories by relevance and pick the most relevant category and classify the item to the most relevant one.


### Output
1. Please output the predicted tag in json format, with two fields, "category" and "description"


### Examples

#### Example 1
**Content**
# 21st.dev Magic AI Agent

![MCP Banner](https://21st.dev/magic-agent-og-image.png)

Magic Component Platform (MCP) is a powerful AI-driven tool that helps developers create beautiful, modern UI components instantly through natural language descriptions. It integrates seamlessly with popular IDEs and provides a streamlined workflow for UI development.

## 🌟 Features

- **AI-Powered UI Generation**: Create UI components by describing them in natural language
- **Multi-IDE Support**:
  - [Cursor](https://cursor.com) IDE integration
  - [Windsurf](https://windsurf.ai) support
  - [VSCode](https://code.visualstudio.com/) support
  - [VSCode + Cline](https://cline.bot) integration (Beta)
- **Modern Component Library**: Access to a vast collection of pre-built, customizable components inspired by [21st.dev](https://21st.dev)
- **Real-time Preview**: Instantly see your components as you create them
- **TypeScript Support**: Full TypeScript support for type-safe development
- **SVGL Integration**: Access to a vast collection of professional brand assets and logos
- **Component Enhancement**: Improve existing components with advanced features and animations (Coming Soon)

## 🎯 How It Works

1. **Tell Agent What You Need**

   - In your AI Agent's chat, just type `/ui` and describe the component you're looking for
   - Example: `/ui create a modern navigation bar with responsive design`

2. **Let Magic Create It**

   - Your IDE prompts you to use Magic
   - Magic instantly builds a polished UI component
   - Components are inspired by 21st.dev's library

3. **Seamless Integration**
   - Components are automatically added to your project
   - Start using your new UI components right away
   - All components are fully customizable

**Output**
```
{{"category": "GUI", "description": "21st.dev Magic AI Agent Magic Component Platform (MCP) is a powerful AI-driven tool that helps developers create beautiful, modern UI components instantly through natural language descriptions. Main features include AI-Powered UI Generation, Multi-IDE Support, Modern Component Library, Real-time Preview, TypeScript Support, SVGL Integration and more."}}
```

#### Example 2
**Content**
# Firecrawl MCP Server

A Model Context Protocol (MCP) server implementation that integrates with [Firecrawl](https://github.com/mendableai/firecrawl) for web scraping capabilities.

> Big thanks to [@vrknetha](https://github.com/vrknetha), [@knacklabs](https://www.knacklabs.ai) for the initial implementation!


## Features

- Web scraping, crawling, and discovery
- Search and content extraction
- Deep research and batch scraping
- Automatic retries and rate limiting
- Cloud and self-hosted support
- SSE support

> Play around with [our MCP Server on MCP.so's playground](https://mcp.so/playground?server=firecrawl-mcp-server) or on [Klavis AI](https://www.klavis.ai/mcp-servers).

## Installation

**Output**
```
{{"category": "WEB", "description": "Firecrawl MCP Server is useful for web scraping capabilities with features: Web scraping, crawling, and discovery, Search and content extraction, Deep research and batch scraping,Automatic retries and rate limiting, Cloud and self-hosted support and also provides SSE support."}}
```

#### Example 3

**Content**
Funny MCP Server is the MCP server that can tell jokes to make AI laugh
**Output**
```
{{"category": "Miscellaneous", "description": "Funny MCP Server is the MCP server that can tell jokes to make AI laugh"}}
```

And the content need to be classified is 
**Content**
{content}
**Output**
'''
