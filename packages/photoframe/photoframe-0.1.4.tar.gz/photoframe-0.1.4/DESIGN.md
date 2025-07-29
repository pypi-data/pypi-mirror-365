# Watermarker CLI Tool - 技术设计文档

## 1. 项目概述

一个基于 Python 的 CLI 工具，用于为照片添加水印并输出无损照片，支持多种模板和自动方向检测。

**使用方式**:
```bash
uvx watermarker 文件名.常用图片格式 --template date 
```

**核心特性**:
- 支持常用图片格式 (JPEG, PNG, TIFF, HEIC)
- 无损输出，保持原始质量
- 多种水印模板
- 自动判断横竖拍方向
- 提取并利用 EXIF 元数据

## 2. 架构设计

### 2.1 核心组件
- **CLI 接口**: 基于 Click 的命令行界面
- **图像处理**: Pillow (PIL) 进行图像操作
- **模板引擎**: 模块化模板系统支持不同水印样式
- **EXIF 处理器**: 提取元数据（日期、相机设置、GPS）
- **输出管理器**: 无损图像输出，保留元数据

### 2.2 项目结构
```
watermarker/
├── src/
│   └── watermarker/
│       ├── __init__.py
│       ├── cli.py              # CLI 接口
│       ├── core/
│       │   ├── __init__.py
│       │   ├── processor.py    # 主要图像处理
│       │   ├── exif_reader.py  # EXIF 数据提取
│       │   └── utils.py        # 工具函数
│       ├── templates/
│       │   ├── __init__.py
│       │   ├── base.py         # 基础模板类
│       │   ├── date.py         # 日期水印模板
│       │   ├── baby.py         # 宝宝年龄模板
│       │   └── camera.py       # 相机参数模板
│       └── fonts/              # 字体文件
├── tests/
├── pyproject.toml
├── README.md
└── DESIGN.md
```

## 3. CLI 接口设计

### 3.1 命令结构
```bash
uvx watermarker <input_file> [options]
```

### 3.2 参数设计

**位置参数**:
- `input_file`: 输入图像文件路径

**选项参数**:
- `--template, -t`: 模板类型 (date, baby, camera) [默认: date]
- `--output, -o`: 输出文件路径 [默认: 自动生成]
- `--position`: 水印位置 (bottom-right, bottom-left, bottom-center) [默认: bottom-right]
- `--opacity`: 水印透明度 (0.0-1.0) [默认: 0.8]
- `--font-size`: 字体大小倍数 [默认: 1.0]
- `--color`: 文本颜色 [默认: white]
- `--baby-birth-date`: 宝宝出生日期 (YYYY-MM-DD)
- `--custom-text`: 自定义水印文本
- `--dry-run`: 预览模式，不保存文件

### 3.3 使用示例
```bash
# 基础日期水印
uvx watermarker photo.jpg --template date

# 宝宝照片带年龄
uvx watermarker baby_photo.jpg --template baby --baby-birth-date 2024-01-15

# 相机参数水印
uvx watermarker landscape.jpg --template camera --position bottom-center

# 自定义位置和透明度
uvx watermarker photo.jpg --template date --position bottom-left --opacity 0.6

# 预览模式
uvx watermarker photo.jpg --template date --dry-run
```

## 4. 技术实现

### 4.1 项目依赖
```toml
dependencies = [
    "click>=8.1.0",           # CLI 框架
    "Pillow>=10.0.0",         # 图像处理
    "exifread>=3.0.0",        # EXIF 数据读取
    "python-dateutil>=2.8.0", # 日期处理
]
```

### 4.2 核心类设计

#### 4.2.1 ImageProcessor - 图像处理器
```python
class ImageProcessor:
    def __init__(self, image_path: str)
    def load_image(self) -> Image
    def get_orientation(self) -> str  # landscape/portrait
    def apply_watermark(self, template: BaseTemplate) -> Image
    def save_lossless(self, output_path: str) -> None
    def preview(self) -> None  # 预览功能
```

#### 4.2.2 BaseTemplate - 基础模板类
```python
class BaseTemplate:
    def generate_text(self, exif_data: dict) -> str
    def get_font_size(self, image_size: tuple) -> int
    def get_position(self, image_size: tuple, text_size: tuple) -> tuple
    def render(self, image: Image, **kwargs) -> Image
    def validate_requirements(self, exif_data: dict) -> bool
```

