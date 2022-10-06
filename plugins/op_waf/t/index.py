# coding:utf-8

import sys
import io
import os
import time
import json


def run():
    print('op lua run ok')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "remove":
            removeBgTask()
        elif action == "add":
            createBgTask()
        elif action == "run":
            run()
