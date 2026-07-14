"""ByteTrack 使用的边界框卡尔曼滤波器。"""

import numpy as np
import scipy.linalg


"""自由度为 1 至 9 时，卡方分布 0.95 分位数查找表。

该查找表用于计算马氏距离门控阈值，数值来源于 MATLAB/Octave 的
chi2inv 函数。
"""
chi2inv95 = {
    1: 3.8415,
    2: 5.9915,
    3: 7.8147,
    4: 9.4877,
    5: 11.070,
    6: 12.592,
    7: 14.067,
    8: 15.507,
    9: 16.919,
}


class KalmanFilter(object):
    """在图像空间中跟踪边界框的卡尔曼滤波器。

    状态空间为 8 维：x、y、a、h、vx、vy、va、vh。其中 x、y 表示边界框
    中心位置，a 表示宽高比，h 表示高度，其余变量表示对应速度。

    目标运动采用恒定速度模型，边界框位置 x、y、a、h 作为状态空间的直接
    观测值。
    """

    def __init__(self):
        """初始化卡尔曼滤波器的运动和观测模型。"""
        ndim, dt = 4, 1.

        # 创建卡尔曼滤波器的模型矩阵。
        self._motion_mat = np.eye(2 * ndim, 2 * ndim)
        for i in range(ndim):
            self._motion_mat[i, ndim + i] = dt
        self._update_mat = np.eye(ndim, 2 * ndim)

        # 根据当前状态估计设置运动和观测不确定性权重。
        self._std_weight_position = 1. / 20
        self._std_weight_velocity = 1. / 160

    def initiate(self, measurement):
        """根据未关联观测创建轨迹。

        参数:
            measurement: 边界框坐标 ``(x, y, a, h)``，分别表示中心位置、
                宽高比和高度。

        返回:
            新轨迹的 8 维均值向量和 8×8 协方差矩阵。未观测速度的均值初始
            为 0。
        """
        mean_pos = measurement
        mean_vel = np.zeros_like(mean_pos)
        mean = np.r_[mean_pos, mean_vel]

        std = [
            2 * self._std_weight_position * measurement[3],
            2 * self._std_weight_position * measurement[3],
            1e-2,
            2 * self._std_weight_position * measurement[3],
            10 * self._std_weight_velocity * measurement[3],
            10 * self._std_weight_velocity * measurement[3],
            1e-5,
            10 * self._std_weight_velocity * measurement[3],
        ]
        covariance = np.diag(np.square(std))
        return mean, covariance

    def predict(self, mean, covariance):
        """执行卡尔曼滤波预测步骤。

        参数:
            mean: 上一时刻目标状态的 8 维均值向量。
            covariance: 上一时刻目标状态的 8×8 协方差矩阵。

        返回:
            预测状态的均值向量和协方差矩阵。
        """
        std_pos = [
            self._std_weight_position * mean[3],
            self._std_weight_position * mean[3],
            1e-2,
            self._std_weight_position * mean[3],
        ]
        std_vel = [
            self._std_weight_velocity * mean[3],
            self._std_weight_velocity * mean[3],
            1e-5,
            self._std_weight_velocity * mean[3],
        ]
        motion_cov = np.diag(np.square(np.r_[std_pos, std_vel]))

        mean = np.dot(mean, self._motion_mat.T)
        covariance = np.linalg.multi_dot((
            self._motion_mat, covariance, self._motion_mat.T)) + motion_cov

        return mean, covariance

    def project(self, mean, covariance):
        """将状态分布投影到观测空间。

        参数:
            mean: 状态的 8 维均值向量。
            covariance: 状态的 8×8 协方差矩阵。

        返回:
            投影后的均值向量和协方差矩阵。
        """
        std = [
            self._std_weight_position * mean[3],
            self._std_weight_position * mean[3],
            1e-1,
            self._std_weight_position * mean[3],
        ]
        innovation_cov = np.diag(np.square(std))

        mean = np.dot(self._update_mat, mean)
        covariance = np.linalg.multi_dot((
            self._update_mat, covariance, self._update_mat.T))
        return mean, covariance + innovation_cov

    def multi_predict(self, mean, covariance):
        """批量执行卡尔曼滤波预测步骤。

        参数:
            mean: 上一时刻目标状态的 N×8 均值矩阵。
            covariance: 上一时刻目标状态的 N×8×8 协方差矩阵。

        返回:
            预测状态的均值矩阵和协方差矩阵。
        """
        std_pos = [
            self._std_weight_position * mean[:, 3],
            self._std_weight_position * mean[:, 3],
            1e-2 * np.ones_like(mean[:, 3]),
            self._std_weight_position * mean[:, 3],
        ]
        std_vel = [
            self._std_weight_velocity * mean[:, 3],
            self._std_weight_velocity * mean[:, 3],
            1e-5 * np.ones_like(mean[:, 3]),
            self._std_weight_velocity * mean[:, 3],
        ]
        sqr = np.square(np.r_[std_pos, std_vel]).T

        motion_cov = []
        for i in range(len(mean)):
            motion_cov.append(np.diag(sqr[i]))
        motion_cov = np.asarray(motion_cov)

        mean = np.dot(mean, self._motion_mat.T)
        left = np.dot(self._motion_mat, covariance).transpose((1, 0, 2))
        covariance = np.dot(left, self._motion_mat.T) + motion_cov

        return mean, covariance

    def update(self, mean, covariance, measurement):
        """执行卡尔曼滤波校正步骤。

        参数:
            mean: 预测状态的 8 维均值向量。
            covariance: 状态的 8×8 协方差矩阵。
            measurement: 4 维观测向量 ``(x, y, a, h)``。

        返回:
            根据观测校正后的状态分布。
        """
        projected_mean, projected_cov = self.project(mean, covariance)

        chol_factor, lower = scipy.linalg.cho_factor(
            projected_cov, lower=True, check_finite=False)
        kalman_gain = scipy.linalg.cho_solve(
            (chol_factor, lower), np.dot(covariance, self._update_mat.T).T,
            check_finite=False).T
        innovation = measurement - projected_mean

        new_mean = mean + np.dot(innovation, kalman_gain.T)
        new_covariance = covariance - np.linalg.multi_dot((
            kalman_gain, projected_cov, kalman_gain.T))
        return new_mean, new_covariance

    def gating_distance(
        self,
        mean,
        covariance,
        measurements,
        only_position=False,
        metric='maha',
    ):
        """计算状态分布与观测之间的门控距离。

        当 ``only_position`` 为假时使用 4 个自由度，否则使用 2 个自由度。
        支持平方欧氏距离 ``gaussian`` 和平方马氏距离 ``maha``。

        参数:
            mean: 状态分布的 8 维均值向量。
            covariance: 状态分布的 8×8 协方差矩阵。
            measurements: N×4 观测矩阵，格式为 ``(x, y, a, h)``。
            only_position: 是否仅根据边界框中心位置计算距离。
            metric: 距离度量方式。

        返回:
            长度为 N 的距离数组。
        """
        mean, covariance = self.project(mean, covariance)
        if only_position:
            mean, covariance = mean[:2], covariance[:2, :2]
            measurements = measurements[:, :2]

        d = measurements - mean
        if metric == 'gaussian':
            return np.sum(d * d, axis=1)
        elif metric == 'maha':
            cholesky_factor = np.linalg.cholesky(covariance)
            z = scipy.linalg.solve_triangular(
                cholesky_factor,
                d.T,
                lower=True,
                check_finite=False,
                overwrite_b=True,
            )
            squared_maha = np.sum(z * z, axis=0)
            return squared_maha
        else:
            raise ValueError('无效的距离度量方式')
