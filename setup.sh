#!/bin/bash

# 🤖 Robot Sender - Automated Setup Script (Linux/macOS)

# Colors for output
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}   Welcome to Robot Sender Setup        ${NC}"
echo -e "${CYAN}==========================================${NC}"

# 1. Gather User Input
echo -e "\n${YELLOW}[1/3] Platform Configuration${NC}"
read -p "Enter SOURCE platform (soroush, telegram, bale, rubika, eitaa): " source
read -p "Enter TARGET platforms (comma separated, e.g: telegram,eitaa,bale): " targets_raw

# Get Source details
read -p "Enter Source Channel ID: " source_id

# Function to get credentials
get_creds() {
    local platform=$1
    echo -e "\n${GREEN}--- Configuration for [$platform] ---${NC}"
    case $platform in
        soroush)
            read -p "Enter Soroush Bot Token: " token
            echo "$token"
            ;;
        telegram)
            read -p "Enter Telegram Bot Token: " token
            echo "$token"
            ;;
        eitaa)
            read -p "Enter Eitaayar API Token: " token
            echo "$token"
            ;;
        rubika)
            read -p "Enter Rubika Bot Token: " token
            echo "$token"
            ;;
        bale)
            read -p "Enter Bale Bot Token: " token
            echo "$token"
            ;;
    esac
}

# Credentials gathering
source_token=$(get_creds "$source")

# Target mapping
IFS=',' read -ra ADDR <<< "$targets_raw"
target_mapping=""
credentials_json="\"$source\": {\"token\": \"$source_token\"}"

for t in "${ADDR[@]}"; do
    t=$(echo "$t" | xargs) # trim
    read -p "Enter Channel ID for Target [$t]: " t_id
    
    if [[ -z "$target_mapping" ]]; then
        target_mapping="\"$t\": \"$t_id\""
    else
        target_mapping="$target_mapping, \"$t\": \"$t_id\""
    fi

    # Check if we already got creds for this platform (if it was the source)
    if [[ "$t" != "$source" ]]; then
        t_token=$(get_creds "$t")
        credentials_json="$credentials_json, \"$t\": {\"token\": \"$t_token\"}"
    fi
done

# 2. Generate config.json
echo -e "\n${YELLOW}[2/3] Generating Configuration...${NC}"

cat <<EOF > config.json
{
  "source": "$source",
  "source_channel_id": "$source_id",
  "interval": 60,
  "targets": {
    $target_mapping
  },
  "credentials": {
    $credentials_json
  }
}
EOF

# 3. Finalize
echo -e "\n${YELLOW}[3/3] Setup Complete!${NC}"
echo -e "${GREEN}All files have been generated and configured.${NC}"

read -p "Do you want to run the system now via Docker? (y/n): " run_now
if [[ "$run_now" == "y" ]]; then
    echo -e "${CYAN}Launching Docker Compose...${NC}"
    docker-compose up -d --build
    echo -e "${GREEN}System is running in background!${NC}"
    echo -e "Use 'docker-compose logs -f app' to see live logs."
else
    echo -e "${WHITE}You can start the system later by running: docker-compose up -d${NC}"
fi

echo -e "\nSetup finished."
