# yai-loguru-sinks 测试框架

本项目采用分层测试策略，确保代码质量和功能完整性。测试框架基于 pytest，支持单元测试、集成测试和端到端测试。

## 📁 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和共享 fixtures
├── test_basic.py            # 基础功能测试
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_core.py         # 核心功能单元测试
│   ├── test_data.py         # 数据结构单元测试
│   └── test_factory.py      # 工厂函数单元测试
├── integration/             # 集成测试
│   ├── __init__.py
│   └── test_sls_integration.py  # SLS 集成测试
└── e2e/                     # 端到端测试
    ├── __init__.py
    └── test_user_scenarios.py   # 用户场景测试
```

## 🧪 测试类型

### 单元测试 (Unit Tests)
- **目标**: 测试独立模块的功能
- **特点**: 快速执行，不依赖外部服务
- **覆盖**: 数据结构、核心逻辑、工厂函数
- **标记**: `@pytest.mark.unit`

### 集成测试 (Integration Tests)
- **目标**: 测试模块间的协作
- **特点**: 验证完整工作流程
- **覆盖**: SLS 协议解析、字段映射、异步处理
- **标记**: `@pytest.mark.integration`

### 端到端测试 (E2E Tests)
- **目标**: 测试完整用户场景
- **特点**: 模拟真实使用情况
- **覆盖**: 配置文件、环境变量、微服务场景
- **标记**: `@pytest.mark.e2e`

## 🚀 快速开始

### 安装依赖
```bash
# 在项目根目录
uv sync
```

### 运行测试

#### 使用测试运行器（推荐）
```bash
# 运行单元测试
python run_tests.py --unit

# 运行集成测试
python run_tests.py --integration

# 运行端到端测试
python run_tests.py --e2e

# 运行所有测试
python run_tests.py --all

# 运行快速测试（排除慢速测试）
python run_tests.py --fast

# 生成覆盖率报告
python run_tests.py --all --coverage

# 详细输出
python run_tests.py --unit --verbose

# 并行测试
python run_tests.py --unit --parallel 4

# 运行特定文件
python run_tests.py --file test_core.py

# 运行匹配模式的测试
python run_tests.py --pattern "test_sls*"

# 只运行上次失败的测试
python run_tests.py --failed
```

#### 直接使用 pytest
```bash
# 运行单元测试
uv run pytest -m unit

# 运行集成测试
uv run pytest -m integration

# 运行端到端测试
uv run pytest -m e2e

# 运行所有测试
uv run pytest

# 生成覆盖率报告
uv run pytest --cov=yai_loguru_sinks --cov-report=html

# 详细输出
uv run pytest -v

# 并行测试（需要 pytest-xdist）
uv run pytest -n auto
```

## 📊 覆盖率报告

测试覆盖率目标：**85%+**

当前覆盖率：
- **总体覆盖率**: 85%
- **核心模块**: 96%
- **数据结构**: 100%
- **工厂函数**: 100%

### 查看覆盖率报告
```bash
# 生成 HTML 报告
python run_tests.py --all --coverage

# 打开 HTML 报告
open htmlcov/index.html
```

## 🏷️ 测试标记

项目使用以下 pytest 标记：

- `unit`: 单元测试
- `integration`: 集成测试
- `e2e`: 端到端测试
- `slow`: 慢速测试（运行时间 > 1秒）
- `network`: 需要网络连接的测试
- `sls`: 需要阿里云 SLS 的测试

### 运行特定标记的测试
```bash
# 运行单元测试
pytest -m unit

# 运行非慢速测试
pytest -m "not slow"

# 运行 SLS 相关测试
pytest -m sls

# 组合标记
pytest -m "unit and not slow"
```

## 🛠️ 测试配置

### pytest.ini
项目配置文件包含：
- 测试发现规则
- 输出格式配置
- 覆盖率设置
- 标记定义
- 警告过滤

### conftest.py
共享测试配置包含：
- Mock fixtures（模拟 SLS SDK）
- 环境变量管理
- 临时目录创建
- 测试数据准备

## 🧩 Fixtures

### 可用的 Fixtures

#### 模拟相关
- `mock_aliyun_sdk`: 模拟阿里云 SDK
- `mock_socket`: 模拟网络操作

#### 配置相关
- `sls_config`: SLS 配置对象
- `sample_env_vars`: 示例环境变量
- `clean_env`: 清理环境变量

#### 文件系统
- `temp_dir`: 临时目录

### 使用示例
```python
def test_example(mock_aliyun_sdk, sls_config, temp_dir):
    """使用多个 fixtures 的测试示例"""
    # mock_aliyun_sdk 自动模拟阿里云 SDK
    # sls_config 提供预配置的 SLS 配置
    # temp_dir 提供临时目录路径
    pass
