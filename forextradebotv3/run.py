import subprocess

venv_python = r'.venv\Scripts\python.exe'

# Start the first program
p1 = subprocess.Popen([venv_python, "forextradebotv3\TradingB_FrontEnd.py"])
# Start the second program
p2 = subprocess.Popen([venv_python, "forextradebotv3\TradingB_BackEnd.py"])


# Wait for both programs to complete
p1.wait()
p2.wait()