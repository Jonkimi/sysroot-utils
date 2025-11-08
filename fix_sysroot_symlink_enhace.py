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
from pathlib import Path
from typing import Dict, Set


class SymlinkFixer:
    def __init__(self, sysroot_dir: Path, dry_run: bool = False, verbose: bool = False):
        self.sysroot_dir = sysroot_dir.resolve()
        self.dry_run = dry_run
        self.verbose = verbose
        self.symlink_map: Dict[Path, str] = {}
        self.visited_links: Set[Path] = set()

    def log(self, message: str) -> None:
        if self.verbose:
            print(message)

    def collect_all_symlinks(self) -> None:
        """收集所有符号链接及其目标"""
        self.log("收集所有符号链接信息...")
        for root, _, files in os.walk(self.sysroot_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_symlink():
                    target = os.readlink(file_path)
                    self.symlink_map[file_path] = target

    def resolve_final_target(
        self, link_path: Path, original_target: str, depth: int = 0
    ) -> str:
        """解析链接的最终目标，处理链接级联"""
        if depth > 100:  # 防止无限递归
            return original_target

        if link_path in self.visited_links:
            return original_target

        self.visited_links.add(link_path)

        try:
            # 如果是绝对路径，调整为相对于sysroot的路径
            if os.path.isabs(original_target):
                adjusted_target = self.sysroot_dir / str(original_target).lstrip("/")
            else:
                adjusted_target = (link_path.parent / original_target).resolve()

            # 移除sysroot前缀
            if str(adjusted_target).startswith(str(self.sysroot_dir)):
                relative_path = str(adjusted_target)[len(str(self.sysroot_dir)) :]
                adjusted_target = Path("/" + relative_path.lstrip("/"))

            # 检查这个目标是否也是一个符号链接
            target_in_sysroot = self.sysroot_dir / str(adjusted_target).lstrip("/")
            if target_in_sysroot.is_symlink():
                next_target = os.readlink(target_in_sysroot)
                return self.resolve_final_target(
                    target_in_sysroot, next_target, depth + 1
                )

            return str(adjusted_target)

        finally:
            self.visited_links.discard(link_path)

    def fix_symlinks(self) -> None:
        """修复所有符号链接"""
        self.collect_all_symlinks()

        self.log("开始修复符号链接...")
        for link_path, original_target in self.symlink_map.items():
            self.visited_links.clear()
            final_target = self.resolve_final_target(link_path, original_target)

            if not self.dry_run:
                temp_link = link_path.with_name(link_path.name + ".tmp")
                try:
                    os.symlink(final_target, temp_link)
                    link_path.unlink()
                    temp_link.rename(link_path)
                    self.log(f"修复链接: {link_path} -> {final_target}")
                except Exception as e:
                    print(f"修复链接 {link_path} 时出错: {e}")
                    if temp_link.exists():
                        temp_link.unlink()
            else:
                self.log(f"将修复链接: {link_path} -> {final_target}")


def main():
    parser = argparse.ArgumentParser(description="修复sysroot中的符号链接")
    parser.add_argument("sysroot_dir", type=Path, help="sysroot目录路径")
    parser.add_argument("-n", "--dry-run", action="store_true", help="演示模式")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")

    args = parser.parse_args()

    if not args.sysroot_dir.is_dir():
        print(f"错误：{args.sysroot_dir} 不是一个有效的目录")
        return 1

    fixer = SymlinkFixer(args.sysroot_dir, args.dry_run, args.verbose)
    fixer.fix_symlinks()
    print("操作完成")


if __name__ == "__main__":
    main()
