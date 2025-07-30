from multiprocessing import Process
import time
from rememory import RememoryDict, RememoryList
from .worker_file import worker, list_worker, SHARED_NAME, SHARED_LIST_NAME

NUM_PROCESSES = 4

def main():
    # --- Shared dict test ---
    shared: RememoryDict[str, dict[str, int]] = RememoryDict(SHARED_NAME)
    shared.clear()

    procs = [Process(target=worker) for _ in range(NUM_PROCESSES)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    time.sleep(0.2)

    print("\nFinal shared dict contents:")
    for k, v in shared.items():
        print(f"{k}: {v}")

    # --- Shared list test ---
    shared_list: RememoryList[int] = RememoryList(SHARED_LIST_NAME)
    # clear the list
    with shared_list._lock:
        shared_list._write_data([])

    list_procs = [Process(target=list_worker) for _ in range(NUM_PROCESSES)]
    for p in list_procs:
        p.start()
    for p in list_procs:
        p.join()

    time.sleep(0.2)

    print("\nFinal shared list contents:")
    for v in shared_list:
        print(v)
