#!/bin/bash

# This script is used to test the program during development. 
# usage : ./scripts/install.sh

echo "[+] Deleting older sources..."
rm -rf "`pip3 show kharma| grep "Location: *"|sed "s/Location: //g"`/kharma"
echo "[+] Uninstalling previous versions of kharma..."
yes | pip3 uninstall kharma
echo "[+] Deleting older wheels..."
rm dist/*
echo "[+] Building..."
poetry build
echo "[+] Installing kharma..."
find ./dist -name 'kharma-*.*.*.whl' -exec pip3 install {} \;
echo "[+] Installation completed"