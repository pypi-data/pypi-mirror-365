# Watermarker

一个基于 Python 的 CLI 工具，用于为照片添加水印并输出无损照片。支持多种模板和自动方向检测。

## 特性

- 🖼️ **多格式支持**: 支持 JPEG, PNG, TIFF, HEIC 等常见图片格式
- 🏷️ **多种模板**: 日期水印、宝宝年龄、相机参数等
- 🔄 **自动方向**: 自动检测横竖拍并调整水印位置
- 📊 **EXIF 提取**: 智能提取拍摄日期、相机信息等元数据
- 💯 **无损输出**: 保持原始图片质量和元数据
- ⚙️ **高度可定制**: 支持位置、透明度、字体大小等自定义

## 安装

本地开发使用:
```bash
git clone <repository-url>
cd watermarker
uv sync
uv run watermarker --help
```

## 使用方法

### 基础用法

```bash
# 添加日期水印
uv run watermarker add photo.jpg

# 指定输出文件
uv run watermarker add photo.jpg --output photo_with_date.jpg

# 预览模式（不保存文件）
uv run watermarker add photo.jpg --dry-run
```

### 模板选项

#### 1. 日期模板（默认）
```bash
# 基础日期水印
uv run watermarker add photo.jpg --template date

# 自定义位置和透明度
uv run watermarker add photo.jpg --template date --position bottom-left --opacity 0.6
```

#### 2. 宝宝年龄模板
```bash
# 显示宝宝年龄（需要出生日期）
uv run watermarker add photos/1.jpg --template baby --baby-birth-date 2024-01-15

# 结果示例: "2024.05.15 · 4个月3天"
```

#### 3. 相机参数模板
```bash
# 显示相机参数（类似徕卡风格）
uv run watermarker add photo.jpg --template camera

# 结果示例: "LEICA Q2 · 28mm f/1.4 ISO100 1/60s"
```

### 高级选项

```bash
# 自定义文本
uv run watermarker add photo.jpg --custom-text "我的照片"

# 调整字体大小和颜色
uv run watermarker add photo.jpg --font-size 1.5 --color white

# 设置固定边距（像素）
uv run watermarker add photo.jpg --margin 60

# 详细输出
uv run watermarker add photo.jpg --verbose
```

### 查看图片信息

```bash
# 显示图片的 EXIF 信息
uv run watermarker info photo.jpg
```

## 参数说明

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--template, -t` | 模板类型 (date/baby/camera) | date |
| `--output, -o` | 输出文件路径 | 自动生成 |
| `--position` | 水印位置 (bottom-right/bottom-left/bottom-center) | bottom-right |
| `--opacity` | 透明度 (0.0-1.0) | 0.8 |
| `--font-size` | 字体大小倍数 | 1.0 |
| `--color` | 文本颜色 | white |
| `--margin` | 固定边距像素 (10-200) | 40 |
| `--baby-birth-date` | 宝宝出生日期 (YYYY-MM-DD) | - |
| `--custom-text` | 自定义水印文本 | - |
| `--dry-run` | 预览模式，不保存文件 | false |
| `--verbose, -v` | 显示详细信息 | false |

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)
- BMP (.bmp)
- WebP (.webp)

## 项目结构

```
watermarker/
├── src/watermarker/
│   ├── cli.py              # CLI 接口
│   ├── core/
│   │   ├── processor.py    # 图像处理
│   │   ├── exif_reader.py  # EXIF 读取
│   │   └── utils.py        # 工具函数
│   └── templates/
│       ├── base.py         # 基础模板
│       ├── date.py         # 日期模板
│       ├── baby.py         # 宝宝年龄模板
│       └── camera.py       # 相机参数模板
├── tests/                  # 测试文件
├── DESIGN.md              # 技术设计文档
└── README.md
```

## 示例输出

### 日期模板
- 简单日期: `2024.05.15`

### 宝宝年龄模板
- 月龄显示: `2024.05.15 · 4个月3天`
- 岁数显示: `2024.05.15 · 2岁3个月`

### 相机参数模板
- 徕卡风格: `LEICA Q2 · 28mm f/1.4 ISO100 1/60s`
- 紧凑风格: `Canon EOS R5 | 85mm | f/2.8, 1/200s, ISO400`

## 开发

### 运行测试
```bash
uv run pytest
```

### 代码格式化
```bash
uv run black src/
uv run isort src/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.1.0
- 初始版本
- 支持日期、宝宝年龄、相机参数三种模板
- 支持多种图片格式
- 无损输出功能