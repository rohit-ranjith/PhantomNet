#!/bin/bash

AZURE_USER="azureuser"
AZURE_IP="azure vm public ip"
AZURE_DIR="/home/azureuser/cowrie_snapshots/"
LOCAL_DIR="$HOME/phantomnet/data/raw/cowrie_snapshots/"

mkdir -p "$LOCAL_DIR"

rsync -av -e "ssh -p 22222" \
  ${AZURE_USER}@${AZURE_IP}:${AZURE_DIR} \
  "$LOCAL_DIR"
