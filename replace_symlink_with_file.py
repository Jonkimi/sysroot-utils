# Copyright (c) 2025 Jonkimi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import os
import shutil
from pathlib import Path


def replace_symlinks(directory, dry_run=False, verbose=False):
    """
    递归替换目录中的所有符号链接为原始文件

    Args:
        directory: 要处理的目录路径
        dry_run: 如果为True，只显示将要执行的操作而不实际执行
        verbose: 是否显示详细信息
    """
    directory = Path(directory).resolve()

    def log(message):
        if verbose:
            print(message)

    def handle_symlink(symlink_path):
        try:
            # 获取符号链接的真实路径
            real_path = symlink_path.resolve()

            # 检查目标是否存在
            if not real_path.exists():
                log(f"警告: 符号链接 {symlink_path} 指向不存在的文件: {real_path}")
                return

            # 检查是否是文件而不是目录
            if not real_path.is_file():
                log(f"跳过: {symlink_path} 指向一个目录")
                return

            # 备份原始文件
            backup_path = Path(str(symlink_path) + ".bak")

            if not dry_run:
                # 创建备份
                shutil.copy2(real_path, backup_path)
                # 删除符号链接
                symlink_path.unlink()
                # 复制原始文件
                shutil.copy2(real_path, symlink_path)
                # 保持原始权限
                shutil.copymode(backup_path, symlink_path)
                # 删除备份
                backup_path.unlink()

            log(f"替换: {symlink_path} -> {real_path}")

        except Exception as e:
            print(f"错误: 处理 {symlink_path} 时出错: {e}")

    try:
        # 递归遍历目录
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)

            # 处理当前目录中的符号链接
            for name in files + dirs:
                file_path = root_path / name
                if file_path.is_symlink():
                    handle_symlink(file_path)

    except Exception as e:
        print(f"错误: 遍历目录 {directory} 时出错: {e}")


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="将目录中的符号链接替换为其指向的原始文件"
    )

    parser.add_argument("directory", help="要处理的目录路径")

    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="显示将要执行的操作而不实际执行"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="显示详细的操作信息"
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 获取要处理的目录的绝对路径
    directory = Path(args.directory).resolve()

    # 检查目录是否存在
    if not directory.exists():
        print(f"错误: 目录不存在: {directory}")
        return

    if not directory.is_dir():
        print(f"错误: {directory} 不是一个目录")
        return

    # 显示操作模式
    if args.dry_run:
        print("运行在演示模式 (dry run) - 不会实际修改文件")

    # 执行替换操作
    try:
        replace_symlinks(directory, args.dry_run, args.verbose)
        print("操作完成")
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
