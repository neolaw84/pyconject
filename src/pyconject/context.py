from copy import deepcopy
from pathlib import Path
import inspect
from .registry import Registry
from .utils import Stack, load_and_merge_configs, merge_dictionaries

# def _get_caller():
#     """Retrieves the globals() dictionary of the caller's frame."""

#     caller_frame = inspect.currentframe().f_back.f_back
#     return caller_frame

class Cntx:
    def __init__(self, target=None, config_path=None, cntx_stack=None):
        self.cntx_stack = cntx_stack if cntx_stack else _cntx_stack

        frame = inspect.currentframe()

        while frame:
            filename = inspect.getframeinfo(frame).filename
            if not any(pattern in filename for pattern in ["<frozen importlib._bootstrap>", "<pytest", "<ipython-input-"]):
                self.glb = frame.f_globals
                break  # Exit after modifying the first suitable frame
            frame = frame.f_back

        self.target = target
        self.config_path = config_path

    def __enter__(self):
        self.cntx_stack.stack(target=self.target, config_path=self.config_path)
        
        # new_globals = {n: self.cntx_stack.registry.register(v, by_dev=False) for n, v in self.glb.items()}
        # for n, v in new_globals.items():
        #     self.glb[n] = v
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cntx_stack.unstack()


class CntxStack:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CntxStack, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config_stack = Stack()
        self.target_stack = Stack()
        self.registry = Registry(self)

    def _resolve_dev_configs(self, target=None):
        dev_configs = self.registry.load_dev_configs(force=True, target=target)
        self.config_stack.push(dev_configs)
        self.target_stack.push(target)
        return dev_configs

    def stack(self, target=None, config_path=None):
        prev_configs = self.config_stack.peek()
        if prev_configs is None:
            prev_configs = self._resolve_dev_configs(target=None)
        if target is not None:
            prev_configs_target = self._resolve_dev_configs(target=target)
            prev_configs = merge_dictionaries(prev_configs, prev_configs_target)
        # at this point, prev_configs is not None
        configs = deepcopy(prev_configs)
        if config_path is None: 
            config_path = "./configs.yml"
        config_path = Path(config_path)
        configs = load_and_merge_configs(config_path, configs)
        
        if target is not None: 
            tgt_config_path = config_path.parent / f"{config_path.stem}-{target}{config_path.suffix}"
            configs = load_and_merge_configs(tgt_config_path, configs)
        
        self.config_stack.push(configs)
        self.target_stack.push(target)

        return configs
    
    def get_configs(self):
        # load dev config if it is not there yet 
        if len(self.config_stack) < 1: 
            self.stack() 
        return self.config_stack.peek() # if len(self.config_stack) > 1 else {}
    
    def unstack(self):
        if self.target_stack.peek():
            self.config_stack.pop()
            self.target_stack.pop()
        self.config_stack.pop()
        self.target_stack.pop()
        # if len(self.config_stack) == 1: self.config_stack.pop()

_cntx_stack = CntxStack()