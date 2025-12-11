#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书籍内容核查工具
用于检查书籍章节中的表述、数据、公式和定理是否符合事实
"""

import os
import re
import time
from pathlib import Path
from typing import Optional
import traceback

# 尝试导入所需的库
import openai
# import anthropic


class ContentChecker:
    """书籍内容核查器"""

    def __init__(self, model_type: str = "deepseek", api_key: Optional[str] = None):
        """
        初始化内容核查器

        Args:
            model_type: 使用的模型类型 ("anthropic" 或 "openai")
            api_key: API密钥（如果不提供，会从环境变量读取）
        """
        self.model_type = model_type
        self.api_key = api_key

        # if model_type == "anthropic":
        #     if not ANTHROPIC_AVAILABLE:
        #         raise ImportError("请安装 anthropic 库: pip install anthropic")
        #     self.client = anthropic.Anthropic(
        #         api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        #     )
        #     self.model_name = "claude-3-5-sonnet-20241022"
        if model_type == "deepseek":
            api_key = api_key or os.getenv("ARK_API_KEY")
            self.client = openai.OpenAI(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=api_key)
            self.model_name = "deepseek-v3-2-251201"
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    def create_examined_folder(self):
        """创建Examinied文件夹（如果不存在）"""
        examined_path = Path("Examinied")
        examined_path.mkdir(exist_ok=True)
        return examined_path

    def read_file_content(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
            return ""

    def create_check_prompt(self, content: str, file_name: str) -> str:
        """创建核查提示，专注于定理、公式和数据真实性核查"""
        topic = file_name.replace('.md', '')

        prompt = f"""你是一位专业的物理学教授，负责核查一本提供给本科生和研究生阅读的物理学专业书籍的内容。

请仔细检查以下章节内容，重点关注定理的正确性、公式的规范性以及数据的真实性。

文件：{file_name}
主题：{topic}

**核查重点一：定理的正确性**
1. 检查引用的物理学定理是否与标准表述一致
2. 确认定理的适用条件是否准确描述
3. 明确标注不常见的定理，并提供权威出处
4. 检查定理陈述是否符合物理学常识

**核查重点二：公式的正确性和规范性**
1. 检查物理常量和公式的正确性（如玻尔兹曼常数、普朗克常数等）
2. 确认数学符号的使用是否与现实版本一致
3. 检查量纲一致性（主要但非强制性质疑）
4. 注意指数、乘号、分号等数学符号的规范性

**核查重点三：具体数据和前沿结果的真实性**
1. 检查具体的物理数据是否有可靠来源
    - 实验测量值
    - 理论计算结果
    - 数值模拟结果
2. 确认前沿研究成果的可真实性
    - 检查是否存在已发表研究可查
    - 标记可能存疑的数据
    - 核实重大物理发现在时间和人物上的准确性
3. 验证物理参数的合理性
    - 数量级是否在前范围
    - 单位是否正确
4. 检查历史事实的准确性
    - 物理学家的发现时间和贡献
    - 重大物理事件的时代背景    

章节内容：
{content[:12000]}{'...' if len(content) > 12000 else ''}

**最终输出要求：**

请提供两个独立的部分：

**第一部分：核查报告**

按照以下格式输出：

## 核查结果

### 总体评价
[简要说明内容质量，重点关注定理、公式、数据三个方面的准确性]

### 发现的具体问题

#### 定理类问题
[详细列出发现的定理相关问题]

#### 公式类问题
[详细列出的公式正确性或规范相关问题]

#### 数据类问题
[详细列出具体数据或前沿结果的真实性问题]

### 修正建议
[针对各类问题提供具体的修正建议和要求]

### 需要注意的存疑点
[列出需要进一步查证或可能有争议的内容]

### 验证建议
[提供验证这些问题准确性的具体方向和方法]

---

**第二部分：修改后的版本**

在第一部分结束后，开始一个新的 Section，标题为：

## 修改后的版本

[提供根据上述发现并完全修正后的版本内容，保持原有结构但修正所有问题]

