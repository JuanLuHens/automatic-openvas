#!/bin/bash

VIRTUAL_ENV="/home/redteam/gvm/gvm"
SCRIPT_PATH="/home/redteam/gvm/Update/update-script.py"

source "$VIRTUAL_ENV/bin/activate"
python3 "$SCRIPT_PATH"
rm "/home/redteam/gvm/tasksend.txt"
deactivate
