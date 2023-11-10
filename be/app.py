from be import server
import multiprocessing
import subprocess

if __name__ == '__main__':
    # p = multiprocessing.Process(target=subprocess.call, args=(["python", "auto_cancel.py"],))
    # p.start()
    server.be_run()