#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版内容检查器 - 一键运行
"""

import os
import sys
from pathlib import Path
from content_checker import ContentChecker

def main():
    """一键运行内容检查"""
    print("=" * 50)
    print("书籍内容一键检查工具")
    print("=" * 50)

    # 检查API密钥
    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        print("错误: 没有找到API密钥!")
        print("请设置环境变量:")
        print("  export ANTHROPIC_API_KEY='你的密钥'  # 使用Claude模型")
        print("  或")
        print("  export OPENAI_API_KEY='你的密钥'    # 使用GPT模型")
        sys.exit(1)

    # 自动选择模型
    if os.getenv("ANTHROPIC_API_KEY"):
        model_type = "anthropic"
        print("使用模型: Claude (Anthropic)")
    else:
        model_type = "openai"
        print("使用模型: GPT (OpenAI)")

    print("=" * 50)

    try:
        # 创建检查器并运行
        checker = ContentChecker(model_type=model_type)

        # 显示待检查的文件
        original_path = Path("Originial")
        if original_path.exists():
            files = list(original_path.glob("*.md"))
            print(f"\n找到 {len(files)} 个文件需要检查:")
            for f in files:
                print(f"  - {f.name}")

            # 确认检查
            response = input(f"\n确认要检查这 {len(files)} 个文件吗? [Y/n]: ").strip().lower()
            if response == 'n':
                print("取消检查")
                return

            print("\n开始检查...")
            checker.process_all_files()

            print(f"\n检查完成！结果保存在 Examinied 文件夹中")

        else:
            print("错误: Originial 文件夹不存在!")

    except KeyboardInterrupt:
        print("\n取消检查")
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()