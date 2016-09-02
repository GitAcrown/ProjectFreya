@Echo off
chcp 65001
:Start

python core.py
timeout 3

goto Start