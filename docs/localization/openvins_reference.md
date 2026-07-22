# OpenVINS 参考与 rescue-system 接口映射

## 1. OpenVINS 简介

OpenVINS 是面向视觉惯性估计研究的开源系统。其核心由相机数据、IMU 数据、特征跟踪、初始化和 MSCKF/EKF 状态估计等部分组成，并通过统一管理器把传感器测量送入估计器。

本项目只参考其输入组织、时间戳约定、输出概念和配置分层，不复制源码、不直接依赖 OpenVINS，也不在 rescue-system 内实现 VIO 算法。

## 2. Camera 输入说明

OpenVINS 的相机测量按一帧组织，核心信息包括：

- `timestamp`：图像采集时间，使用秒作为统一接口单位。
- `sensor_ids`：参与该帧的相机编号列表。
- `images`：与 `sensor_ids` 一一对应的原始图像列表。
- `masks`：可选的图像掩码列表。

rescue-system 的 `OpenVINSAdapter` 将 `SensorData.data` 规范化为：

```text
{
    "timestamp": float,
    "sensor_ids": tuple[int, ...],
    "images": tuple[object, ...],
    "masks": tuple[object, ...],
}
```

适配器只做容器转换和边界校验，不读取硬件、不处理图像、不提取特征。

## 3. IMU 输入说明

OpenVINS 的单次 IMU 测量包含：

- `timestamp`：测量时间。
- `wm`：三轴角速度，单位为 rad/s。
- `am`：三轴线性加速度，单位为 m/s²。

rescue-system 接受 `angular_velocity`/`linear_acceleration`、`gyro`/`accel` 或六元素序列，并规范化为：

```text
{
    "timestamp": float,
    "wm": (wx, wy, wz),
    "am": (ax, ay, az),
    "angular_velocity": (wx, wy, wz),
    "linear_acceleration": (ax, ay, az),
}
```

三轴校验只保证类型、长度和有限数值，不执行预积分、偏置估计或融合。

## 4. Pose 输出说明

OpenVINS 的状态输出概念上包含时间、位置、姿态、速度、偏置和不确定性等信息。rescue-system 当前阶段只承接规划所需的最小统一结果：

- `PoseEstimate.timestamp`
- `PoseEstimate.frame_id`
- `PoseEstimate.pose.x/y/z`
- `PoseEstimate.pose.roll/pitch/yaw`
- `PoseEstimate.covariance`
- `PoseEstimate.source`

`PoseEstimate.position` 和 `PoseEstimate.orientation` 提供只读访问，分别返回位置三元组和欧拉姿态三元组。当前 OpenVINS 后端返回身份位姿占位结果，仅用于验证接口，不代表真实估计。

## 5. OpenVINS 与 rescue-system 接口映射

| OpenVINS 概念 | rescue-system 接口 |
| --- | --- |
| `ImuData.timestamp` | `SensorData.timestamp` |
| `ImuData.wm` | `SensorData.data["wm"]` |
| `ImuData.am` | `SensorData.data["am"]` |
| `CameraData.timestamp` | `SensorData.timestamp` |
| `CameraData.sensor_ids` | `SensorData.data["sensor_ids"]` |
| `CameraData.images` | `SensorData.data["images"]` |
| `CameraData.masks` | `SensorData.data["masks"]` |
| VIO 状态时间 | `PoseEstimate.timestamp` |
| VIO 位置和姿态 | `PoseEstimate.pose` |
| 估计坐标系 | `PoseEstimate.frame_id` |
| 状态不确定性 | `PoseEstimate.covariance` |

数据流保持为：

```text
Camera / IMU
    ↓
OpenVINSAdapter
    ↓
OpenVINSBackend 接口
    ↓
PoseEstimate
    ↓
LocalizationManager
    ↓
Planning
```

## 6. 为什么采用 Adapter 隔离

Adapter 将外部算法的数据结构隔离在定位模块边界内，使 `LocalizationManager`、`PoseEstimate` 和 Planning 不需要知道 OpenVINS 的 C++ 类型、图像库或构建方式。未来更换为其他 VIO、视觉 SLAM 或 LiDAR SLAM 后端时，只需实现对应 Adapter/Backend，不需要修改上层数据流。

## 7. 参考范围与限制

本说明依据本地 OpenVINS 参考目录中的 `sensor_data.h`、`VioManager.h`、配置文件和相关输出接口整理。未复制源码，未修改参考目录，rescue-system 也不直接 import OpenVINS。
