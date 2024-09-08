from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd
import numpy as np

from typing import Dict

from . import utils

def calculate_objective(metric_values: pd.DataFrame):
    """
    calculate objective value using given metric values

    Parameters
    ----------
    metric_values: pd.DataFrame
        A DataFrame containing customized metric values needed for objective.
    """
    pass


class TreeNodeMetric:
    def __init__(self, metrics: Dict[str, str], **kwargs):
        """
        Parameters
        ----------
        metrics: Dict[str, str]
            A dictionary of metric names and their corresponding sql script.
        """

        self.metrics = metrics


    def build(self, table: str, **kwargs):
        """
        build metric values using given table

        Parameters
        ----------
        table: str
            The table name to be used for building metric values.
        """
        
        sql = "select\n" + "\,".join(
            [f"{sql} as {name}" for name, sql in self.metrics.items()]
        ) + f"\nfrom {table}"

        self.metric_values = utils.get_dataframe_from_sql(sql)
        return self.metric_values