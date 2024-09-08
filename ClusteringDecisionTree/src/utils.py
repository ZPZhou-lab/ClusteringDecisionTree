from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd

def run_odps_sql(odps_sql: str, enable_wait: bool = True):
    """
    submit sql job

    Parameters
    ----------
    odps_sql: str
        sql to be submitted
    enable_wait: bool
        whether to wait for the job to complete
    """
    pass


def get_dataframe_from_sql(odps_sql: str) -> pd.DataFrame:
    """
    submit sql job and return a dataframe object

    Parameters
    ----------
    odps_sql: str
        sql to be submitted
    """
    pass