import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from my_pip_lib import hello

def test_hello():
    assert hello("World") == "Hello, World!"
