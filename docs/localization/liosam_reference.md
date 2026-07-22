# LIO-SAM 参考与接口映射

## 1. 参考目录

本阶段只读参考：`D:\dachuang\github-source\LIO-SAM`，源码实际位于其 `LIO-SAM-master` 子目录。参考目录未被修改，也没有被复制或导入到 `rescue-system`。

## 2. LIO-SAM 简介

LIO-SAM 是 ROS1 下的 LiDAR-Inertial Odometry 系统。其工程结构把点云投影与去畸变、特征处理、里程计、地图优化和 IMU 预积分组织为相互协作的模块，并通过参数文件和 ROS 话题连接数据。`rescue-system` 本阶段只复用这种边界划分思想，不实现其中的算法。

## 3. 输入数据说明

### LiDAR

参考实现要求点云具备：

- 扫描时间戳；
- 点级相对时间，常见字段名为 `time`；
- 激光线号，常见字段名为 `ring`；
- 点坐标序列。

这些字段用于真实系统的点云去畸变和扫描组织。在 `rescue-system` 中，`LioSAMAdapter` 将 `points`、`point_time`/`time`、`ring`/`rings` 规范化为统一字典。

### IMU

输入至少表达：

- 时间戳；
- 三轴角速度；
- 三轴线性加速度；
- 传感器坐标系。

适配器统一保留 `angular_velocity`、`linear_acceleration`，并提供 `gyro`、`accel` 别名。

## 4. 输出数据说明

LIO-SAM 对外可抽象为带时间戳和坐标系关系的 LiDAR/IMU 里程计位姿。`rescue-system` 使用 `PoseEstimate` 表达：

- `position`：来自 `PoseState` 的 `(x, y, z)`；
- `orientation`：当前模型的 `(roll, pitch, yaw)`；
- `timestamp`；
- `frame_id`；
- `source`；
- 可选 `covariance`。

如果未来外部后端返回四元数，转换工作放在 Adapter 边界，内部模型接口保持稳定。本阶段的 Mock 后端只返回身份位姿。

## 5. 与 rescue-system 的接口映射

| LIO-SAM 概念 | rescue-system 接口 |
| --- | --- |
| LiDAR 点云话题 | `SensorData(sensor_type="lidar")` |
| IMU 话题 | `SensorData(sensor_type="imu")` |
| 点云字段转换 | `LioSAMAdapter.process_pointcloud()` |
| IMU 字段转换 | `LioSAMAdapter.process_imu()` |
| 算法调用边界 | `LioSAMBackend` |
| 统一位姿 | `PoseEstimate` |
| 上层保存与状态 | `LocalizationManager` |

## 6. 为什么使用 Adapter 隔离

Adapter 隔离外部算法的数据格式、话题命名和坐标约定，使 Manager、Planning 和模型层不需要知道 LIO-SAM 的 ROS 消息或 C++ 类型。未来替换为其他 LiDAR-SLAM 后端时，只需实现同一 Backend/Adapter 协议，不需要修改 Manager。

本阶段明确不包含：点云匹配、ICP、因子图优化、IMU 预积分、ROS2 节点和真实 LIO-SAM 调用。