#### 4.2.3 ExifReader - EXIF 读取器
```python
class ExifReader:
    def __init__(self, image_path: str)
    def get_datetime(self) -> datetime
    def get_camera_info(self) -> dict
    def get_lens_info(self) -> dict
    def get_settings(self) -> dict  # ISO, 光圈, 快门
    def get_gps_info(self) -> dict
```

### 4.3 模板实现

#### 4.3.1 DateTemplate - 日期模板
```python
class DateTemplate(BaseTemplate):
    """
    基础日期水印模板
    输出格式: "2024.05.15"
    特性:
    - 从 EXIF 提取拍摄日期
    - 支持自定义日期格式
    - 自动根据方向调整位置
    """
```

#### 4.3.2 BabyTemplate - 宝宝年龄模板  
```python
class BabyTemplate(BaseTemplate):
    """
    宝宝照片年龄模板
    输出格式: "2024.05.15 · 4个月3天"
    特性:
    - 根据出生日期和拍摄日期计算年龄
    - 支持月龄、天数显示
    - 支持中英文显示
    """
```

#### 4.3.3 CameraTemplate - 相机参数模板
```python
class CameraTemplate(BaseTemplate):
    """
    相机参数模板（类似徕卡相框）
    输出格式: "LEICA Q2 · 28mm f/1.4 ISO100 1/60s"
    特性:
    - 显示相机型号、镜头、设置
    - 模仿徕卡相机显示风格
    - 自动格式化参数显示
    """
```

## 5. 图像处理策略

### 5.1 无损输出
- 保留原始 EXIF 数据
- 使用高质量图像处理
- 支持 JPEG, PNG, TIFF, HEIC 输入格式
- 维持原始质量和色彩配置

### 5.2 字体处理
- 内置开源字体 (Noto Sans 系列)
- 根据图像分辨率自动缩放
- 支持中文字符显示
- 字体回退机制

### 5.3 定位算法
- 基于相对位置计算 (如距离边缘 5% 边距)
- 自动适应不同宽高比
- 确保文本不遮挡重要内容
- 支持横竖拍自动调整

## 6. 配置与扩展性

### 6.1 配置文件支持
可选的 `~/.watermarker/config.yaml`:
```yaml
default_template: date
default_position: bottom-right
default_opacity: 0.8
baby_birth_date: "2024-01-15"
fonts:
  default: "NotoSans-Regular.ttf"
  chinese: "NotoSansCJK-Regular.ttf"
date_format: "%Y.%m.%d"
```

### 6.2 自定义模板
- 插件系统支持用户定义模板
- 通过 entry points 发现模板
- 简单情况支持 JSON/YAML 模板定义

## 7. 错误处理与验证

### 7.1 输入验证
- 文件格式验证
- 文件存在性和可读性检查
- 参数范围验证
- 依赖关系检查

### 7.2 错误处理
- EXIF 数据可用性检查
- 缺失元数据的优雅回退
- 清晰的错误消息和建议
- 详细的调试信息选项

## 8. 性能考虑

### 8.1 优化策略
- 字体和资源延迟加载
- 内存高效的图像处理
- 未来批处理能力支持
- 大文件进度指示器

### 8.2 资源管理
- 自动内存释放
- 临时文件清理
- 字体缓存机制

## 9. 测试策略

### 9.1 测试类型
- 各模板单元测试
- 示例图像集成测试
- EXIF 数据解析测试
- 输出质量验证
- CLI 接口测试

### 9.2 测试数据
- 不同格式的示例图像
- 各种 EXIF 数据场景
- 横竖拍测试用例
- 边界条件测试

## 10. 未来增强

### 10.1 短期计划
- 批量处理多个文件
- 更多自定义选项
- 性能优化

### 10.2 长期愿景
- 视频水印支持
- 云存储集成
- GUI 版本
- 模板市场

## 11. 部署与分发

### 11.1 打包策略
- 使用 uv 进行包管理
- 支持 `uvx watermarker` 直接运行
- 跨平台兼容性

### 11.2 依赖管理
- 最小化外部依赖
- 确保版本兼容性
- 提供离线字体支持

---

本设计文档为 watermarker CLI 工具提供了完整的技术架构和实现指南，确保项目的专业性、可扩展性和用户友好性。