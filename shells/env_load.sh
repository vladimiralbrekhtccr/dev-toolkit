#!/bin/bash

#---- <|.env loading|>
find_env_file() { # # Find .env file starting from current directory and going up the directory tree
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        [[ -f "$dir/.env" ]] && echo "$dir/.env" && return
        dir="$(dirname "$dir")"
    done
    [[ -f "/.env" ]] && echo "/.env"
}
ENV_FILE="$(find_env_file)"
if [[ -n "$ENV_FILE" ]]; then # Load environment variables from .env file
    set -a; source "$ENV_FILE"; set +a
    echo "Loaded environment variables from $ENV_FILE"
else
    echo "Warning: No .env file found in current directory or parent directories"
fi
# EXAMPLE="${VAR1:-${VAR2:-${VAR3:-"Default Value"}}}" # # Use VAR1, then VAR2, then VAR3, then default
# echo "EXAMPLE (multiple fallbacks): $EXAMPLE"
#---- </|.env loading|>