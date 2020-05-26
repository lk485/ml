# -*- coding: utf-8 -*-
# @Date  : 2020/5/21
# @Author: Luokun
# @Email : olooook@outlook.com

import numpy as np


class LogisticRegression:
    """
    Logistic regression classifier(逻辑斯蒂回归分类器)
    """

    def __init__(self, input_dim: int, lr: float):
        self.weights = np.random.randn(input_dim + 1)  # 随机初始化参数
        self.lr = lr  # 学习率

    def fit(self, X: np.ndarray, Y: np.ndarray):
        x_pad = pad(X)  # 为X填充1作为偏置
        pred = sigmoid(x_pad @ self.weights)  # 计算预测值
        grad = x_pad.T @ (pred - Y) / len(pred)  # 计算梯度
        self.weights -= self.lr * grad  # 沿负梯度更新参数

    def predict(self, X: np.ndarray):
        x_pad = pad(X)  # 为X填充1作为偏置
        pred = sigmoid(x_pad @ self.weights)  # 计算预测值
        return binarize(pred)  # 将(0, 1)之间分布的概率转化为{0, 1}标签


def pad(x):
    return np.concatenate([x, np.ones([len(x), 1])], axis=1)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def binarize(x, threshold=.5):
    y = np.zeros_like(x, dtype=int)
    y[x > threshold] = 1
    return y