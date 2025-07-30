#!/usr/bin/env python3
"""
测试运行脚本

提供便捷的测试运行命令，支持不同类型和级别的测试。
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """运行命令并处理结果"""
    print(f"\n🚀 {description}")
    print(f"📝 命令: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败 (退出码: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"❌ 命令未找到: {cmd[0]}")
        print("请确保已安装 pytest 和相关依赖")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="yai-loguru-sinks 测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_tests.py --unit              # 运行单元测试
  python run_tests.py --integration       # 运行集成测试
  python run_tests.py --e2e               # 运行端到端测试
  python run_tests.py --all               # 运行所有测试
  python run_tests.py --fast              # 运行快速测试（排除慢速测试）
  python run_tests.py --coverage          # 运行测试并生成覆盖率报告
  python run_tests.py --verbose           # 详细输出
  python run_tests.py --file test_core.py # 运行特定文件
        """
    )
    
    # 测试类型选项
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--unit', action='store_true', help='运行单元测试')
    test_group.add_argument('--integration', action='store_true', help='运行集成测试')
    test_group.add_argument('--e2e', action='store_true', help='运行端到端测试')
    test_group.add_argument('--all', action='store_true', help='运行所有测试')
    test_group.add_argument('--fast', action='store_true', help='运行快速测试（排除慢速测试）')
    
    # 其他选项
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--parallel', '-n', type=int, help='并行测试进程数')
    parser.add_argument('--file', '-f', help='运行特定测试文件')
    parser.add_argument('--pattern', '-k', help='运行匹配模式的测试')
    parser.add_argument('--failed', action='store_true', help='只运行上次失败的测试')
    parser.add_argument('--pdb', action='store_true', help='测试失败时进入调试器')
    
    args = parser.parse_args()
    
    # 检查是否在正确的目录
    if not Path('pytest.ini').exists():
        print("❌ 请在包含 pytest.ini 的目录中运行此脚本")
        print("当前目录:", Path.cwd())
        return 1
    
    # 构建 pytest 命令
    cmd = ['python', '-m', 'pytest']
    
    # 添加测试类型标记
    if args.unit:
        cmd.extend(['-m', 'unit'])
        description = "单元测试"
    elif args.integration:
        cmd.extend(['-m', 'integration'])
        description = "集成测试"
    elif args.e2e:
        cmd.extend(['-m', 'e2e'])
        description = "端到端测试"
    elif args.fast:
        cmd.extend(['-m', 'not slow'])
        description = "快速测试"
    elif args.all:
        description = "所有测试"
    else:
        # 默认运行单元测试
        cmd.extend(['-m', 'unit'])
        description = "单元测试（默认）"
    
    # 添加特定文件
    if args.file:
        cmd.append(args.file)
        description += f" ({args.file})"
    
    # 添加模式匹配
    if args.pattern:
        cmd.extend(['-k', args.pattern])
        description += f" (模式: {args.pattern})"
    
    # 添加其他选项
    if args.verbose:
        cmd.append('-vv')
    
    if args.parallel:
        cmd.extend(['-n', str(args.parallel)])
    
    if args.failed:
        cmd.append('--lf')
        description += " (仅失败的测试)"
    
    if args.pdb:
        cmd.append('--pdb')
    
    if args.coverage:
        cmd.extend([
            '--cov=yai_loguru_sinks',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov'
        ])
        description += " (包含覆盖率)"
    
    # 运行测试
    success = run_command(cmd, description)
    
    if success:
        print("\n🎉 测试运行完成！")
        
        if args.coverage:
            print("\n📊 覆盖率报告:")
            print("  - 终端报告: 已显示在上方")
            print("  - HTML报告: htmlcov/index.html")
            
            # 尝试打开覆盖率报告
            html_report = Path('htmlcov/index.html')
            if html_report.exists():
                print(f"  - 文件路径: {html_report.absolute()}")
        
        print("\n💡 提示:")
        print("  - 使用 --verbose 获取更详细的输出")
        print("  - 使用 --coverage 生成覆盖率报告")
        print("  - 使用 --help 查看所有选项")
        
        return 0
    else:
        print("\n💥 测试运行失败！")
        print("\n🔧 故障排除:")
        print("  1. 检查是否安装了所有依赖: uv sync")
        print("  2. 检查测试文件语法是否正确")
        print("  3. 使用 --verbose 获取更多错误信息")
        print("  4. 使用 --pdb 进入调试模式")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())