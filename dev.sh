#!/usr/bin/env bash

# +-+-+-+-+-+-+-+-+-+
# FUNCTIONS
# +-+-+-+-+-+-+-+-+-+

# Startup Banner
startup_banner() {
cat << "EOF"
.____                          _________ .__           .__        
|    |   _____    ____    ____ \_   ___ \|  |__ _____  |__| ____  
|    |   \__  \  /    \  / ___\/    \  \/|  |  \\__  \ |  |/    \ 
|    |___ / __ \|   |  \/ /_/  >     \___|   Y  \/ __ \|  |   |  \
|_______ (____  /___|  /\___  / \______  /___|  (____  /__|___|  /
        \/    \/     \//_____/         \/     \/     \/        \/ 

EOF
}

# Function to clear local environment
clear_local() {
    docker compose down
    docker volume rm langchain-dev-template_weaviate_data
}

# Function to set the local .env with
# the proper OpenAI API Key
save_env_file() {
    echo "Enter in your OpenAI API Key: "
    read key
    echo "OPENAI_API_KEY=$key" > .env
}

# +-+-+-+-+-+-+-+-+-+
# Defaults
# +-+-+-+-+-+-+-+-+-+
export PYTHONDEVMODE=1

# +-+-+-+-+-+-+-+-+-+
# OPTIONS
# +-+-+-+-+-+-+-+-+-+
case $1 in
install)
    startup_banner
    save_env_file
    clear_local
    docker compose build
    echo "Install complete, run ./dev.sh start to start the environment"
    ;;
start)
    startup_banner
    docker compose up
    ;;
stop)
    docker compose down
    ;;
build)
    startup_banner
    docker compose build
    ;;
terminal)
    startup_banner
    docker compose run --rm api bash
    ;;
format)
    startup_banner
    docker-compose run --rm api /bin/bash -c 'black .'
    ;;
esac
