#!/bin/bash
# Setup script for web search and Twitter access

echo "Setting up web search access..."

# Get the Brave Search API key
read -p "Enter your Brave Search API key: " BRAVE_API_KEY

# Store the API key in OpenClaw's config
openclaw configure web.braveApiKey "$BRAVE_API_KEY"

echo "Web search configuration complete!"

echo "Setting up Twitter (X) access with Bird CLI..."

# Check if Bird CLI is installed
if command -v bird >/dev/null 2>&1; then
    echo "Bird CLI is already installed."
else
    echo "Bird CLI not found. Installing via Homebrew..."
    brew install steipete/tap/bird
fi

# Test Bird CLI authentication
echo "Testing Bird authentication..."
bird check

if [ $? -eq 0 ]; then
    echo "Bird CLI is authenticated and ready to use."
    bird whoami
else
    echo "Bird CLI needs authentication."
    echo "You have several options:"
    echo "1. Use cookies from a browser (recommended)"
    echo "   Choose from: chrome, firefox, safari, edge, brave, arc"
    read -p "Which browser do you use? " BROWSER
    
    case "$BROWSER" in
        chrome|Chrome)
            echo "Using Chrome cookies"
            bird check --cookie-source chrome
            ;;
        firefox|Firefox)
            echo "Using Firefox cookies"
            bird check --cookie-source firefox
            ;;
        safari|Safari)
            echo "Using Safari cookies"
            bird check --cookie-source safari
            ;;
        brave|Brave)
            echo "Using Brave cookies"
            bird check --cookie-source brave
            ;;
        arc|Arc)
            echo "Using Arc cookies"
            bird check --cookie-source arc
            ;;
        *)
            echo "Unknown browser. Using default cookie source."
            bird check
            ;;
    esac
    
    echo "Testing authentication again..."
    bird whoami
fi

# Create a sample usage file
cat > "/Users/karst/.openclaw/workspace/twitter_examples.md" << EOL
# Twitter (X) Usage Examples with Bird CLI

## Reading Tweets
- Read a tweet: \`bird read <url-or-id>\`
- View a thread: \`bird thread <url-or-id>\`
- See replies: \`bird replies <url-or-id>\`

## Timeline & Search
- Home timeline: \`bird home\`
- Following timeline: \`bird home --following\`
- Search tweets: \`bird search "query" -n 10\`
- User tweets: \`bird user-tweets @handle -n 20\`

## Engagement
- Follow a user: \`bird follow @handle\`
- Unfollow a user: \`bird unfollow @handle\`
- Like a tweet: \`bird like <url-or-id>\`
- Bookmark a tweet: \`bird bookmark <url-or-id>\`

## Posting
- Post a tweet: \`bird tweet "hello world"\`
- Reply to a tweet: \`bird reply <url-or-id> "nice thread!"\`
- Tweet with media: \`bird tweet "check this out" --media image.png --alt "description"\`
EOL

echo "Twitter (X) setup complete! Examples saved to /Users/karst/.openclaw/workspace/twitter_examples.md"
echo "Setup complete!"