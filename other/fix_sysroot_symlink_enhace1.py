#!/usr/bin/env python3

import os
import argparse
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
                    # 将绝对路径转换为相对于sysroot的路径
                    if os.path.isabs(target):
                        rel_path = os.path.relpath(
                            self.sysroot_dir / target.lstrip("/"),
                            os.path.dirname(file_path),
                        )
                        self.symlink_map[file_path] = rel_path
                    else:
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
            # 解析目标路径
            if os.path.isabs(original_target):
                target_path = self.sysroot_dir / original_target.lstrip("/")
                rel_path = os.path.relpath(target_path, os.path.dirname(link_path))
            else:
                target_path = (link_path.parent / original_target).resolve()
                rel_path = original_target

            # 检查目标是否也是符号链接
            if target_path.is_symlink():
                next_target = os.readlink(target_path)
                return self.resolve_final_target(target_path, next_target, depth + 1)

            # 返回相对路径
            return rel_path

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
