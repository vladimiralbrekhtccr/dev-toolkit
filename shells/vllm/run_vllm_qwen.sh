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


export CUDA_VISIBLE_DEVICES=1
MODEL="${vLLM_PATH_QWEN:-"path_to_qwen_model"}"
SERVER_NAME="${QWEN_MODEL_PATH:-"qwen_server"}"
echo "SERVER_NAME: $SERVER_NAME"
PORT="${vLLM_PORT:-7050}"
HOST="${vLLM_HOST:-"0.0.0.0"}"
SEED=0

# vLLM configuration parameters
GPU_MEMORY_UTILIZATION=0.83 # max memory utilization of VRAM if 1.0 then 100% of VRAM will be used and might cause OOM
MAX_NUM_BATCHED_TOKENS=5000 # max number of tokens in the batch
MAX_MODEL_LEN=5000 # max length of the generated text
if [[ "$MODEL" == *"gemma"* ]]; then
    DTYPE="bfloat16"
else
    DTYPE="auto"
fi
TENSOR_PARALLEL_SIZE=1 # amount of GPUs
BLOCK_SIZE=32
KV_CACHE_DTYPE="auto"
SWAP_SPACE=4 
MAX_NUM_SEQS=4 # max number of requests
# Construct the vLLM command
CMD="vllm serve $MODEL \
  --host $HOST \
  --port $PORT \
  --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
  --max-num-batched-tokens $MAX_NUM_BATCHED_TOKENS \
  --max-model-len $MAX_MODEL_LEN \
  --served-model-name $SERVER_NAME \
  --trust-remote-code \
  --dtype $DTYPE \
  --tensor-parallel-size $TENSOR_PARALLEL_SIZE \
  --swap-space $SWAP_SPACE \
  --block-size $BLOCK_SIZE \
  --kv-cache-dtype $KV_CACHE_DTYPE \
  --max-num-seqs $MAX_NUM_SEQS \
  --seed $SEED"

# Execute the command
eval $CMD