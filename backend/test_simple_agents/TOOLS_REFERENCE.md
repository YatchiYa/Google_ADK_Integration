# Google ADK Tools Reference

## Available Tools in the System

Based on the tool manager analysis, here are the tools available for agent creation:

### 🔍 **Search & Research Tools**
- **`google_search`** - Google ADK built-in Google Search tool with web grounding
- **`load_memory`** - Search and load relevant information from memory

### 🧮 **Calculation & Analysis Tools**
- **`custom_calculator`** - Safe calculator for mathematical expressions and basic arithmetic
- **`text_analyzer`** - Analyze text for word count, sentiment, and other metrics

### 💰 **Financial Data Tools**
- **`yahoo_finance_data`** - Get real-time and historical financial data from Yahoo Finance (stocks, crypto, symbols)

### 🚀 **Product Discovery Tools**
- **`product_hunt_search`** - Search Product Hunt for products, posts, and collections

## Tool Combinations Used in Tests

### 1. **Calculation Agent**
```json
"tools": ["custom_calculator", "text_analyzer", "load_memory"]
```
- Mathematical calculations and statistical analysis
- Text metrics and analysis
- Memory storage for calculation results

### 2. **Analysis Agent**
```json
"tools": ["text_analyzer", "custom_calculator", "load_memory"]
```
- Advanced text analysis and sentiment evaluation
- Statistical calculations for content metrics
- Memory integration for analysis insights

### 3. **Research Agent**
```json
"tools": ["google_search", "text_analyzer", "load_memory"]
```
- Web research and information gathering
- Content quality analysis of search results
- Research findings storage in memory

### 4. **Finance Agent**
```json
"tools": ["yahoo_finance_data", "custom_calculator", "text_analyzer", "load_memory"]
```
- Real-time financial data retrieval
- Financial calculations and portfolio metrics
- Financial news analysis
- Investment strategy storage

### 5. **Product Discovery Agent**
```json
"tools": ["product_hunt_search", "text_analyzer", "custom_calculator", "load_memory"]
```
- Product discovery via Product Hunt API
- Product description analysis
- Market metrics calculations
- Product insights storage

## Best Practices for Tool Selection

1. **Always include `load_memory`** for persistent insights across conversations
2. **Combine complementary tools** - e.g., data retrieval + analysis + calculations
3. **Match tools to agent expertise** - financial tools for finance agents, etc.
4. **Use `text_analyzer`** when dealing with content evaluation or sentiment analysis
5. **Include `custom_calculator`** for any numerical computations or metrics

## Tool Registration Information

All tools are registered in the `ToolManager` with:
- **Name**: Unique identifier for the tool
- **Description**: Detailed explanation of tool capabilities
- **Category**: Organizational grouping
- **Author**: Tool creator (system/user/custom)

Tools can be dynamically registered and unregistered via the API endpoints.
