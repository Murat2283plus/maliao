
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目代码文档生成器
用于生成包含项目结构和所有代码内容的Markdown文档
路径: /home/mulati/Murat_large/sda/老师的项目/配合前端代码/generate_project_docs.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 运行终端命令

shell_code = '''#!/bin/bash

# 目录路径
TARGET_DIR="./"

# 输出文件名
OUTPUT_FILE="directory_report.md"

# Python 脚本内容
python3 << 'EOF'
import os
import sys
from collections import defaultdict, Counter
from pathlib import Path
import re
from datetime import datetime

def get_file_extension(filename):
    """获取文件扩展名"""
    return Path(filename).suffix.lower()

def get_file_size_str(size_bytes):
    """将字节数转换为可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f}KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f}MB"
    else:
        return f"{size_bytes/(1024**3):.1f}GB"

def get_directory_signature(path, max_sample_size=10):
    """获取目录的特征签名，用于识别相似目录结构"""
    try:
        items = os.listdir(path)
        subdirs = []
        files_by_ext = defaultdict(int)
        
        for item in items[:max_sample_size]:  # 只采样前几个项目
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                subdirs.append("DIR")
            elif os.path.isfile(item_path):
                ext = get_file_extension(item)
                files_by_ext[ext] += 1
        
        # 生成签名：子目录数量 + 文件类型及大致数量
        signature = f"dirs:{len(subdirs)}|files:{dict(sorted(files_by_ext.items()))}"
        return signature
    except:
        return "ERROR"

def find_similar_directories(parent_path, max_show=3):
    """查找相似的目录并分组"""
    try:
        dirs = [d for d in os.listdir(parent_path) 
                if os.path.isdir(os.path.join(parent_path, d))]
    except:
        return {}
    
    if len(dirs) <= max_show:
        return {d: [d] for d in dirs}
    
    # 按目录签名分组
    signature_groups = defaultdict(list)
    for directory in dirs:
        dir_path = os.path.join(parent_path, directory)
        signature = get_directory_signature(dir_path)
        signature_groups[signature].append(directory)
    
    # 处理分组结果
    result = {}
    for signature, dir_group in signature_groups.items():
        if len(dir_group) <= max_show:
            # 如果组内目录数量不多，单独显示
            for d in dir_group:
                result[d] = [d]
        else:
            # 如果组内目录很多，选择前几个作为代表
            sorted_dirs = sorted(dir_group)
            representative = sorted_dirs[0]  # 选择第一个作为代表
            result[representative] = sorted_dirs  # 包含所有同类目录
    
    return result

def analyze_directory(path, max_files_per_type=3, max_dirs_per_type=3, max_depth=6, current_depth=0):
    """分析目录结构并生成简化的树形显示"""
    result = []
    
    if current_depth >= max_depth:
        return ["📁 ... (目录层级过深，已省略)"]
    
    try:
        items = os.listdir(path)
    except PermissionError:
        return ["❌ (权限不足，无法访问)"]
    except Exception as e:
        return [f"❌ (错误: {str(e)})"]
    
    # 查找相似目录并分组
    similar_dirs = find_similar_directories(path, max_dirs_per_type)
    
    # 处理目录
    for representative, all_dirs in similar_dirs.items():
        dir_path = os.path.join(path, representative)
        
        if len(all_dirs) == 1:
            # 单独的目录
            result.append(f"📁 **{representative}/**")
            sub_items = analyze_directory(dir_path, max_files_per_type, max_dirs_per_type, max_depth, current_depth + 1)
            for item in sub_items:
                result.append(f"    {item}")
        else:
            # 相似目录组
            total_count = len(all_dirs)
            shown_count = min(max_dirs_per_type, total_count)
            
            # 显示代表目录的详细结构
            result.append(f"📁 **{representative}/** (代表 {total_count} 个相似目录)")
            sub_items = analyze_directory(dir_path, max_files_per_type, max_dirs_per_type, max_depth, current_depth + 1)
            for item in sub_items:
                result.append(f"    {item}")
            
            # 显示其他几个同类目录名称
            if shown_count > 1:
                other_dirs = sorted(all_dirs)[1:shown_count]
                for other_dir in other_dirs:
                    result.append(f"📁 **{other_dir}/** (结构相似)")
            
            # 省略信息
            if total_count > shown_count:
                omitted = total_count - shown_count
                dir_range = f"从 {min(all_dirs)} 到 {max(all_dirs)}" if len(set(all_dirs)) > 2 else "等"
                result.append(f"📁 ... *还有 {omitted} 个结构相似的目录* ({dir_range})")
    
    # 处理文件
    files = []
    for item in items:
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            files.append(item)
    
    if files:
        # 按扩展名分组文件
        files_by_ext = defaultdict(list)
        for file in files:
            ext = get_file_extension(file)
            try:
                size = os.path.getsize(os.path.join(path, file))
                files_by_ext[ext].append((file, size))
            except:
                files_by_ext[ext].append((file, 0))
        
        # 显示文件信息
        for ext in sorted(files_by_ext.keys()):
            file_list = files_by_ext[ext]
            total_count = len(file_list)
            
            if ext == '':
                ext_display = "**无扩展名文件**"
            else:
                ext_display = f"**{ext} 文件**"
            
            if total_count <= max_files_per_type:
                # 显示所有文件
                result.append(f"📄 {ext_display} ({total_count} 个):")
                for filename, size in file_list:
                    size_str = get_file_size_str(size)
                    result.append(f"    - `{filename}` ({size_str})")
            else:
                # 只显示前几个文件，其余省略
                result.append(f"📄 {ext_display} ({total_count} 个):")
                for filename, size in file_list[:max_files_per_type]:
                    size_str = get_file_size_str(size)
                    result.append(f"    - `{filename}` ({size_str})")
                
                remaining = total_count - max_files_per_type
                total_size = sum(size for _, size in file_list)
                total_size_str = get_file_size_str(total_size)
                result.append(f"    - ... *还有 {remaining} 个同类型文件* (总计: {total_size_str})")
    
    return result

def generate_directory_report(target_path, output_file):
    """生成目录报告并写入文件"""
    if not os.path.exists(target_path):
        print(f"❌ **错误**: 路径不存在: `{target_path}`")
        return
    
    if not os.path.isdir(target_path):
        print(f"❌ **错误**: 不是目录: `{target_path}`")
        return
    
    # 准备输出内容
    output_lines = []
    
    output_lines.append("# 📁 目录结构分析报告\\n")
    output_lines.append(f"**路径**: `{target_path}`\\n")
    output_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
    
    # 获取目录总体信息
    total_size = 0
    total_files = 0
    total_dirs = 0
    
    for root, dirs, files in os.walk(target_path):
        total_dirs += len(dirs)
        total_files += len(files)
        for file in files:
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except:
                pass
    
    output_lines.append("**概览信息**:")
    output_lines.append(f"- 📁 总目录数: {total_dirs}")
    output_lines.append(f"- 📄 总文件数: {total_files}")
    output_lines.append(f"- 💾 总大小: {get_file_size_str(total_size)}\\n")
    
    output_lines.append("---\\n")
    output_lines.append("## 📋 详细结构\\n")
    
    # 生成详细结构
    tree_lines = analyze_directory(target_path)
    output_lines.extend(tree_lines)
    
    output_lines.append("\\n---")
    output_lines.append("\\n**📝 说明**:")
    output_lines.append("- 为了保持输出简洁，**每种文件类型最多显示 3 个示例**")
    output_lines.append("- **大量同类型文件会被省略显示**，但会显示总数和总大小")
    output_lines.append("- **相似结构的目录会被分组显示**，避免重复冗余信息")
    output_lines.append("- **目录层级限制为 6 层**，避免过深的嵌套")
    output_lines.append("- **文件大小**会自动转换为合适的单位显示")
    
    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in output_lines:
                f.write(line + '\\n')
        
        print("✅ **报告生成完成**!")
        print(f"📄 **文件位置**: `{os.path.abspath(output_file)}`")
        print(f"📊 **报告行数**: {len(output_lines)} 行")
        
    except Exception as e:
        print(f"❌ **写入文件失败**: {str(e)}")

# 主程序
if __name__ == "__main__":
    import os
    target_directory = os.getenv('TARGET_DIR', './')
    output_filename = os.getenv('OUTPUT_FILE', 'directory_report.md')
    generate_directory_report(target_directory, output_filename)

EOF

'''

