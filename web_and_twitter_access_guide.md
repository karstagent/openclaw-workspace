# Setting Up Web Search and Twitter Access

This guide will help you set up web search capabilities and Twitter access for your autonomous OpenClaw agent.

## 1. Web Search Setup

Web search requires a Brave Search API key. Here's how to set it up:

### Option A: Run the Setup Script

```bash
# Run the automated setup script
bash /Users/karst/.openclaw/workspace/setup_brave_api.sh

# Follow the prompts to enter your API key
```

### Option B: Manual Configuration

1. Get a Brave Search API key from https://brave.com/search/api/
2. Configure OpenClaw to use your key:
   ```bash
   openclaw configure web.braveApiKey "YOUR_API_KEY_HERE"
   ```
3. Set the environment variable:
   ```bash
   export BRAVE_API_KEY="YOUR_API_KEY_HERE"
   ```
4. Restart the Gateway:
   ```bash
   openclaw gateway restart
   ```

### Testing Web Search

Once configured, you can test web search with:

```bash
openclaw eval 'web_search({ query: "OpenClaw autonomy" })'
```

## 2. Twitter (X) Access Setup

The Bird CLI is used for Twitter access. It appears to be already installed on your system.

### Checking Bird CLI Setup

```bash
# Verify Bird CLI is installed
which bird

# Check if Bird is already authenticated
bird whoami
```

### Authentication Options

Bird CLI uses browser cookies for authentication:

```bash
# Check available authentication sources
bird check

# Specify a browser cookie source
bird check --cookie-source chrome  # Options: chrome, firefox, safari, brave, arc
```

### Basic Twitter Commands

Once authenticated, you can:

- **Read tweets**: `bird read <tweet-url-or-id>`
- **View home timeline**: `bird home`
- **Search tweets**: `bird search "query" -n 10`
- **Post a tweet**: `bird tweet "Hello world!"`

See `/Users/karst/.openclaw/workspace/twitter_examples.md` for more examples.

## Autonomous Setup

Once configured, your autonomous agent will be able to:

1. Search the web for current information
2. Monitor Twitter for mentions and relevant content
3. Post updates to Twitter when instructed

For autonomous operation, both the Brave API key and Twitter authentication need to be properly configured.

## Troubleshooting

### Web Search Issues

- Ensure your Brave API key is valid
- Check if the Gateway is running: `openclaw gateway status`
- Restart the Gateway: `openclaw gateway restart`

### Twitter Access Issues

- Make sure you're logged into Twitter in your browser
- Try different cookie sources: `bird check --cookie-source chrome`
- For Arc/Brave browsers, you may need to specify: `bird check --chrome-profile-dir <path>`
- Refresh query IDs if getting 404 errors: `bird query-ids --fresh`

## Maintenance

Both web search and Twitter access are dependent on external services that may change over time. Regular maintenance checks are recommended:

```bash
# Schedule a weekly check job
openclaw cron add \
  --name "API Health Check" \
  --cron "0 9 * * MON" \
  --session isolated \
  --message "Check if web search and Twitter access are still working properly. Test web_search and bird commands, and report any issues."
```