```

## 📝 编写测试

### 测试命名规范
- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 测试结构
```python
import pytest
from unittest.mock import MagicMock

class TestYourModule:
    """测试模块描述"""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """测试基本功能"""
        # Arrange
        # Act
        # Assert
        pass
    
    @pytest.mark.integration
    def test_integration_scenario(self, mock_aliyun_sdk):
        """测试集成场景"""
        pass
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_end_to_end_scenario(self, temp_dir):
        """测试端到端场景"""
        pass
```

### 最佳实践

1. **使用描述性的测试名称**
   ```python
   def test_sls_sink_handles_missing_credentials_gracefully(self):
   ```

2. **遵循 AAA 模式**
   ```python
   def test_example(self):
       # Arrange - 准备测试数据
       config = SlsConfig(...)
       
       # Act - 执行被测试的操作
       result = create_sls_sink(config)
       
       # Assert - 验证结果
       assert callable(result)
   ```

3. **使用适当的标记**
   ```python
   @pytest.mark.unit
   @pytest.mark.parametrize("input,expected", [("a", "b"), ("c", "d")])
   def test_with_parameters(self, input, expected):
   ```

4. **模拟外部依赖**
   ```python
   @patch('yai_loguru_sinks.internal.core.LogClient')
   def test_with_mock(self, mock_client):
   ```

## 🔧 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保在正确的目录
   cd packages/yai-loguru-sinks
   
   # 重新安装依赖
   uv sync
   ```

2. **测试失败**
   ```bash
   # 详细输出
   python run_tests.py --unit --verbose
   
   # 进入调试模式
   python run_tests.py --unit --pdb
   ```

3. **覆盖率问题**
   ```bash
   # 检查覆盖率配置
   cat pytest.ini
   
   # 重新生成报告
   python run_tests.py --all --coverage
   ```

### 调试技巧

1. **使用 pytest 的调试功能**
   ```bash
   pytest --pdb  # 失败时进入调试器
   pytest -s     # 显示 print 输出
   pytest -v     # 详细输出
   ```

2. **查看具体错误**
   ```bash
   pytest --tb=long  # 完整错误追踪
   pytest --tb=short # 简短错误追踪
   ```

3. **运行特定测试**
   ```bash
   pytest tests/unit/test_core.py::TestSlsSink::test_init
   ```

## 📈 持续集成

项目配置了 GitHub Actions CI/CD 流水线：

- **触发条件**: Push 和 Pull Request
- **测试矩阵**: Python 3.8, 3.9, 3.10, 3.11
- **操作系统**: Ubuntu, macOS, Windows
- **检查项目**:
  - 代码格式（black, ruff）
  - 类型检查（mypy）
  - 测试覆盖率（pytest-cov）
  - 安全扫描（bandit）

## 🎯 测试策略

### 测试金字塔
```
    /\     E2E Tests (少量)
   /  \    - 用户场景
  /____\   - 配置集成
 /      \  
/________\ Integration Tests (适量)
\        / - 模块协作
 \______/  - 工作流程
  \    /   
   \__/    Unit Tests (大量)
          - 函数逻辑
          - 数据结构
```

### 覆盖率目标
- **单元测试**: 90%+
- **集成测试**: 80%+
- **端到端测试**: 70%+
- **总体覆盖率**: 85%+

### 性能基准
- **单元测试**: < 0.1秒/测试
- **集成测试**: < 1秒/测试
- **端到端测试**: < 5秒/测试
- **总测试时间**: < 30秒

## 📚 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-cov 覆盖率插件](https://pytest-cov.readthedocs.io/)
- [Python 测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [测试驱动开发 (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)

---

**维护者**: yai-loguru-sinks 开发团队  
**更新时间**: 2024年12月  
**版本**: 1.0.0