from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from . import utils

from typing import List, Any, Union, Tuple

class FeatureInfo:
    def __init__(self, 
        name: str, 
        is_categorical: bool, 
        values: Union[List[Any], None] = None
    ):
        self.name = name
        self.is_categorical = is_categorical
        # quantiles for numerical features
        # categories for categorical features
        self.values = values if values is not None else []

        # store the best split point
        self.best_split: Tuple[str] = None

        # whether the feature can be used for splitting
        self.split = True
    
    @property
    def left(self):
        return self.best_split[0]
    
    @property
    def right(self):
        return self.best_split[1]
    
    def derive(self, is_left: bool=True) -> 'FeatureInfo':
        """
        derive the feature info for the left and right node
        """
        values = self.values
        if is_left:
            values = self.values[:self.best_split]
        else:
            values = self.values[self.best_split:]
            
        info = FeatureInfo(self.name, self.is_categorical, values)
        return info
