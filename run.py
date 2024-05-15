import subprocess


venv_python = r'.venv\Scripts\python.exe'
# Start the first program
p1 = subprocess.Popen([venv_python, 'TradingB_BackEnd.py'])

# Start the second program
p2 = subprocess.Popen([venv_python, 'TradingB_FrontEnd.py'])

# Wait for both programs to complete
p1.wait()
p2.wait()
