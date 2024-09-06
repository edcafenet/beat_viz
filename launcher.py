from sys import exit
import subprocess
import time

print('running ...')
fft_api = subprocess.Popen(['mamba', 'run', '-n', 'fastapi', 'fastapi', 'dev', 'fft_api.py'])
pyautogui = subprocess.Popen(['mamba', 'run', '-n', 'pyautogui', 'python', 'main.py', '--device 2', '--ip 10.205.3.4', '--port 9876'])

umh0 = subprocess.Popen(['mamba', 'run', '-n', 'fastapi', 'fastapi', 'run', 'udp_api_umh0.py', '--port 8001'])
umh1 = subprocess.Popen(['mamba', 'run', '-n', 'fastapi', 'fastapi', 'run', 'udp_api_umh1.py', '--port 8002'])
umh2 = subprocess.Popen(['mamba', 'run', '-n', 'fastapi', 'fastapi', 'run', 'udp_api_umh2.py', '--port 8003'])
umh3 = subprocess.Popen(['mamba', 'run', '-n', 'fastapi', 'fastapi', 'run', 'udp_api_umh3.py', '--port 8004'])

ableton_bridge = subprocess.Popen(['mamba', 'run', '-n', 'pyautogui', 'python', 'ableton_bridge.py'])
spline_draw = subprocess.Popen(['mamba', 'run', '-n', 'fastapi', 'npx', 'vite', '/Users/edu/beat_viz/www/spline_draw'])
google_chrome = subprocess.Popen(['open', '-na Google\ Chrome', '--args', '--user-data-dir=/tmp/temporary-chrome-profile-dir', '--disable-web-security', '--disable-site-isolation-trials', '/Users/edu/beat_viz/www/webgl/index.html']) 

while True:
    try:
        pass
    except KeyboardInterrupt:
        # User interrupt the program with ctrl+c
        subprocess.Popen.kill(fft_api)
        subprocess.Popen.kill(pyautogui)
        subprocess.Popen.kill(umh0)
        subprocess.Popen.kill(umh1)
        subprocess.Popen.kill(umh2)
        subprocess.Popen.kill(umh3)

        subprocess.Popen.kill(ableton_bridge)
        subprocess.Popen.kill(spline_draw)
        subprocess.Popen.kill(google_chrome)

        exit()
    
    time.sleep(1)