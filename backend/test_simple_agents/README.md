# Simple Agent Tests

This folder contains test scripts for different types of agents with various tool combinations.

## Test Scripts

1. **test_calculation_agent.sh** - Math and calculation agent with multiple calculation tools
2. **test_analysis_agent.sh** - Text and data analysis agent 
3. **test_research_agent.sh** - Research agent with Google Search and web tools
4. **test_finance_agent.sh** - Finance agent with Yahoo Finance and market data tools
5. **test_product_agent.sh** - Product discovery agent with Product Hunt integration

## Usage

Each script follows the same pattern:
1. Creates an agent with specific tools
2. Starts a conversation session
3. Performs 3 streaming interactions
4. Tests different capabilities of the agent

Run any script:
```bash
chmod +x test_*.sh
./test_calculation_agent.sh
```

## Prerequisites

- Server running on localhost:8000
- curl and jq installed
- Valid authentication credentials
