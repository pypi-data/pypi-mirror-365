# versions/__init__.py
import importlib
import os
import sys

class VersionSelector:
    _available_versions = {
        'v0': 'v0',
        'v1': 'v1',
        'v2': 'v2',
        'v3a': 'v3a',
        'v3b': 'v3b',
        'v3c': 'v3c'
    }
    
    def __init__(self, version='v0'):
        self.version = version.lower()
        
        if self.version not in self._available_versions:
            raise ValueError(f"Unsupported version. Available versions: {list(self._available_versions.keys())}")
        
        # 确保模块路径正确
        #sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        #module_name = f"flexscspace.{self._available_versions[self.version]}"
        module_name = f"flexscspace.{self.version}"
        try:
            self.module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise ImportError(f"Failed to import version {version}") from e
    
    def load_data(self, **kwargs):
        return self.module.load_data(**kwargs)
    
    def construct_pseudo_space(self, **kwargs):
        return self.module.construct_pseudo_space(**kwargs)
    
    def spatial_cluster(self, **kwargs):
        return self.module.spatial_cluster(**kwargs)
    
    def fit(self, **kwargs):  # TCA训练[^5]
        return self.module.fit(**kwargs)
        
    def kernel(self, **kwargs):  # 核计算[^6]
        return self.module.kernel(**kwargs)
        
    def run_leiden(self, **kwargs):  # 聚类[^4]
        return self.module.run_leiden(**kwargs)
    
    def preporcess(self, **kwargs):
        return self.module.preporcess(**kwargs)
    
    def cal_dist(self, coord, normalize=True):
        return self.module.cal_dist(coord, normalize=normalize)

    def cal_dist_group(self, **kwargs):
        return self.module.cal_dist_group(**kwargs)

    # 可以添加其他通用方法...
