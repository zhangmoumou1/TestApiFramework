#!/bin/bash
#@@Author: 张某某
#@@Create Date: 2023/02/16 10:28
#@@Description: windows系统执行脚本
#@@Copyright © zhangmoumou, Inc. All rights reserved.

#用法：./run.sh TEST

python3 ./load_config.py $1
python3 -m pytest
echo ###################写入%1环境，执行pytest命令，运行用例结束###################