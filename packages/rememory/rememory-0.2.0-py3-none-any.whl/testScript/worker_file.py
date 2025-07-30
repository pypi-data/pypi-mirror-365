import os
import time
from rememory import RememoryDict, RememoryList, RememoryInt, IntTypes, RememoryFloat, RememoryString

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
    shared_list.append(f"{pid}-start")
    time.sleep(0.5)
    shared_list.append(f"{pid}-end")
    print(f"[{pid}] Finished updating shared list")


def int_worker():
    shared_int = RememoryInt("shared_int", IntTypes.INT32)
    with shared_int._lock:
        shared_int.value = shared_int.value + 1
    print(f"[{os.getpid()}] Incremented shared int")


def float_worker():
    shared_float = RememoryFloat("shared_float")
    with shared_float._lock:
        shared_float.value = shared_float.value + 1.5
    print(f"[{os.getpid()}] Added to shared float")


def string_worker():
    shared_string = RememoryString("shared_string")
    pid = os.getpid()
    with shared_string._lock:
        # Append process ID to the shared string, separated by '|'
        shared_string.value = shared_string.value + f"|{pid}"
    print(f"[{pid}] Appended to shared string")
