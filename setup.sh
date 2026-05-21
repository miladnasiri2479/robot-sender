#!/bin/bash

# 🤖 Robot Sender - Automated Setup Script (Linux/macOS)

# Colors for output
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
GRAY='\033[0;90m'
WHITE='\033[1;37m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_header() {
    clear
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${CYAN}   Welcome to Robot Sender Setup        ${NC}"
    echo -e "${CYAN}==========================================${NC}"
}

platforms=("telegram" "bale" "eitaa" "rubika" "soroush")

declare -A examples
examples["telegram"]="@channelname (Public) or -100xxxx (Private)"
examples["bale"]="cxxxx (Example: c0221345678)"
examples["eitaa"]="@channelname"
examples["rubika"]="@channelname or cxxxx"
examples["soroush"]="channel_id"

declare -A token_names
token_names["telegram"]="Bot Token (from @BotFather)"
token_names["bale"]="Bot Token (from @BotFather)"
token_names["eitaa"]="Eitaayar API Token (from eitaayar.ir)"
token_names["rubika"]="Bot Token (from @BotFather)"
token_names["soroush"]="Bot Token (from @mrbot)"

get_platform_selection() {
    local title=$1
    echo -e "\n${GRAY}$title${NC}"
    for i in "${!platforms[@]}"; do
        echo "  $((i + 1)). ${platforms[$i]}"
    done
    
    local choice=-1
    while (( choice < 1 || choice > ${#platforms[@]} )); do
        read -p "Select a platform (1-${#platforms[@]}): " input
        if [[ "$input" =~ ^[0-9]+$ ]]; then
            choice=$input
            if (( choice < 1 || choice > ${#platforms[@]} )); then
                echo -e "${RED}Invalid choice.${NC}"
            fi
        else
            echo -e "${RED}Please enter a number.${NC}"
        fi
    done
    echo "${platforms[$((choice - 1))]}"
}

show_header

# 1. Source Configuration
echo -e "\n${YELLOW}[1/3] Source Configuration (Where to read from)${NC}"
source_platform=$(get_platform_selection "Select the SOURCE platform:")

echo -e "\n${GREEN}Configuring $source_platform as source...${NC}"
source_example=${examples[$source_platform]}
read -p "Enter Source Channel ID (Example: $source_example): " source_id

echo -e "\n${GRAY}--- Why is a token needed? ---${NC}"
echo -e "${GRAY}To read messages from $source_platform, the bot must be an administrator in the channel.${NC}"
source_token_name=${token_names[$source_platform]}
read -p "Enter $source_token_name: " source_token

# Initialize JSON fragments
credentials_json="\"$source_platform\": {\"token\": \"$source_token\"}"
target_mapping_json=""

# 2. Target Configuration
echo -e "\n${YELLOW}[2/3] Target Configuration (Where to send to)${NC}"
add_more="y"
while [[ "$add_more" == "y" ]]; do
    target_platform=$(get_platform_selection "Select a TARGET platform:")

    target_example=${examples[$target_platform]}
    read -p "Enter Channel ID for Target [$target_platform] (Example: $target_example): " target_id
    
    if [[ -z "$target_mapping_json" ]]; then
        target_mapping_json="\"$target_platform\": \"$target_id\""
    else
        target_mapping_json="$target_mapping_json, \"$target_platform\": \"$target_id\""
    fi

    # Check if we already got creds for this platform
    if [[ "$target_platform" != "$source_platform" ]]; then
        target_token_name=${token_names[$target_platform]}
        read -p "Enter $target_token_name: " target_token
        credentials_json="$credentials_json, \"$target_platform\": {\"token\": \"$target_token\"}"
    fi

    read -p "$(echo -e "\nDo you want to add another target platform? (y/n): ")" add_more
    add_more=$(echo "$add_more" | tr '[:upper:]' '[:lower:]')
done

# 3. Global Settings
echo -e "\n${YELLOW}[3/3] Global Settings${NC}"
read -p "Enter sync interval in seconds (Default: 60): " interval
if [[ -z "$interval" ]]; then interval=60; fi

# 4. Generate config.json
echo -e "\n${YELLOW}Generating Configuration...${NC}"

cat <<EOF > config.json
{
  "source": "$source_platform",
  "source_channel_id": "$source_id",
  "interval": $interval,
  "targets": {
    $target_mapping_json
  },
  "credentials": {
    $credentials_json
  }
}
EOF

# 5. Finalize
echo -e "\n${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}The 'config.json' file has been created successfully.${NC}"

read -p "$(echo -e "\nDo you want to run the system now via Docker? (y/n): ")" run_now
run_now=$(echo "$run_now" | tr '[:upper:]' '[:lower:]')
if [[ "$run_now" == "y" ]]; then
    echo -e "${CYAN}Launching Docker Compose...${NC}"
    docker-compose up -d --build
    echo -e "${GREEN}System is running in background!${NC}"
    echo -e "Use 'docker-compose logs -f app' to see live logs."
else
    echo -e "${WHITE}You can start the system later by running: docker-compose up -d${NC}"
fi

echo -e "\nSetup finished."
