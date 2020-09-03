#!/bin/bash
cd /home/minion/YC/YC-docker-engine/bundles/binary-daemon
expect -c "
spawn sudo /home/minion/YC/YC-docker-engine/bundles/binary-daemon/dockerd
expect {\[sudo\] password for minion: }
send $::env(PASSWORD)\r
interact;
"
