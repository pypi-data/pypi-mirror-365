import sys
from .finder import _finder_instance

def install():
    if _finder_instance not in sys.meta_path:
        sys.meta_path.insert(0, _finder_instance)

def uninstall():
    if _finder_instance in sys.meta_path:
        sys.meta_path.remove(_finder_instance)
        
install()

__all__ = ['install', 'uninstall']