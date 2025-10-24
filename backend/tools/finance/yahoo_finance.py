
import yfinance as yf
from datetime import datetime, timedelta 
import pytz
from loguru import logger  



def yahoo_finance_data(symbol: str, interval: str = "5m", range_type: str = "today") -> str:
    """
    Yahoo Finance tool for retrieving financial data
    
    Args:
        symbol: Stock symbol (e.g., BTC-USD, AAPL, GOOGL)
        interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d)
        range_type: Type of date range (today, week, month, ytd)
        
    Returns:
        str: Formatted financial data
    """
    try:
        logger.info(f"Fetching Yahoo Finance data for {symbol} with {interval} interval")
        
        # Create Ticker object
        ticker = yf.Ticker(symbol)
        
        # Get date range
        ny_tz = pytz.timezone('America/New_York')
        now = datetime.now(ny_tz)
        
        if range_type == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_type == "week":
            start = now - timedelta(days=7)
            end = now
        elif range_type == "month":
            start = now - timedelta(days=30)
            end = now
        elif range_type == "ytd":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            start = now - timedelta(days=1)
            end = now
        
        # Get historical data
        hist = ticker.history(start=start, end=end, interval=interval)
        
        if hist.empty:
            return f"No data available for {symbol}"
        
        # Get stock info
        info = ticker.info
        
        # Format the data
        hist.index = hist.index.tz_convert('America/New_York')
        
        # Get latest data point
        latest = hist.iloc[-1]
        first = hist.iloc[0]
        
        # Calculate change
        price_change = latest['Close'] - first['Open']
        price_change_pct = (price_change / first['Open']) * 100
        
        result = f"""
            **{symbol} - {info.get('shortName', symbol)}**

            **Latest Data ({latest.name.strftime('%Y-%m-%d %H:%M:%S %Z')})**
            - Open: ${latest['Open']:.2f}
            - High: ${latest['High']:.2f}
            - Low: ${latest['Low']:.2f}
            - Close: ${latest['Close']:.2f}
            - Volume: {int(latest['Volume']):,}

            **Period Summary ({range_type})**
            - Data Points: {len(hist)}
            - Price Change: ${price_change:.2f} ({price_change_pct:+.2f}%)
            - Period High: ${hist['High'].max():.2f}
            - Period Low: ${hist['Low'].min():.2f}
            - Avg Volume: {int(hist['Volume'].mean()):,}

            **Stock Info**
            - Exchange: {info.get('exchange', 'N/A')}
            - Currency: {info.get('currency', 'N/A')}
            - Sector: {info.get('sector', 'N/A')}
            - Industry: {info.get('industry', 'N/A')}
            """
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error in yahoo_finance_data: {e}")
        return f"Error fetching Yahoo Finance data: {str(e)}"

