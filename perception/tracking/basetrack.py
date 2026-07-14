"""ByteTrack 基础轨迹类型定义。"""

from collections import OrderedDict

import numpy as np


class TrackState(object):
    """定义轨迹生命周期状态。"""

    New = 0
    Tracked = 1
    Lost = 2
    Removed = 3


class BaseTrack(object):
    """定义 ByteTrack 轨迹基类。"""

    _count = 0

    track_id = 0
    is_activated = False
    state = TrackState.New

    history = OrderedDict()
    features = []
    curr_feature = None
    score = 0
    start_frame = 0
    frame_id = 0
    time_since_update = 0

    # 多摄像机位置
    location = (np.inf, np.inf)

    @property
    def end_frame(self):
        """返回轨迹结束帧编号。"""
        return self.frame_id

    @staticmethod
    def next_id():
        """分配下一个轨迹编号。"""
        BaseTrack._count += 1
        return BaseTrack._count

    def activate(self, *args):
        """激活轨迹。"""
        raise NotImplementedError

    def predict(self):
        """预测轨迹下一时刻状态。"""
        raise NotImplementedError

    def update(self, *args, **kwargs):
        """使用新的观测更新轨迹。"""
        raise NotImplementedError

    def mark_lost(self):
        """将轨迹标记为丢失状态。"""
        self.state = TrackState.Lost

    def mark_removed(self):
        """将轨迹标记为移除状态。"""
        self.state = TrackState.Removed
