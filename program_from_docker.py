from threading import Thread
import os
import program
import time

def lst():
    program.main()

def start_server():
    cmd = "python3 -m http.server"
    print("start server")
    os.system(cmd)

def main():
    thread_server = Thread(target=start_server, args=())
    thread_server.start()
    time.sleep(1)

    thread_LST = Thread(target=lst, args=())
    thread_LST.start()

if __name__ == '__main__':
    main()