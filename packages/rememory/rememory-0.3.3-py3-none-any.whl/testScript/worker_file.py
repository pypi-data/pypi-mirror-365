import os
import time, pickle, base64
from rememory import RememoryDict, RememoryList, RememoryInt, IntTypes, RememoryFloat, RememoryString, BlockSize


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


def list_worker():
    shared_list: RememoryList[str] = RememoryList(SHARED_LIST_NAME)
    pid = os.getpid()
    shared_list.append(f"start")
    time.sleep(0.5)
    shared_list.append(f"end")


def int_worker():
    shared_int = RememoryInt("shared_int", IntTypes.INT32)
    with shared_int._lock:
        shared_int.value = shared_int.value + 1


def float_worker():
    shared_float = RememoryFloat("shared_float")
    with shared_float._lock:
        shared_float.value = shared_float.value + 1.5


def string_worker():
    shared_string = RememoryString("shared_string")
    pid = os.getpid()
    with shared_string._lock:
        shared_string.value = shared_string.value + f"|rememory"

SHARED_EXCEPTION_NAME = "shared_exception"

def exception_worker():
    shared_str = RememoryString(SHARED_EXCEPTION_NAME, BlockSize.s4096)
    data = shared_str.value
    if not data:
        print(f"[{__name__}] No exception data found")
        return

    try:
        raw_bytes = base64.b64decode(data.encode("ascii"))
        exc = pickle.loads(raw_bytes)
    except Exception as e:
        print(f"[{__name__}] Failed to unpickle: {e}")