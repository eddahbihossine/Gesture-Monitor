#!bin/zsh
rm -rf env/ venv/

python3.11 -m venv env 
source env/bin/activate
python3.11 -m pip install -r requirements.txt 
pip install --upgrade pip

python3.11 script.py