**注意：**
- 不要只修改有问题的部分，请提供完整的修改后版本
- 保持原有的章节结构和格式一致性
- 如果有公式错误，使用正确的LaTeX格式
- 如果有事实错误，请更正为经过确认的内容
"""

        return prompt

    def call_api(self, prompt: str) -> str:
        """调用API获取回复"""
        try:
            if self.model_type == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    max_tokens=8000,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            else:
                # 未来支持其他模型
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    max_tokens=8000,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
        except Exception as e:
            error_msg = f"API调用失败: {e}"
            print(f"错误: {error_msg}")
            traceback.print_exc()
            return f"错误: {error_msg}"

    def parse_and_save_results(self, original_file: Path, api_response: str, original_content: str) -> tuple:
        """解析API响应并分别保存核查结果和修改后的版本"""
        examined_folder = self.create_examined_folder()
        base_name = original_file.stem

        # 默认保存核查结果，可选保存修改版本
        check_result = api_response
        saved_modified = None

        # 如果找到了分隔标记，分离两部分内容
        if "---" in api_response and "## 修改后的版本" in api_response:
            # 使用分隔线分割内容
            parts = api_response.split("---", 1)
            if len(parts) == 2:
                # 第一部分是核查结果
                check_result = parts[0].strip()

                # 第二部分包含修改后的版本
                if "## 修改后的版本" in parts[1]:
                    modified_start = parts[1].find("## 修改后的版本")
                    modified_content = parts[1][modified_start:].strip()

                    # 保存修改后的版本
                    modified_file_name = f"{base_name}_modified.md"
                    modified_file_path = examined_folder / modified_file_name

                    try:
                        with open(modified_file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        print(f"✓ 修改后的版本已保存到: {modified_file_path}")
                        saved_modified = modified_file_path
                    except Exception as e:
                        print(f"  ✗ 保存修改版本失败: {e}")

        # 保存核查结果报告
        check_result_file_name = f"{base_name}_checked.md"
        check_result_file_path = examined_folder / check_result_file_name

        try:
            with open(check_result_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# 内容核查报告\n\n")
                f.write(f"**原文件名**: {original_file.name}\n\n")
                f.write(f"**核查日期**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**内容长度**: {len(original_content):,} 字符\n\n")
                f.write("---\n\n")
                f.write(check_result)

            print(f"✓ 核查报告已保存到: {check_result_file_path}")
            return check_result_file_path, saved_modified

        except Exception as e:
            print(f"  ✗ 保存核查报告失败: {e}")
            return None, saved_modified

    def process_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        print(f"\n正在处理文件: {file_path.name}")

        # 读取内容
        content = self.read_file_content(file_path)
        if not content:
            print(f"✗ 无法读取文件内容: {file_path}")
            return False

        # 创建检查提示
        print("  创建检查提示...")
        prompt = self.create_check_prompt(content, file_path.name)

        # 调用API
        print("  调用大模型API进行内容核查...")
        print("  这可能需要一些时间，请稍候...")
        check_result = self.call_api(prompt)

        if check_result.startswith("错误:"):
            print(f"✗ API调用失败: {check_result}")
            return False

        # 保存结果
        print("  保存核查结果和修改版本...")
        saved_check_path, saved_modified_path = self.parse_and_save_results(file_path, check_result, content)

        if saved_check_path:
            print("✓ 文件处理完成!")
            if saved_modified_path:
                print(f"✓ 生成的修改版本已保存到: {saved_modified_path}")
            return True
        else:
            print("✗ 保存结果失败!")
            return False

    def process_all_files(self, original_folder: str = "Originial"):
        """处理Original文件夹中的所有文件"""
        original_path = Path(original_folder)

        if not original_path.exists():
            print(f"错误: {original_folder} 文件夹不存在")
            return

        # 获取所有markdown文件
        markdown_files = list(original_path.glob("*.md"))

        if not markdown_files:
            print(f"在 {original_folder} 文件夹中没有找到markdown文件")
            return

        print(f"找到 {len(markdown_files)} 个markdown文件:")
        for f in markdown_files:
            print(f"  - {f.name} ({f.stat().st_size:,} 字节)")

        print("\n开始处理文件...")
        successful = 0
        failed = 0

        for file_path in markdown_files:
            try:
                if self.process_file(file_path):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"处理 {file_path.name} 时发生错误: {e}")
                failed += 1
                traceback.print_exc()

        # 处理完成后显示统计信息
        print(f"\n{'='*50}")
        print(f"处理完成!")
        print(f"总文件数: {len(markdown_files)}")
        print(f"成功: {successful}")
        print(f"失败: {failed}")
        print(f"{'='*50}")

        # 检查结果文件夹大小和文件类型统计
        examined_path = self.create_examined_folder()
        checked_files = list(examined_path.glob("*checked.md"))
        modified_files = list(examined_path.glob("*modified.md"))
        total_size = sum(f.stat().st_size for f in checked_files) + sum(f.stat().st_size for f in modified_files)

        print(f"\n处理完成统计:")
        print(f"  - 生成核查报告: {len(checked_files)} 个文件")
        print(f"  - 生成修改版本: {len(modified_files)} 个文件")
        print(f"  - 总计大小: {total_size:,} 字节 ({total_size/1024:.1f} KB)")


def main():
    """主函数"""
    # import argparse

    # parser = argparse.ArgumentParser(description='书籍内容核查工具')
    # parser.add_argument('--model', choices=['anthropic', 'openai'], default='anthropic',
    #                    help='使用的模型类型 (默认: anthropic)')
    # parser.add_argument('--api-key', type=str, help='API密钥（可选，不填则从环境变量读取）')
    # parser.add_argument('--original-folder', type=str, default='Originial',
    #                    help='原始文件夹路径 (默认: Originial)')
    # parser.add_argument('--examined-folder', type=str, default='Examinied',
    #                    help='检查结果文件夹路径 (默认: Examinied)')
    # parser.add_argument('--timeout', type=int, default=120, help='API超时时间（秒）')

    # args = parser.parse_args()

    # 显示启动信息
    # print("=" * 60)
    print("书籍内容核查工具 v1.0")
    # print("=" * 60)
    # print(f"模型类型: {args.model}")
    # print(f"原始文件夹: {args.original_folder}")
    # print(f"检查结果文件夹: {args.examined_folder}")
    # print("=" * 60)

    try:
        # 创建检查器实例
        # checker = ContentChecker(
        #     model_type=args.model,
        #     api_key=args.api_key
        # )

        checker = ContentChecker()

        # 处理所有文件
        checker.process_all_files("Originial")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行失败: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()