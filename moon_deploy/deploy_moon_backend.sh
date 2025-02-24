#!/bin/bash

#set -ex
set -e

./deploy_event-pump.sh

echo "Wait 5s for event-pump"
sleep 5

./deploy_acct.sh
./deploy_gatekeeper.sh
./deploy_logbot.sh
./deploy_mini-fstore.sh
./deploy_user-vault.sh
./deploy_vfm.sh