#!/bin/bash

VIRTUAL_ENV="/home/redteam/gvm/gvm"
SCRIPT_PATH="/home/redteam/gvm/Targets_Tasks/run-task.py"

source "$VIRTUAL_ENV/bin/activate"
python3 "$SCRIPT_PATH"

deactivate