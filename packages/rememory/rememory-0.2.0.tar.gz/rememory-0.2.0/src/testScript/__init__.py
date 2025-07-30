from multiprocessing import Process
import time
from rememory import RememoryDict, RememoryList
from rememory.sharedInt import RememoryInt, IntTypes
from rememory.sharedFloat import RememoryFloat
from rememory.sharedString import RememoryString, BlockSize
from .worker_file import (
    worker,
    list_worker,
    int_worker,
    float_worker,
    string_worker,
    SHARED_NAME,
    SHARED_LIST_NAME
)

NUM_PROCESSES = 4

def main():
    # --- Shared Dict ---
    shared: RememoryDict[str, dict[str, int]] = RememoryDict(SHARED_NAME)
    shared.clear()

    procs = [Process(target=worker) for _ in range(NUM_PROCESSES)]
    for p in procs: p.start()
    for p in procs: p.join()

    print("\nFinal shared dict contents:")
    for k, v in shared.items():
        print(f"{k}: {v}")

    # --- Shared List ---
    shared_list: RememoryList[str] = RememoryList(SHARED_LIST_NAME)
    with shared_list._lock:
        shared_list._write_data([])

    list_procs = [Process(target=list_worker) for _ in range(NUM_PROCESSES)]
    for p in list_procs: p.start()
    for p in list_procs: p.join()

    print("\nFinal shared list contents:")
    for v in shared_list:
        print(v)

    # --- Shared Int ---
    shared_int = RememoryInt("shared_int", IntTypes.INT32)
    shared_int.value = 0

    int_procs = [Process(target=int_worker) for _ in range(NUM_PROCESSES)]
    for p in int_procs: p.start()
    for p in int_procs: p.join()

    print("\nFinal shared int value:", shared_int.value)

    # --- Shared Float ---
    shared_float = RememoryFloat("shared_float")
    shared_float.value = 0.0

    float_procs = [Process(target=float_worker) for _ in range(NUM_PROCESSES)]
    for p in float_procs: p.start()
    for p in float_procs: p.join()

    print("\nFinal shared float value:", shared_float.value)

    # --- Shared String ---
    shared_string = RememoryString("shared_string", BlockSize.S128)
    shared_string.value = ""

    string_procs = [Process(target=string_worker) for _ in range(NUM_PROCESSES)]
    for p in string_procs: p.start()
    for p in string_procs: p.join()

    print("\nFinal shared string value:", shared_string.value)
