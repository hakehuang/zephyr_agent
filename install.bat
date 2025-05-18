@echo off
rem 安装uv并设置虚拟环境
python -m pip install --user pipx
python -m pipx ensurepath
pipx install uv
uv venv .venv
call .venv\Scripts\activate
uv pip install -r requirements.txt