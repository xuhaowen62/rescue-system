# Localization 系统接口集成说明

## 1. 模块职责

Localization 只负责输出统一定位结果：

- `PoseEstimate`：机器人位置、姿态、时间戳和坐标系。
- `Transform`：坐标系之间的刚体变换。
- `LocalizationStatus`：定位生命周期和健康状态。

Localization 不负责路径规划、可通过性分析或控制算法。

## 2. 统一数据流

```text
Perception / Sensor
        ↓
Localization Adapter / Backend
        ↓
PoseEstimate + Transform + LocalizationStatus
        ├── LocalizationPlanningAdapter
        │       ↓
        │   Planning Pose
        │       ↓
        │   PlanningManager
        │
        └── LocalizationTraversabilityAdapter
                ↓
            Robot Position / Transform / Timestamp
                ↓
            Traversability
```

## 3. Planning如何接收定位结果

`LocalizationPlanningAdapter` 从 `LocalizationManager` 读取当前 `PoseEstimate`，转换为
Planning 已有的 `planning.models.Pose`，不修改 Planning 内部模型和管理流程。

```python
planning_adapter = LocalizationPlanningAdapter(localization_manager)
start_pose = planning_adapter.get_pose()
```

当没有有效定位结果时，适配器返回 `None`，由上层决定是否等待或终止规划请求。

## 4. Traversability如何接收定位结果

`LocalizationTraversabilityAdapter` 提供：

- `get_pose()`：当前 `PoseEstimate`。
- `get_robot_position()`：当前 `(x, y, z)`。
- `get_transform()`：当前坐标变换。
- `get_time_sync_info()`：时间戳、坐标系和数据来源。

Traversability 仍然负责可通过性结果和Cost，不由Localization计算。

## 5. 状态接口

通过以下接口查询状态：

```python
state = localization_manager.get_localization_state()
```

支持状态包括：

- `INITIALIZING`
- `RUNNING`
- `LOST`
- `FAILED`

同时兼容已有的 `IDLE`、`READY`、`NO_POSE` 和 `NO_SENSOR_DATA` 状态。

## 6. 边界约束

本阶段只完成接口集成，不实现：

- SLAM/VIO算法。
- LIO优化。
- ROS2节点。
- 控制算法。
- Traversability算法。
