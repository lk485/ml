# -*- coding: utf-8 -*-
# @Date  : 2020/5/23
# @Author: Luokun
# @Email : olooook@outlook.com

import numpy as np
from numpy.lib.npyio import load


class DecisionTree:
    """
    Decision tree classifier(决策树分类器，ID3生成算法)
    """

    def __init__(self, rate: float = 0.95):
        self.rate = rate
        self._X, self._Y, self.tree = None, None, None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        self._X, self._Y = X, Y
        indices = np.arange(X.shape[0])  # 所有行索引
        features = np.arange(X.shape[1])  # 所有列索引
        self.tree = self._create_tree(indices, features)
        self._X, self._Y = None, None

    def predict(self, X: np.ndarray):
        Y = np.zeros([len(X)], dtype=int)  # 输出变量
        for i, x in enumerate(X):
            Y[i] = self._predict(self.tree, x)
        return Y

    def _predict(self, node, x):
        if isinstance(node, dict):  # 如果节点是树(字典)类型
            key = x[node['feature']]  # 获取划分特征的值
            return self._predict(node['trees'][key], x)  # 根据值进行下一次递归
        return node  # 如果节点是叶子类型则直接返回该值

    def _create_tree(self, indices, features):
        best_class, rate = self._select_class(indices)  # 获得数量最多的类别及其频率
        if len(features) == 0 or rate > self.rate:  # 无特征可分或者满足一定的单一性
            return best_class  # 返回最单一的类别
        best_feature = self._select_feature(indices, features)  # 选择香农熵最小的特征
        sub_trees = {}
        rest_features = features[features != best_feature]  # 除去选择的特征
        for key in np.unique(self._X[indices, best_feature]):  # 为该特征的每一个取值都建立子树
            sub_indices = self._query_indices(indices, best_feature, key)
            sub_trees[key.item()] = self._create_tree(sub_indices, rest_features)  # 递归构建子决策树
        return {'feature': best_feature, 'trees': sub_trees}

    def _query_indices(self, indices, feature, value):
        return indices[self._X[indices, feature] == value]

    def _calc_info_gain(self, indices, feature):  # 计算信息增益
        ent = self._calc_entropy(indices)  # 经验熵
        cond_ent = self._calc_cond_entropy(indices, feature)  # 经验条件熵
        return ent - cond_ent  # 信息增益

    def _calc_entropy(self, indices):  # 计算经验熵
        prob = np.bincount(self._Y[indices]) / len(indices)  # 采用二进制计数法，x必须为正整数向量
        prob = prob[prob != 0]  # 除去0概率
        return np.sum(prob * -np.log(prob))  # 经验熵

    def _calc_cond_entropy(self, indices, feature):  # 计算条件熵
        cond_ent = 0  # 经验条件熵
        for val in np.unique(self._X[indices, feature]):
            sub_indices = self._query_indices(indices, feature, val)
            cond_ent += len(sub_indices) / len(indices) * self._calc_entropy(sub_indices)
        return cond_ent  # 条件熵

    def _select_class(self, indices):
        prob = np.bincount(self._Y[indices]) / len(indices)  # 计算类别频率
        c = np.argmax(prob)
        return c, prob[c]  # 返回出现次数最多的类别，以及其频率

    def _select_feature(self, indices, features):
        gains = np.array([
            self._calc_info_gain(indices, feature) for feature in features
        ])  # 计算features中所有特征的信息增益
        f = np.argmax(gains)
        return features[f]  # 返回信息增益最大的特征


def load_data():
    x = np.array([
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 1],
        [0, 1, 1],

        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 0],
        [1, 1, 0],
        [1, 1, 1],
        [1, 1, 1],
    ])
    y = np.array([1 if np.sum(xi) >= 2 else 0 for xi in x])
    return x, y


if __name__ == '__main__':
    x, y = load_data()
    decision_tree = DecisionTree(rate=0.95)
    decision_tree.fit(x, y)
    print(decision_tree.tree)
    pred = decision_tree.predict(x)
    print(y)
    print(pred)
    acc = np.sum(pred == y) / len(pred)
    print(f'Acc = {100 * acc:.2f}%')
