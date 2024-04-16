@REM @@Author: 张某某
@REM @@Create Date: 2023/02/16 10:28
@REM @@Description: windows系统执行脚本
@REM @@Copyright © zhangmoumou, Inc. All rights reserved.

@REM 用法：.\run.bat TEST

@echo off
chcp 65001
python .\load_config.py %1
pytest
echo ###################写入%1环境，执行pytest命令，运行用例结束###################