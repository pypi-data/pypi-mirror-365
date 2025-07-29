from stream import testbybnr

def test_testbybnr():
    assert testbybnr() == {"status_code":200,
            "message": "Hello from testbybnr"}