import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def pytest_collection_modifyitems(items, config):
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("unmarked")