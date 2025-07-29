# PyPI 发布指南

本文档介绍如何将 photoframe 发布到 PyPI，使用户能够通过 `uvx` 直接使用。

## 前置准备

### 1. 注册 PyPI 账号

#### 正式环境
访问 [PyPI](https://pypi.org/account/register/) 注册账号

#### 测试环境（推荐先测试）
访问 [TestPyPI](https://test.pypi.org/account/register/) 注册测试账号

### 2. 配置 API Token

为了安全发布，建议使用 API Token 而非密码：

1. 登录 PyPI/TestPyPI
2. 进入 Account Settings > API tokens
3. 创建新的 API token
4. 保存 token（只显示一次）

### 3. 配置本地认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## 发布流程

### 第一步：构建包

```bash
# 确保在项目根目录
cd /path/to/watermarker

# 清理之前的构建
rm -rf dist/

# 构建新版本
uv build
```

构建成功后会在 `dist/` 目录生成：
- `photoframe-x.x.x.tar.gz` (源码包)
- `photoframe-x.x.x-py3-none-any.whl` (wheel包)

### 第二步：测试发布（推荐）

先发布到 TestPyPI 进行测试：

```bash
# 上传到测试环境
uv run twine upload --repository testpypi dist/*

# 等待几分钟让包索引更新，然后测试安装
uvx --index-url https://test.pypi.org/simple/ photoframe add --help
```

如果测试成功，可以继续正式发布。

### 第三步：正式发布

```bash
# 上传到正式 PyPI
uv run twine upload dist/*
```

## 版本管理

### 更新版本号

在 `pyproject.toml` 中更新版本号：

```toml
[project]
name = "photoframe"
version = "0.1.1"  # 更新这里
```

### 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- `0.1.0` → `0.1.1`: 补丁版本（bug修复）
- `0.1.0` → `0.2.0`: 次版本（新功能，向后兼容）
- `0.1.0` → `1.0.0`: 主版本（重大更改，可能不向后兼容）

### 发布新版本流程

```bash
# 1. 更新版本号
vim pyproject.toml

# 2. 提交更改
git add pyproject.toml
git commit -m "bump: version 0.1.1"
git tag v0.1.1

# 3. 构建并发布
rm -rf dist/
uv build
uv run twine upload dist/*

# 4. 推送到 Git
git push origin main --tags
```

## 用户使用方式

发布成功后，用户可以通过以下方式使用：

### 方式一：直接运行（推荐）

```bash
# 无需安装，直接使用
uvx photoframe add photo.jpg --template date

# 带参数的例子
uvx photoframe add photo.jpg --template baby --baby-birth-date 2024-01-15
```

### 方式二：安装后使用

```bash
# 安装工具
uv tool install photoframe

# 使用（命令名为 photoframe）
photoframe add photo.jpg --template date

# 更新工具
uv tool upgrade photoframe

# 卸载工具
uv tool uninstall photoframe
```

## 故障排除

### 常见问题

#### 1. 包名冲突
如果遇到包名已存在的错误，需要修改 `pyproject.toml` 中的 `name` 字段。

#### 2. 认证失败
检查 `~/.pypirc` 文件配置是否正确，确保 API token 有效。

#### 3. 构建失败
确保 `pyproject.toml` 中的包路径配置正确：

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/watermarker"]
```

#### 4. 依赖问题
确保所有依赖都在 `pyproject.toml` 中正确声明。

### 验证发布

发布后可以通过以下方式验证：

```bash
# 检查包信息
uvx photoframe --help

# 测试核心功能
uvx photoframe add test_image.jpg --template date --dry-run
```

## 自动化发布

可以考虑使用 GitHub Actions 自动化发布流程，在 `.github/workflows/publish.yml` 中配置。

## 相关链接

- [PyPI - photoframe](https://pypi.org/project/photoframe/)
- [TestPyPI - photoframe](https://test.pypi.org/project/photoframe/)
- [uv 文档](https://docs.astral.sh/uv/)
- [Python 打包指南](https://packaging.python.org/)