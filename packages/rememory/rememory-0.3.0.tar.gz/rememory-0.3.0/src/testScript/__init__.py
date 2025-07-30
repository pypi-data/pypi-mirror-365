from multiprocessing import Process
import base64
import pickle
from rememory import (
    RememoryDict, RememoryList, RememoryInt,
    IntTypes, RememoryFloat, RememoryString, BlockSize
)
from .worker_file import (
    worker,
    list_worker,
    int_worker,
    float_worker,
    string_worker,
    exception_worker,
    SHARED_EXCEPTION_NAME,
    SHARED_NAME,
    SHARED_LIST_NAME,
)
from .exception import NoBaseException
NUM_PROCESSES = 4

def main():
    passed = []
    failed = []

    if testSharedDict():
        passed.append("Shared Dict")
    else:
        failed.append("Shared Dict")

    if testSharedList():
        passed.append("Shared List")
    else:
        failed.append("Shared List")

    if testSharedInt():
        passed.append("Shared Int")
    else:
        failed.append("Shared Int")

    if testSharedFloat():
        passed.append("Shared Float")
    else:
        failed.append("Shared Float")

    if testSharedString():
        passed.append("Shared String")
    else:
        failed.append("Shared String")

    if testClassBlock():
        passed.append("Class Block")
    else:
        failed.append("Class Block")

    if len(failed) > 0 and len(passed) > 0:
        print("Tests Passed:")
        for test in passed:
            print(f"- {test}")
        print("Tests Failed:")
        for test in failed:
            print(f"- {test}")
    elif len(failed) > 0:
        print("All tests failed!")
    else:
        print("All tests passed!")


def testSharedDict() -> bool:
    shared: RememoryDict[str, dict[str, int]] = RememoryDict(SHARED_NAME)
    shared.clear()

    procs = [Process(target=worker) for _ in range(NUM_PROCESSES)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    return len(shared.keys()) == NUM_PROCESSES


def testSharedList() -> bool:
    shared_list: RememoryList[str] = RememoryList(SHARED_LIST_NAME)
    with shared_list._lock:
        shared_list._write_data([])

    list_procs = [Process(target=list_worker) for _ in range(NUM_PROCESSES)]
    for p in list_procs:
        p.start()
    for p in list_procs:
        p.join()

    expected = [f"start" for _ in range(NUM_PROCESSES)] + [f"end" for _ in range(NUM_PROCESSES)]
    return list(shared_list) == expected


def testSharedInt() -> bool:
    shared_int = RememoryInt("shared_int", IntTypes.INT32)
    shared_int.value = 0

    int_procs = [Process(target=int_worker) for _ in range(NUM_PROCESSES)]
    for p in int_procs:
        p.start()
    for p in int_procs:
        p.join()

    return shared_int.value == NUM_PROCESSES


def testSharedFloat() -> bool:
    shared_float = RememoryFloat("shared_float")
    shared_float.value = 0.0

    float_procs = [Process(target=float_worker) for _ in range(NUM_PROCESSES)]
    for p in float_procs:
        p.start()
    for p in float_procs:
        p.join()

    return shared_float.value == 1.5 * NUM_PROCESSES


def testSharedString() -> bool:
    shared_string = RememoryString("shared_string", BlockSize.s128)
    shared_string.value = ""

    string_procs = [Process(target=string_worker) for _ in range(NUM_PROCESSES)]
    for p in string_procs:
        p.start()
    for p in string_procs:
        p.join()

    return shared_string.value == f"|rememory" * NUM_PROCESSES

def testClassBlock() -> bool:
    e = NoBaseException(404, "Not Found")

    raw_bytes = pickle.dumps(e)
    data_str = base64.b64encode(raw_bytes).decode("ascii")

    shared_str = RememoryString(SHARED_EXCEPTION_NAME, BlockSize.s4096)
    with shared_str._lock:
        shared_str.value = data_str

    procs = [Process(target=exception_worker) for _ in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    reloaded = pickle.loads(base64.b64decode(shared_str.value.encode("ascii")))
    return isinstance(reloaded, NoBaseException)