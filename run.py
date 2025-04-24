import subprocess
import os

os.chdir("code")
subprocess.run(["streamlit", "run", "menu.py"])
