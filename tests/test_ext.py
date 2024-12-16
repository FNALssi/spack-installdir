import os
import time
import pytest

# basic integration tests

@pytest.fixture
def workdir():
    wd = f"{os.environ.get('TMPDIR','/tmp')}/work{os.getpid()}"
    yield wd
    os.system("rm -rf {wd}")

@pytest.fixture
def workdir_w_files(workdir):
    os.makedirs(f"{workdir}/files", exist_ok=True)
    for f in ["a","b","c"]:
        with open(f"{workdir}/files/{f}", "w") as fout:
            fout.write(f"{f}\n")
    yield workdir
    return None   

@pytest.fixture
def newvers():
    return f"{int(time.time())}"

def test_help():
    with os.popen("spack installdir --help", "r") as fin:
        data = fin.read()
    assert(data.find("--directory DIRECTORY") >= 0)
    assert(data.find("--namespace NAMESPACE") >= 0)


def test_minimal( workdir_w_files, newvers):
    with os.popen(f"cd {workdir_w_files} && spack installdir test-pkg@{newvers}.1") as fin:
        data = fin.read()
        print(data)
    with os.popen(f"spack location -i test-pkg@{newvers}.1") as fin:
        path = fin.read().strip()
    assert(path.find(f"test-pkg") >= 0)
    assert(path.find(f"{newvers}.1") >= 0)
    assert(os.stat(f"{path}/a").st_size == 2 )
    assert(os.stat(f"{path}/b").st_size == 2 )
    with os.popen(f"spack uninstall test-pkg@{newvers}.1") as fin:
        data = fin.read()
        print(data)

def test_directory( workdir_w_files, newvers):
    with os.popen(f"spack installdir --directory {workdir_w_files} test-pkg@{newvers}.2") as fin:
        data = fin.read()
    with os.popen(f"spack location -i test-pkg@{newvers}.2") as fin:
        path = fin.read().strip()
    assert(path.find(f"test-pkg") >= 0)
    assert(path.find(f"{newvers}.2") >= 0)
    assert(os.stat(f"{path}/a").st_size == 2 )
    assert(os.stat(f"{path}/b").st_size == 2 )
    with os.popen(f"spack uninstall test-pkg@{newvers}.2") as fin:
        data = fin.read()
        print(data)
