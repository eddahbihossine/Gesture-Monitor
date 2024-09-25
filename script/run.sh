#!bin/zsh
# rm -rf env/ venv/

python3.9 -m venv env 
source env/bin/activate
pip install --upgrade pip
python -m pip install -r requirements.txt 

python script.py