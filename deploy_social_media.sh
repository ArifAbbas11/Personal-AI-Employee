#!/bin/bash
# Automated Social Media Deployment Script
# Guides through social media platform setup and credential configuration

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONFIG_FILE="AI_Employee_Vault/Config/social_media_config.json"
CONFIG_TEMPLATE="AI_Employee_Vault/Config/social_media_config.json.template"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Social Media Automated Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to open URL in browser
open_url() {
    local url=$1
    if command_exists xdg-open; then
        xdg-open "$url" 2>/dev/null
    elif command_exists open; then
        open "$url" 2>/dev/null
    else
        echo "Please open this URL in your browser: $url"
    fi
}

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites${NC}"
echo "-----------------------------------"

if ! command_exists python3; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 installed${NC}"

# Check for required Python packages
if python3 -c "import requests" 2>/dev/null; then
    echo -e "${GREEN}✓ requests package installed${NC}"
else
    echo -e "${YELLOW}⚠ requests package not found${NC}"
    echo "Installing requests..."
    pip3 install requests
fi

echo ""

# Step 2: Platform selection
echo -e "${BLUE}Step 2: Select platforms to configure${NC}"
echo "-----------------------------------"
echo ""
echo "Which platforms do you want to configure?"
echo "1. Facebook"
echo "2. Instagram"
echo "3. Twitter"
echo "4. LinkedIn"
echo "5. All platforms"
echo ""
read -p "Enter your choice (1-5): " PLATFORM_CHOICE

CONFIGURE_FACEBOOK=false
CONFIGURE_INSTAGRAM=false
CONFIGURE_TWITTER=false
CONFIGURE_LINKEDIN=false

case $PLATFORM_CHOICE in
    1) CONFIGURE_FACEBOOK=true ;;
    2) CONFIGURE_INSTAGRAM=true ;;
    3) CONFIGURE_TWITTER=true ;;
    4) CONFIGURE_LINKEDIN=true ;;
    5)
        CONFIGURE_FACEBOOK=true
        CONFIGURE_INSTAGRAM=true
        CONFIGURE_TWITTER=true
        CONFIGURE_LINKEDIN=true
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""

# Initialize config object
CONFIG_JSON='{'

# Step 3: Facebook Configuration
if [ "$CONFIGURE_FACEBOOK" = true ]; then
    echo -e "${BLUE}Step 3a: Facebook Configuration${NC}"
    echo "-----------------------------------"
    echo ""
    echo "To configure Facebook, you need:"
    echo "1. A Facebook Developer account"
    echo "2. A Facebook App"
    echo "3. App ID and App Secret"
    echo "4. Access Token"
    echo ""
    echo "Opening Facebook Developers portal..."
    open_url "https://developers.facebook.com/apps"
    echo ""
    echo "Steps to get credentials:"
    echo "1. Create a new app (or select existing)"
    echo "2. Go to Settings > Basic"
    echo "3. Copy App ID and App Secret"
    echo "4. Go to Tools > Graph API Explorer"
    echo "5. Generate an access token with required permissions:"
    echo "   - pages_manage_posts"
    echo "   - pages_read_engagement"
    echo "   - pages_show_list"
    echo ""
    read -p "Press Enter when you have your credentials ready..."
    echo ""

    read -p "Facebook App ID: " FB_APP_ID
    read -p "Facebook App Secret: " FB_APP_SECRET
    read -p "Facebook Access Token: " FB_ACCESS_TOKEN

    CONFIG_JSON+="\"facebook\": {\"app_id\": \"$FB_APP_ID\", \"app_secret\": \"$FB_APP_SECRET\", \"access_token\": \"$FB_ACCESS_TOKEN\"}"

    echo -e "${GREEN}✓ Facebook configured${NC}"
    echo ""
fi

