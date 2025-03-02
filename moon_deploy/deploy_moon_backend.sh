#!/bin/bash

#set -ex
set -e

./deploy_event-pump.sh
sleep 5

./deploy_user-vault.sh
sleep 3

./deploy_gatekeeper.sh
./deploy_acct.sh
./deploy_logbot.sh
./deploy_mini-fstore.sh
./deploy_vfm.sh
./deploy_drone.sh