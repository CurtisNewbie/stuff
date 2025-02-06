#!/bin/bash

#set -ex
set -e

./deploy_acct.sh
./deploy_event-pump.sh
./deploy_gatekeeper.sh
./deploy_logbot.sh
./deploy_mini-fstore.sh
./deploy_user-vault.sh
./deploy_vfm.sh