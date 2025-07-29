
__version__ = '0.1.7'  # 2025-07-28


from . datasets import *
from . datasets import get_datasets



def link( path ):
    import os,sys
    import importlib.util
    this = sys.modules[__name__]
    for s in sorted( os.listdir( path ) ):
        if s[0].isupper():
            path2init = os.path.join( path, s, '__init__.py' )
            spec      = importlib.util.spec_from_file_location(s, path2init)
            module    = importlib.util.module_from_spec(spec)
            sys.modules[s] = module
            spec.loader.exec_module(module)
            exec( f'this.{s} = module.{s}' )


def get_dataset_by_name(name):
    dataset = eval( f'{name}()' )
    return dataset