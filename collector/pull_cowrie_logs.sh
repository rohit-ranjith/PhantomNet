#!/bin/bash

AZURE_USER="azureuser"
AZURE_IP="130.33.97.184"
AZURE_DIR="/home/azureuser/cowrie_snapshots/"
LOCAL_DIR="$HOME/phantomnet/data/raw/cowrie_snapshots/"

mkdir -p "$LOCAL_DIR"

rsync -avz --ignore-existing \
  ${AZURE_USER}@${AZURE_IP}:${AZURE_DIR} \
  "$LOCAL_DIR"