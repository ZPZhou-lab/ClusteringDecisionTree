from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd

from . import utils
from .metrics import TreeNodeMetric, calculate_objective
from .feature import FeatureInfo

from typing import List

def calculate_criterion(metric_values: pd.DataFrame, criterion: str):
    pass


class TreeNode:
    def __init__(self,
        sample_table: str,
        paths: List[str],
        feature_infos: List[FeatureInfo],
        depth: int,
        metric: TreeNodeMetric,
        **kwargs
    ):
        """
        Parameters
        ----------
        sample_table: str
            The table name corresponding to this tree node.
        paths: List[str]
            The decision paths leading to this tree node.\n
            Format in sql where clause, e.g. "age > 18 and city in ('Beijing', 'Shanghai')"
        feature_infos: List[FeatureInfo]
            The feature information used for splitting.
        depth: int
            The depth of this tree node.
        """
        self.sample_table = sample_table
        self.paths = paths
        self.depth = depth
        self.feature_infos = feature_infos

        # Node attributes
        self.is_leaf = False
        self.left = None
        self.right = None
        self.feature: FeatureInfo = None

        # build metric values and calculate objective in this node
        self.metric = metric
        self.metric_values = self.metric.build(self.sample_table)
        self._obj = calculate_objective(self.metric_values)

        # total sample in this node
        self.total = self.metric_values["total"].sum()

    def split(self, **kwargs):
        """
        split the sample table into two tables

        Parameters
        ----------
        feature_infos: List[FeatureInfo]
            The feature information used for splitting.
        **kwargs:
            Additional decision tree parameters.
        """

        # build the left and right node
        if not self.is_leaf and self.feature is not None:
            # left sample table
            left_table, right_table = self.sample_table + "_L", self.sample_table + "_R"
            left_path, _ = self.build_subset_table(self.feature, is_left=True, subset_table=left_table)
            right_path, _ = self.build_subset_table(self.feature, is_left=False, subset_table=right_table)

            # build left
            self.left = TreeNode(
                sample_table=left_table,
                paths=list(self.paths) + [left_path],
                feature_infos=[f.derive(is_left=True) for f in self.feature_infos],
                depth=self.depth + 1, 
                metric=self.metric
            )

            # build right
            self.right = TreeNode(
                sample_table=right_table,
                paths=list(self.paths) + [right_path],
                feature_infos=[f.derive(is_left=False) for f in self.feature_infos],
                depth=self.depth + 1, 
                metric=self.metric
            )

    
    def build(self, **kwargs):
        """
        build the tree node and find the best split feature

        Parameters
        ----------
        **kwargs:
            Additional decision tree parameters.
        """
        # check stop condition
        if self.depth == kwargs["max_depth"] or\
            self.total <= kwargs["min_samples_split"]:
            self.is_leaf = True
            return

        # find the best split feature
        best_feat, best_crit = None, None
        for feature in self.feature_infos:
            pass

    def build_subset_table(self, 
        feature: FeatureInfo, 
        is_left: bool=True,
        subset_table: str=None
    ):
        path = feature.left if is_left else feature.right
        subset_table = ... if subset_table is None else subset_table

        # create subset table
        sql = f"drop table if exists {subset_table}; create table {subset_table} lifecycle 1 as\n\
        select * from {self.sample_table} where {path}"
        utils.run_odps_sql(sql)
        
        return path, subset_table


class ClusteringDecisionTree:
    def __init__(self,
        max_depth: int=5,
        max_leaves: int=31,
        min_samples_split: int=100000,
        epsilon: float=0.01,
        **kwargs
    ):
        self.max_depth = max_depth
        self.max_leaves = max_leaves
        self.min_samples_split = min_samples_split
        self.epsilon = epsilon
        # format decision tree parameters
        self._parameters = parse_decision_tree_parameters(
            max_depth=max_depth, 
            max_leaves=max_leaves, 
            min_samples_split=min_samples_split, 
            epsilon=epsilon
        )

        # init root node
        self.root = None

    def fit(self,
        sample_table: str,
        feature_infos: List[FeatureInfo],
        metric: TreeNodeMetric,
        **kwargs
    ):
        # init root node
        self.root = TreeNode(sample_table, paths=["1 = 1"], depth=0, metric=metric)

        # use leaf-wise strategy to grow tree
        leaf_nodes = [self.root]
        
        # grow tree until max_leaves or no more nodes can be split
        while len(leaf_nodes) < self.max_leaves and any(not node.is_leaf for node in leaf_nodes):
            # find best node to split
            best_node, best_crit = None, None
            for node in leaf_nodes:
                if not node.is_leaf:
                    node.build(feature_infos)
            
            # split best node
            if best_node is not None:
                best_node.split(feature_infos, **self._parameters)
                # add new leaf nodes to leaf_nodes if not leaf
                if not best_node.is_leaf:
                    leaf_nodes.remove(best_node)
                    leaf_nodes.extend([best_node.left, best_node.right])
        

    def predict(self, sample_table: str, **kwargs):
        pass



def parse_decision_tree_parameters(**kwargs):
    params = {
        "max_depth": kwargs.get("max_depth", 5),
        "max_leaves": kwargs.get("max_leaves", 31),
        "min_samples_split": kwargs.get("min_samples_split", 100000),
        "epsilon": kwargs.get("epsilon", 0.01)
    }
    return params
