import sys

class LazyProxy:
    def __init__(self, module_name, obj_name):
        self.__module_name = module_name
        self.__obj_name = obj_name
        self.__real_obj = None

    def _load_real_obj(self):
        if self.__real_obj is None:
            module = sys.modules[self.__module_name]
            self.__real_obj = getattr(module, self.__obj_name)
        return self.__real_obj

    def __call__(self, *args, **kwargs):
        return self._load_real_obj()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._load_real_obj(), name)