# TradeMaster AI Bot - Deployment Instructions

## 🚀 Deployment Configuration

### Environment Variables Required:
- `TELEGRAM_API_TOKEN` - Your Telegram Bot Token
- `OPENAI_API_KEY` - Your OpenAI API Key

### Optional Environment Variables:
- `DEPLOYMENT_MODE=true` - Enable lightweight deployment mode
- `PORT=5000` - Port for health check (optional for background workers)

### Run Command:
```
python main.py
```

### Deployment Type:
**Background Worker** - The bot runs continuously without a web interface

### Important Notes:

1. **Size Optimization**: The project includes a `.dockerignore` file to exclude unnecessary files during deployment

2. **Lightweight Mode**: The bot automatically detects deployment and runs with minimal dependencies

3. **Features Available**:
   - ✅ All Telegram commands (/price, /analyze, /portfolio, /watchlist, etc.)
   - ✅ AI-powered analysis via OpenAI
   - ✅ Real-time market data
   - ✅ Portfolio and trade tracking
   - ✅ Watchlist management

4. **Dependencies**: The bot uses fallback services that don't require heavy ML libraries

### Deployment Steps:

1. Click **Deploy** in Replit
2. Select **Background Worker**
3. Enter run command: `python main.py`
4. Make sure environment variables are set in Secrets
5. Deploy!

### Troubleshooting:

If deployment fails due to size:
- The project uses `.dockerignore` to exclude large files
- Background workers have more lenient size limits than web services
- Contact Replit support if size issues persist

The bot is optimized for deployment and will run efficiently as a background worker!