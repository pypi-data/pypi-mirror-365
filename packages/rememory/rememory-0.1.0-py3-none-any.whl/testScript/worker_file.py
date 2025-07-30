import os
import time
from rememory import RememoryDict, RememoryList

SHARED_NAME = "game"
SHARED_LIST_NAME = "gamelist"

def worker():
    shared: RememoryDict[str, dict[str, int]] = RememoryDict(SHARED_NAME)
    pid = os.getpid()
    shared[str(pid)] = {"score": 1, "level": 1}
    time.sleep(0.5)
    temp = shared[str(pid)]
    temp["score"] += 1
    temp["level"] += 1
    shared[str(pid)] = temp
    print(f"[{pid}] Finished updating shared dict")

def list_worker():
    shared_list: RememoryList[str] = RememoryList(SHARED_LIST_NAME)
    pid = os.getpid()
    # Append pid twice to test concurrent appends
    shared_list.append(f"{pid}-start")
    time.sleep(0.5)
    shared_list.append(f"{pid}-end")
    print(f"[{pid}] Finished updating shared list")
