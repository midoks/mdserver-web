#!/bin/bash

# 测试 Apache 安装脚本
cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/apache/versions/2.4
echo "Running Apache install script..."
# 直接运行脚本，不使用 trae-sandbox
./install.sh upgrade

echo "Installation completed with exit code: $?"
