"""
Vector Memory module - Context Retention System Component 3

This module provides an interface to the Vector Memory Pipeline,
which enables semantic search of memory files and session logs.

This is a wrapper module that imports from vector-memory.py to maintain
the proper Python module naming convention.
"""

import os
import sys

# Add the workspace directory to the Python path
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
sys.path.append(WORKSPACE_DIR)

# Import all objects from vector-memory.py
try:
    from vector_memory_impl import *
except ImportError:
    # If the implementation module doesn't exist, copy from the original file
    import shutil
    original_file = os.path.join(WORKSPACE_DIR, "vector-memory.py")
    impl_file = os.path.join(WORKSPACE_DIR, "vector_memory_impl.py")
    
    if os.path.exists(original_file) and not os.path.exists(impl_file):
        shutil.copy2(original_file, impl_file)
        # Try importing again
        try:
            from vector_memory_impl import *
        except ImportError:
            raise ImportError("Failed to import vector_memory_impl.py. Make sure vector-memory.py is properly implemented.")
    else:
        raise ImportError("Vector Memory Pipeline (vector-memory.py) not found.")