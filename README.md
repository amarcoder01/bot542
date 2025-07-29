# TradeAI Telegram Bot

Advanced AI-powered Telegram trading bot with comprehensive market analysis and intelligent trading capabilities.

## Features

🤖 **AI-Powered Analysis**: Leverages OpenAI for intelligent market insights
📊 **Real-time Market Data**: Get current stock prices and market information  
📈 **Technical Analysis**: Advanced indicators and trend analysis
💹 **Portfolio Tracking**: Monitor your investments and performance
🚨 **Price Alerts**: Set custom alerts for your favorite stocks
🔒 **Secure & Reliable**: Built with security best practices

## Quick Start

### 1. Environment Setup

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `TELEGRAM_API_TOKEN`: Get from [@BotFather](https://t.me/botfather)
- `OPENAI_API_KEY`: Get from [OpenAI Platform](https://platform.openai.com/)

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python simple_telegram_bot.py
```

### 3. Deployment

The bot is configured for easy deployment on platforms like Render, Railway, or Heroku.

#### Render Deployment
1. Fork this repository
2. Create a new Web Service on Render
3. Connect your repository
4. Add environment variables in Render dashboard
5. Deploy!

#### Required Environment Variables
- `TELEGRAM_API_TOKEN` - Your Telegram bot token
- `OPENAI_API_KEY` - Your OpenAI API key
- `PORT` - Port for health checks (default: 8080)

## Bot Commands

### Basic Commands
- `/start` - Welcome message and bot introduction
- `/help` - Show all available commands
- `/status` - Check bot status and uptime

### Trading Commands
- `/price SYMBOL` - Get current stock price (e.g., `/price AAPL`)
- `/analyze SYMBOL` - AI-powered stock analysis (e.g., `/analyze TSLA`)
- `/market` - Overall market status and indices

### Example Usage
```
/price AAPL
📊 AAPL Stock Price
💰 Current: $150.25
📈 Change: +$2.15 (+1.45%)

/analyze TSLA
📈 TSLA Analysis
🎯 Technical Indicators:
• Trend: Bullish
• RSI: 65 (Neutral)
💡 AI Insight: Strong momentum detected...
```

## Architecture

### Core Components
- **simple_telegram_bot.py**: Main bot implementation
- **deploy_config.py**: Deployment configuration
- **deploy/**: Advanced features and services

### Tech Stack
- **Python 3.11+**: Core language
- **python-telegram-bot**: Telegram Bot API wrapper
- **aiohttp**: Async web framework for health checks
- **OpenAI**: AI-powered market analysis
- **asyncio**: Asynchronous programming

### Deployment Files
- `Procfile`: Process configuration for deployment
- `runtime.txt`: Python version specification
- `.env.example`: Environment variables template

## Health Monitoring

The bot includes built-in health check endpoints:
- `GET /` - Basic status check
- `GET /health` - Detailed health information

## Security Features

- Environment variable validation
- Secure API key handling
- Error handling and logging
- Rate limiting protection

## Development

### Project Structure
```
├── simple_telegram_bot.py    # Main bot implementation
├── deploy_config.py          # Configuration management
├── deploy/                   # Advanced features
├── .env.example             # Environment template
├── Procfile                 # Deployment config
├── runtime.txt              # Python version
└── README.md               # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure API keys are valid and have proper permissions
4. Check network connectivity

## License

This project is licensed under the MIT License.