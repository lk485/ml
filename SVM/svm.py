# -*- coding: utf-8 -*-
# @Date  : 2020/5/23
# @Author: Luokun
# @Email : olooook@outlook.com

import matplotlib.pyplot as plt
import numpy as np


class SVM:
    """
    Support Vector Machines(支持向量机)
    """

    def __init__(self, C=1.0, tol=1e-3, max_iter=100, kernel='linear', **kwargs):
        """
        :param C: 惩罚因子
        :param tol: 绝对误差限
        :param max_iter: 最大迭代次数
        :param kernel: 核函数
        """
        self.C, self.tol, self.max_iter = C, tol, max_iter
        if kernel == 'linear':
            self.K = self._LinearKernel()  # 线性核函数
        if kernel == 'poly':
            self.K = self._PolyKernel()  # 多项式核函数
        if kernel == 'rbf':
            self.K = self._RBFKernel(kwargs['sigma'])  # 径向基核函数
        self.alpha, self.b = None, .0
        self._X, self._Y = None, None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        self._X, self._Y = X, Y
        self.alpha = np.ones([len(X)], dtype=np.float)  # 拉格朗日乘子
        for _ in range(self.max_iter):
            E = np.array([self._calc_error(i) for i in range(len(X))])  # 此次迭代缓存的误差
            for i1 in range(len(X)):  # 外层循环，寻找第一个alpha
                E1 = self._calc_error(i1)  # 计算误差(不使用E缓存)
                if E1 == 0 or self._satisfy_kkt(i1):  # 误差为0或满足KKT条件
                    continue
                # 大于0则选择最小,小于0选择最大的
                i2 = np.argmin(E) if E1 > 0 else np.argmax(E)  # 内层循环，寻找第二个alpha
                if i1 == i2:
                    continue
                E2 = self._calc_error(i2)
                x1, x2, y1, y2 = X[i1], X[i2], Y[i1], Y[i2]
                alpha1, alpha2 = self.alpha[i1], self.alpha[i2]
                k11, k22, k12 = self.K(x1, x1), self.K(x2, x2), self.K(x1, x2)
                # 计算剪切范围
                if y1 * y2 < 0:
                    L = max(0, alpha2 - alpha1)
                    H = min(self.C, self.C + alpha2 - alpha1)
                else:
                    L = max(0, alpha1 + alpha2 - self.C)
                    H = min(self.C, alpha1 + alpha2)
                if L == H:
                    continue
                eta = k11 + k22 - 2 * k12
                if eta <= 0:
                    continue
                # 计算新alpha
                alpha2_new = np.clip(alpha2 + y2 * (E1 - E2) / eta, L, H)
                alpha1_new = alpha1 + y1 * y2 * (alpha2 - alpha2_new)
                # 计算新b
                alpha2_delta, alpha1_delta = alpha2_new - alpha2, alpha1_new - alpha1
                b1_new = -E1 - y1 * k11 * alpha1_delta - y2 * k12 * alpha2_delta + self.b
                b2_new = -E2 - y1 * k12 * alpha1_delta - y2 * k22 * alpha2_delta + self.b
                # 更新参数
                self.alpha[i1] = alpha1_new
                self.alpha[i2] = alpha2_new
                if 0 < alpha1_new < self.C:
                    self.b = b1_new
                elif 0 < alpha2_new < self.C:
                    self.b = b2_new
                else:
                    self.b = (b1_new + b2_new) / 2
                # 更新误差缓存
                E[i1] = self._calc_error(i1)
                E[i2] = self._calc_error(i2)

    def predict(self, X: np.ndarray):
        Y = np.array([self._g(x) for x in X])
        return np.where(Y > 0, 1, -1)  # 将(-\infinity, \infinity)之间的分布转为{-1, +1}标签

    @property
    def support_vectors(self):  # 支持向量
        return self._X[self.alpha > 0]

    def _g(self, x):  # g(x) =\sum_{i=0}^N alpha_i y_i \kappa(x_i, x)
        return np.sum(self.alpha * self._Y * self.K(self._X, x)) + self.b

    def _calc_error(self, i):  # E_i = g(x_i) - y_i
        return self._g(self._X[i]) - self._Y[i]

    def _satisfy_kkt(self, i):  # 是否满足KKT条件
        gi, yi = self._g(self._X[i]), self._Y[i]
        if np.abs(self.alpha[i]) < self.tol:
            return gi * yi >= 1
        if np.abs(self.alpha[i]) > self.C - self.tol:
            return gi * yi <= 1
        return np.abs(gi * yi - 1) < self.tol

    class _LinearKernel:
        def __call__(self, x: np.ndarray, y: np.ndarray):
            return np.sum(x * y, axis=-1)

    class _PolyKernel:
        def __call__(self, x: np.ndarray, y: np.ndarray):
            return (np.sum(x * y, axis=-1) + 1) ** 2

    class _RBFKernel:
        def __init__(self, sigma):
            self.divisor = 2 * sigma ** 2

        def __call__(self, x: np.ndarray, y: np.ndarray):
            return np.exp(-np.sum((x - y) ** 2, axis=-1) / self.divisor)


def load_data():
    x, y = np.random.randn(2, 400, 2), np.zeros([2, 400], dtype=int)
    y[0] = -1
    y[1] = 1
    for i, theta in enumerate(np.linspace(0, 2 * np.pi, 40)):
        x[0, (10 * i):(10 * i + 10)] += 5 * np.array([np.cos(theta), np.sin(theta)])
    return x, y


def plot_scatter(xys, title):
    plt.figure(figsize=(8, 8))
    for xy, color in zip(xys, ['r', 'g', 'b']):
        plt.scatter(xy[:, 0], xy[:, 1], color=color)
    plt.title(title)
    plt.show()


if __name__ == '__main__':
    x, y = load_data()
    x = x.reshape(-1, 2)
    y = y.flatten()
    plot_scatter([x[y == i] for i in [-1, 1]], 'Real')

    # train
    svm = SVM(C=10, sigma=1, kernel='rbf', max_iter=100)
    svm.fit(x, y)

    # predict
    pred = np.array(svm.predict(x))
    print(svm.support_vectors)
    plot_scatter([x[pred == i] for i in [-1, 1]], 'Pred')

    acc = np.sum(pred == y) / len(pred)
    print(f'Acc = {100 * acc:.2f}%')