# Step 4: Instagram Configuration
if [ "$CONFIGURE_INSTAGRAM" = true ]; then
    echo -e "${BLUE}Step 3b: Instagram Configuration${NC}"
    echo "-----------------------------------"
    echo ""
    echo "To configure Instagram, you need:"
    echo "1. An Instagram Business account"
    echo "2. A Facebook App with Instagram Basic Display"
    echo "3. App ID and App Secret"
    echo "4. Access Token"
    echo ""
    echo "Opening Facebook Developers portal..."
    open_url "https://developers.facebook.com/apps"
    echo ""
    echo "Steps to get credentials:"
    echo "1. Use the same Facebook App (or create new)"
    echo "2. Add Instagram Basic Display product"
    echo "3. Configure Instagram Basic Display"
    echo "4. Generate access token"
    echo ""
    read -p "Press Enter when you have your credentials ready..."
    echo ""

    read -p "Instagram App ID: " IG_APP_ID
    read -p "Instagram App Secret: " IG_APP_SECRET
    read -p "Instagram Access Token: " IG_ACCESS_TOKEN

    if [ ${#CONFIG_JSON} -gt 1 ]; then
        CONFIG_JSON+=","
    fi
    CONFIG_JSON+="\"instagram\": {\"app_id\": \"$IG_APP_ID\", \"app_secret\": \"$IG_APP_SECRET\", \"access_token\": \"$IG_ACCESS_TOKEN\"}"

    echo -e "${GREEN}✓ Instagram configured${NC}"
    echo ""
fi

# Step 5: Twitter Configuration
if [ "$CONFIGURE_TWITTER" = true ]; then
    echo -e "${BLUE}Step 3c: Twitter Configuration${NC}"
    echo "-----------------------------------"
    echo ""
    echo "To configure Twitter, you need:"
    echo "1. A Twitter Developer account"
    echo "2. A Twitter App"
    echo "3. API Key, API Secret, Access Token, Access Token Secret"
    echo ""
    echo "Opening Twitter Developer portal..."
    open_url "https://developer.twitter.com/en/portal/dashboard"
    echo ""
    echo "Steps to get credentials:"
    echo "1. Create a new app (or select existing)"
    echo "2. Go to Keys and Tokens"
    echo "3. Copy API Key and API Secret"
    echo "4. Generate Access Token and Secret"
    echo "5. Ensure app has Read and Write permissions"
    echo ""
    read -p "Press Enter when you have your credentials ready..."
    echo ""

    read -p "Twitter API Key: " TW_API_KEY
    read -p "Twitter API Secret: " TW_API_SECRET
    read -p "Twitter Access Token: " TW_ACCESS_TOKEN
    read -p "Twitter Access Token Secret: " TW_ACCESS_SECRET

    if [ ${#CONFIG_JSON} -gt 1 ]; then
        CONFIG_JSON+=","
    fi
    CONFIG_JSON+="\"twitter\": {\"api_key\": \"$TW_API_KEY\", \"api_secret\": \"$TW_API_SECRET\", \"access_token\": \"$TW_ACCESS_TOKEN\", \"access_token_secret\": \"$TW_ACCESS_SECRET\"}"

    echo -e "${GREEN}✓ Twitter configured${NC}"
    echo ""
fi

# Step 6: LinkedIn Configuration
if [ "$CONFIGURE_LINKEDIN" = true ]; then
    echo -e "${BLUE}Step 3d: LinkedIn Configuration${NC}"
    echo "-----------------------------------"
    echo ""
    echo "To configure LinkedIn, you need:"
    echo "1. A LinkedIn Developer account"
    echo "2. A LinkedIn App"
    echo "3. Client ID, Client Secret, Access Token"
    echo ""
    echo "Opening LinkedIn Developers portal..."
    open_url "https://www.linkedin.com/developers/apps"
    echo ""
    echo "Steps to get credentials:"
    echo "1. Create a new app (or select existing)"
    echo "2. Go to Auth tab"
    echo "3. Copy Client ID and Client Secret"
    echo "4. Request access to required products:"
    echo "   - Share on LinkedIn"
    echo "   - Sign In with LinkedIn"
    echo "5. Generate access token using OAuth 2.0"
    echo ""
    read -p "Press Enter when you have your credentials ready..."
    echo ""

    read -p "LinkedIn Client ID: " LI_CLIENT_ID
    read -p "LinkedIn Client Secret: " LI_CLIENT_SECRET
    read -p "LinkedIn Access Token: " LI_ACCESS_TOKEN

    if [ ${#CONFIG_JSON} -gt 1 ]; then
        CONFIG_JSON+=","
    fi
    CONFIG_JSON+="\"linkedin\": {\"client_id\": \"$LI_CLIENT_ID\", \"client_secret\": \"$LI_CLIENT_SECRET\", \"access_token\": \"$LI_ACCESS_TOKEN\"}"

    echo -e "${GREEN}✓ LinkedIn configured${NC}"
    echo ""
fi

# Close JSON object
CONFIG_JSON+='}'

# Step 7: Create configuration file
echo -e "${BLUE}Step 4: Creating configuration file${NC}"
echo "-----------------------------------"

# Ensure config directory exists
mkdir -p "$(dirname "$CONFIG_FILE")"

# Check if config file already exists
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}⚠ Configuration file already exists${NC}"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Keeping existing configuration${NC}"
        exit 0
    fi
fi

# Write configuration file
echo "$CONFIG_JSON" | python3 -m json.tool > "$CONFIG_FILE"
chmod 600 "$CONFIG_FILE"

echo -e "${GREEN}✓ Configuration file created: $CONFIG_FILE${NC}"
echo ""

# Step 8: Test connections
echo -e "${BLUE}Step 5: Testing connections${NC}"
echo "-----------------------------------"

if [ "$CONFIGURE_FACEBOOK" = true ]; then
    echo "Testing Facebook connection..."
    if python3 watchers/social_media_mcp_server.py --test facebook 2>/dev/null; then
        echo -e "${GREEN}✓ Facebook connection successful${NC}"
    else
        echo -e "${RED}✗ Facebook connection failed${NC}"
    fi
fi

if [ "$CONFIGURE_INSTAGRAM" = true ]; then
    echo "Testing Instagram connection..."
    if python3 watchers/social_media_mcp_server.py --test instagram 2>/dev/null; then
        echo -e "${GREEN}✓ Instagram connection successful${NC}"
    else
        echo -e "${RED}✗ Instagram connection failed${NC}"
    fi
fi

if [ "$CONFIGURE_TWITTER" = true ]; then
    echo "Testing Twitter connection..."
    if python3 watchers/social_media_mcp_server.py --test twitter 2>/dev/null; then
        echo -e "${GREEN}✓ Twitter connection successful${NC}"
    else
        echo -e "${RED}✗ Twitter connection failed${NC}"
    fi
fi

if [ "$CONFIGURE_LINKEDIN" = true ]; then
    echo "Testing LinkedIn connection..."
    if python3 watchers/social_media_mcp_server.py --test linkedin 2>/dev/null; then
        echo -e "${GREEN}✓ LinkedIn connection successful${NC}"
    else
        echo -e "${RED}✗ LinkedIn connection failed${NC}"
    fi
fi

echo ""

# Step 9: Test posting
echo -e "${BLUE}Step 6: Test posting (optional)${NC}"
echo "-----------------------------------"
echo ""
read -p "Would you like to create a test post? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Select platform for test post:"
    if [ "$CONFIGURE_FACEBOOK" = true ]; then echo "1. Facebook"; fi
    if [ "$CONFIGURE_INSTAGRAM" = true ]; then echo "2. Instagram"; fi
    if [ "$CONFIGURE_TWITTER" = true ]; then echo "3. Twitter"; fi
    if [ "$CONFIGURE_LINKEDIN" = true ]; then echo "4. LinkedIn"; fi
    echo ""
    read -p "Enter choice: " TEST_PLATFORM_CHOICE

    case $TEST_PLATFORM_CHOICE in
        1) TEST_PLATFORM="facebook" ;;
        2) TEST_PLATFORM="instagram" ;;
        3) TEST_PLATFORM="twitter" ;;
        4) TEST_PLATFORM="linkedin" ;;
        *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
    esac

    echo ""
    read -p "Enter test post content: " TEST_CONTENT

    python3 -c "
from watchers.social_media_mcp_server import SocialMediaMCPServer
server = SocialMediaMCPServer()
result = server.post_to_platform('$TEST_PLATFORM', '$TEST_CONTENT')
print('Post result:', result)
"

    echo -e "${GREEN}✓ Test post created${NC}"
fi

echo ""

# Step 10: Start scheduler
echo -e "${BLUE}Step 7: Start scheduler (optional)${NC}"
echo "-----------------------------------"
echo ""
read -p "Would you like to start the content scheduler? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting scheduler daemon..."
    python3 watchers/social_media_scheduler.py --daemon &
    SCHEDULER_PID=$!
    echo -e "${GREEN}✓ Scheduler started (PID: $SCHEDULER_PID)${NC}"
    echo ""
    echo "To monitor scheduler:"
    echo "  tail -f AI_Employee_Vault/Logs/social_media_scheduler.log"
    echo ""
    echo "To stop scheduler:"
    echo "  kill $SCHEDULER_PID"
fi

echo ""

# Step 11: Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Social Media Deployment Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Social media platforms configured!"
echo ""
echo "Configured platforms:"
if [ "$CONFIGURE_FACEBOOK" = true ]; then echo "  ✓ Facebook"; fi
if [ "$CONFIGURE_INSTAGRAM" = true ]; then echo "  ✓ Instagram"; fi
if [ "$CONFIGURE_TWITTER" = true ]; then echo "  ✓ Twitter"; fi
if [ "$CONFIGURE_LINKEDIN" = true ]; then echo "  ✓ LinkedIn"; fi
echo ""
echo "Configuration:"
echo "  File: $CONFIG_FILE"
echo ""
echo "Next steps:"
echo ""
echo "1. Post to a platform:"
echo "   python3 -c 'from watchers.social_media_mcp_server import SocialMediaMCPServer; server = SocialMediaMCPServer(); print(server.post_to_platform(\"facebook\", \"Hello from AI Employee!\"))'"
echo ""
echo "2. Schedule a post:"
echo "   python3 -c 'from watchers.social_media_mcp_server import SocialMediaMCPServer; server = SocialMediaMCPServer(); print(server.schedule_post(\"linkedin\", \"Scheduled post\", \"2026-02-28T10:00:00\"))'"
echo ""
echo "3. Get platform stats:"
echo "   python3 -c 'from watchers.social_media_mcp_server import SocialMediaMCPServer; server = SocialMediaMCPServer(); print(server.get_platform_stats(\"twitter\"))'"
echo ""
echo "4. Start scheduler daemon:"
echo "   python3 watchers/social_media_scheduler.py --daemon"
echo ""
echo "5. Generate CEO Briefing (will include social media metrics):"
echo "   python3 watchers/simple_ceo_briefing.py"
echo ""
