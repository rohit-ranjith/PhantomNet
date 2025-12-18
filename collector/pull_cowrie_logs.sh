#!/bin/bash

AZURE_USER=azureuser
AZURE_IP=20.92.166.67
REMOTE_DIR=~/cowrie_snapshots
LOCAL_DIR=~/phantomnet/data/raw/cowrie_snapshots

mkdir -p "$LOCAL_DIR"

rsync -az --ignore-existing \
  ${AZURE_USER}@${AZURE_IP}:${REMOTE_DIR}/ \
  ${LOCAL_DIR}/
