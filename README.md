# 基于多模态感知的异构协同搜救系统

## 项目范围
本项目目前只实现“找到人”这一部分，不包含找到人之后的交互功能。

## 最终入口结构
```text
D:\dachuang\rescue-system
?? main.py                  # 统一入口
?? configs\                 # 配置文件
?? models\
?  ?? weights\              # 模型权重
?  ?? exported\             # 导出的模型（按时间戳保存）
?? scripts\
?  ?? yolo_detect.py        # YOLO 人体检测主界面
?  ?? camera_detect.py      # 备用摄像头检测脚本
?  ?? data_capture.py       # 数据采集
?  ?? export_onnx.py        # 模型导出
?  ?? evaluate.py           # 评估脚本
?? utils\
?  ?? file_utils.py         # 统一时间戳/路径工具
?? data\
?? results\
?? notebooks\
```

## 统一运行方式
### 1. 人体检测
```powershell
python main.py --mode detect
```

### 2. 数据采集
```powershell
python main.py --mode capture
```

### 3. 模型导出
```powershell
python main.py --mode export
```

## 导出与保存规则
项目内所有输出文件统一遵循：
- **不覆盖旧文件**
- **自动按时间戳命名**
- **导出模型、截图、视频都遵守这个规则**

例如：
- `models/exported/yolov8n_20260705_153012_123456.onnx`
- `results/videos/output_20260705_153012_123456.mp4`
- `results/images/rescue_snapshot_20260705_153012_123456.png`

## 检测界面特点
`main.py --mode detect` 调用的是 `scripts/yolo_detect.py`，它现在已经是最终版控制台界面，包含：
- 头部状态栏
- 右侧信息面板
- 事件日志
- 录制状态提示
- 截图提示
- 只聚焦“找到人”功能

## 常用参数
- `--source 0`：摄像头
- `--source D:\path\video.mp4`：视频文件
- `--save results\videos\output.mp4`：保存结果视频（会自动变成时间戳文件名）
- `--mirror`：镜像画面
- `--show-all`：显示所有类别
- `--person-only`：仅显示 person

## 说明
- 你之前的 `yolo_detect1.py` 已经统一为 `scripts/yolo_detect.py`
- 以后如果要新增输出文件，建议直接使用 `utils/file_utils.py` 里的时间戳工具函数
