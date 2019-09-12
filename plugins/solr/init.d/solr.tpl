#!/bin/sh
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

### BEGIN INIT INFO
# Provides:          solr
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       Controls Apache Solr as a Service
### END INIT INFO

# Example of a very simple *nix init script that delegates commands to the bin/solr script
# Typical usage is to do:
#
#   cp bin/init.d/solr /etc/init.d/solr
#   chmod 755 /etc/init.d/solr
#   chown root:root /etc/init.d/solr
#   update-rc.d solr defaults
#   update-rc.d solr enable

# Where you extracted the Solr distribution bundle
SOLR_INSTALL_DIR="{$SERVER_PATH}/solr"

if [ ! -d "$SOLR_INSTALL_DIR" ]; then
  echo "$SOLR_INSTALL_DIR not found! Please check the SOLR_INSTALL_DIR setting in your $0 script."
  exit 1
fi

# Path to an include file that defines environment specific settings to override default
# variables used by the bin/solr script. It's highly recommended to define this script so
# that you can keep the Solr binary files separated from live files (pid, logs, index data, etc)
# see bin/solr.in.sh for an example
SOLR_ENV="{$SERVER_PATH}/solr/bin/solr.in.sh"

if [ ! -f "$SOLR_ENV" ]; then
  echo "$SOLR_ENV not found! Please check the SOLR_ENV setting in your $0 script."
  exit 1
fi

# Specify the user to run Solr as; if not set, then Solr will run as root.
# Running Solr as root is not recommended for production environments
RUNAS="{$RUN_USER}"

# verify the specified run as user exists
runas_uid="`id -u "$RUNAS"`"
if [ $? -ne 0 ]; then
  echo "User $RUNAS not found! Please create the $RUNAS user before running this script."
  exit 1
fi

case "$1" in
  start|stop|restart|status)
    SOLR_CMD="$1"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit
esac

if [ -n "$RUNAS" ]; then
  su  - "$RUNAS" -c "SOLR_INCLUDE=\"$SOLR_ENV\" \"$SOLR_INSTALL_DIR/bin/solr\" $SOLR_CMD"
else
  SOLR_INCLUDE="$SOLR_ENV" "$SOLR_INSTALL_DIR/bin/solr" "$SOLR_CMD"
fi
