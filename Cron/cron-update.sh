#!/bin/bash

VIRTUAL_ENV="/home/redteam/gvm/gvm"
SCRIPT_PATH="/home/redteam/gvm/Update/update.py"

source "$VIRTUAL_ENV/bin/activate"
sudo python3 "$SCRIPT_PATH"

deactivate