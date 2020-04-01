# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
import queue

from lib.log import setupLogger
from lib.wordlist import WordListGenerator
from lib.worker import WorkerThread
from lib.connection import URLFormatter
from lib.connection import RobotHandler


def main():
    """
    A function to parse the command argument
    And control the main program
    """

    logger = setupLogger()
    parser = argparse.ArgumentParser(prog="admin-bulucu.py", description="Admin Panel Bulucu")
    parser.add_argument("-u", "--url", help="Hedef url/website")
    parser.add_argument("-w", "--wordlist", help="Kullanim icin Wordlist,'wordlist.txt'")
    parser.add_argument("-t", "--threadcount", help="Kullanim icin konu numarasi")

    args = parser.parse_args()

    if args.url is None:
        parser.print_help()
        print("[-] -u URL parametresi gerekli")
        exit()

    if args.threadcount is not None:
        if not args.threadcount.isdigit():
            print("[-] İslem sayisi parametresinin basamakli olması gerekir")
            exit()
    else:
        args.threadcount = 20

    if args.wordlist is None:
        args.wordlist = "wordlist.txt"
    args.url = URLFormatter(args.url).geturl()

    if args.credentials:
        if ":" not in args.credentials:
            print("[!] Hata: kimlik bilgisinin bu bicimde olmasi gerekir; user:pass")
            exit()
        args.credentials = args.credentials.split(":")

    robot_handler = RobotHandler(args.url, args.credentials)
    result = robot_handler.scan()

    if result:
        logger.info("Robot dosyasinda algilanan anahtar kelimeler")
        print("-" * 30)
        print("\n".join(result))
        print("-" * 30)
        print("Taramaya devam etmek istiyormusun?")
        choice = input("[e]/h: ")
        if choice == "h":
            exit()

    try:
        workQueue = queue.Queue()
        workerPool = []
        for _ in range(int(args.threadcount)):
            thread = WorkerThread(workQueue, args.credentials)
            thread.daemon = True
            thread.start()
            workerPool.append(thread)

        for url in WordListGenerator(args.url, filename=args.wordlist):
            workQueue.put(url)

        logger.info("Tarayıcı basladi")

        while not workQueue.empty():
            pass
        # to lock the main thread from exiting
    except KeyboardInterrupt:
        logger.info("Tespit edilen Ctrl + C, sonlandirma")
        for i in workerPool:
            i.work = False



def banner():
    print('\033[91m' + """
    ╔════════════════════════════════════════════╗
    ║               .          .                 ║
    ║ ,-. ,-| ,-,-. . ,-.   ," . ,-. ,-| ,-. ,-. ║
    ║ ,-| | | | | | | | |   |- | | | | | |-' |   ║
    ║ `-^ `-^ ' ' ' ' ' '   |  ' ' ' `-^ `-' '   ║
    ║                       '     neo/spyhackerz ║
    ╚════════════════════════════════════════════╝
    """ + '\033[0m')

if __name__ == "__main__":
    banner()
    main()