os.system(shell_code)


class ProjectDocumentGenerator:
    def __init__(self, project_root=None):
        """初始化文档生成器"""
        self.project_root = './'
        self.output_file = os.path.join(self.project_root, f"./文档/project_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        # 定义要忽略的目录和文件
        self.ignore_dirs = {
            '__pycache__', '.git', '.idea', '.vscode', 'venv', 'env', 
            'uploads', 'outputs', '.pytest_cache', 'node_modules','claud输出','project_documentation'
        }
        self.ignore_files = {
            '.pyc', '.pyo', '.DS_Store', '.gitignore', '.env', 
            '__pycache__', '.log', '.db', '.sqlite', '.npy', '.pkl',
            'project_documentation_','generate_project_docs'#,'directory_report'
        }
        
        # 定义要包含的文件扩展名
        self.include_extensions = {
            '.py', '.json'#'.js', '.txt', '.md',
            #'.yaml', '.yml', '.sh', '.bat', '.sql','.cfg','project_documentation' # '.html',  '.css',   '.json',  '.ini', 
        }

        self.include_files = {
            'directory_report.md'
        }
        
        # 项目结构
        self.tree_structure = []
        self.file_contents = []
        
    def should_include_file(self, file_path):
        """判断文件是否应该包含在文档中"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        for include_file in self.include_files :
            if include_file in file_name:
                return True

        # 检查是否是要忽略的文件
        for ignore_pattern in self.ignore_files:
            if ignore_pattern in file_name:
                return False
        
        # 检查是否是要包含的扩展名
        if self.include_extensions and file_ext not in self.include_extensions:
            return False
        
        # 忽略过大的文件（大于1MB）
        try:
            if os.path.getsize(file_path) > 1024 * 1024:
                return False
        except:
            return False
        
        return True
    
    def get_language_for_file(self, file_path):
        """根据文件扩展名返回代码块语言标识"""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sh': 'bash',
            '.bat': 'batch',
            '.sql': 'sql',
            '.md': 'markdown',
            '.txt': 'text',
            '.ini': 'ini',
            '.cfg': 'ini'
        }
        return language_map.get(ext, 'text')
    
    def generate_tree_structure(self, start_path, prefix="", is_last=True):
        """生成目录树结构"""
        def get_sorted_items(path):
            """获取排序后的目录和文件列表"""
            items = []
            try:
                for item in os.listdir(path):
                    if item.startswith('.') and item != '.env':
                        continue
                    item_path = os.path.join(path, item)
                    items.append((item, item_path, os.path.isdir(item_path)))
                # 先按是否为目录排序（目录在前），然后按名称排序
                items.sort(key=lambda x: (not x[2], x[0].lower()))
            except PermissionError:
                pass
            return items
        
        # 添加当前目录
        current_dir = os.path.basename(start_path)
        if current_dir:
            connector = "└── " if is_last else "├── "
            self.tree_structure.append(f"{prefix}{connector}{current_dir}/")
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension
        else:
            new_prefix = prefix
        
        # 获取并处理子项
        items = get_sorted_items(start_path)
        for index, (name, path, is_dir) in enumerate(items):
            is_last_item = index == len(items) - 1
            
            if is_dir:
                if name not in self.ignore_dirs:
                    self.generate_tree_structure(path, new_prefix, is_last_item)
            else:
                if self.should_include_file(path):
                    connector = "└── " if is_last_item else "├── "
                    self.tree_structure.append(f"{new_prefix}{connector}{name}")
    
    def collect_file_contents(self, start_path):
        """递归收集所有文件内容"""
        for root, dirs, files in os.walk(start_path):
            # 过滤掉要忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            # 获取相对路径
            rel_path = os.path.relpath(root, self.project_root)
            
            for file in sorted(files):
                file_path = os.path.join(root, file)
                if self.should_include_file(file_path):
                    self.read_and_store_file(file_path, rel_path)
    
    def read_and_store_file(self, file_path, rel_path):
        """读取并存储文件内容"""
        try:
            # 尝试使用UTF-8编码读取
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取完整相对路径
            if rel_path == '.':
                full_rel_path = os.path.basename(file_path)
            else:
                full_rel_path = os.path.join(rel_path, os.path.basename(file_path))
            
            # 获取代码语言
            language = self.get_language_for_file(file_path)
            
            self.file_contents.append({
                'path': full_rel_path,
                'absolute_path': file_path,
                'language': language,
                'content': content
            })
            
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {str(e)}")
    
    def generate_markdown(self):
        """生成Markdown文档"""
        markdown_content = []
        
        # 标题和基本信息
        markdown_content.append("# 项目代码文档\n")
        markdown_content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        markdown_content.append(f"**项目路径**: `{self.project_root}`\n")
        markdown_content.append("\n---\n")
        
        # 目录
        markdown_content.append("## 目录\n")
        markdown_content.append("1. [项目结构](#项目结构)")
        markdown_content.append("2. [代码文件内容](#代码文件内容)")
        for i, file_info in enumerate(self.file_contents, 1):
            file_name = os.path.basename(file_info['path'])
            anchor = file_info['path'].replace('/', '-').replace('\\', '-').replace('.', '-').replace(' ', '-').lower()
            markdown_content.append(f"   - [{file_info['path']}](#{anchor})")
        markdown_content.append("\n---\n")
        
        # 项目结构
        markdown_content.append("## 项目结构\n")
        markdown_content.append("```")
        markdown_content.append(self.project_root + "/")
        markdown_content.extend(self.tree_structure)
        markdown_content.append("```\n")
        markdown_content.append("\n---\n")
        
        # 代码文件内容
        markdown_content.append("## 代码文件内容\n")
        
        for file_info in self.file_contents:
            # 创建锚点
            anchor = file_info['path'].replace('/', '-').replace('\\', '-').replace('.', '-').replace(' ', '-').lower()
            
            # 文件标题
            markdown_content.append(f"### {file_info['path']} {{#{anchor}}}\n")
            markdown_content.append(f"**完整路径**: `{file_info['absolute_path']}`\n")
            markdown_content.append(f"**文件内容**:\n")
            markdown_content.append(f"```{file_info['language']}")
            markdown_content.append(file_info['content'])
            if not file_info['content'].endswith('\n'):
                markdown_content.append('')
            markdown_content.append("```\n")
            markdown_content.append("\n---\n")
        
        # 添加使用说明
        markdown_content.append("## 使用说明\n")
        markdown_content.append("此文档由自动化脚本生成，包含了项目的完整结构和所有代码文件内容。\n")
        markdown_content.append("您可以将此文档提供给AI助手或其他开发者，以便他们了解项目的完整情况。\n")
        markdown_content.append("\n### 注意事项：\n")
        markdown_content.append("- 二进制文件、缓存文件和大文件已被自动过滤")
        markdown_content.append("- 敏感信息（如密码、密钥）请在分享前手动检查并删除")
        markdown_content.append("- 生成的文档可能较大，建议使用支持大文件的编辑器打开\n")
        
        return '\n'.join(markdown_content)
    
    def generate(self):
        """执行文档生成"""
        print(f"开始生成项目文档...")
        print(f"项目根目录: {self.project_root}")
        
        # 生成目录树
        print("正在生成项目结构...")
        self.generate_tree_structure(self.project_root)
        
        # 收集文件内容
        print("正在收集文件内容...")
        self.collect_file_contents(self.project_root)
        
        # 生成Markdown
        print("正在生成Markdown文档...")
        markdown_content = self.generate_markdown()
        
        # 写入文件
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # 计算文档统计信息
            doc_size = os.path.getsize(self.output_file) / 1024  # KB
            
            print(f"\n✅ 文档生成成功!")
            print(f"输出文件: {self.output_file}")
            print(f"文档大小: {doc_size:.2f} KB")
            print(f"包含文件数: {len(self.file_contents)}")
            print(f"\n您现在可以将生成的Markdown文档发送给AI助手或其他开发者。")
            
            return self.output_file
            
        except Exception as e:
            print(f"\n❌ 文档生成失败: {str(e)}")
            return None

def main():
    """主函数"""
    # 可以通过命令行参数指定项目路径
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = None
    
    # 创建文档生成器
    generator = ProjectDocumentGenerator(project_path)
    
    # 生成文档
    output_file = generator.generate()

if __name__ == "__main__":
    main()   # python generate_project_docs.py

