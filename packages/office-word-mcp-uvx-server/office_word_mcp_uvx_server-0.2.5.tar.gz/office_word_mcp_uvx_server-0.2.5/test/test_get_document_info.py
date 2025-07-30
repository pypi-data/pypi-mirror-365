"""测试get_document_info功能的单元测试"""

import os
import tempfile
import unittest
from pathlib import Path

# 添加src目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from word_mcp.create_document import create_document
from word_mcp.get_document_info import get_document_info
from word_mcp.exceptions import FileError, DocumentError, ValidationError


class TestGetDocumentInfo(unittest.TestCase):
    """测试get_document_info功能的单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_document.docx")

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_document_info_success(self):
        """测试成功获取文档信息"""
        # 先创建一个有元数据的文档
        create_document(
            filepath=self.test_file,
            title="信息测试文档",
            author="信息测试作者"
        )

        # 获取文档信息
        result = get_document_info(filepath=self.test_file)

        self.assertEqual(result["title"], "信息测试文档")
        self.assertEqual(result["author"], "信息测试作者")
        self.assertEqual(result["file_path"], self.test_file)
        self.assertIn("file_size", result)
        self.assertIn("word_count", result)
        self.assertIn("paragraph_count", result)
        self.assertIn("table_count", result)
        self.assertIn("page_count", result)
        self.assertGreater(result["file_size"], 0)

    def test_get_document_info_empty_document(self):
        """测试获取空文档的信息"""
        # 创建空文档
        create_document(filepath=self.test_file)

        # 获取文档信息
        result = get_document_info(filepath=self.test_file)

        self.assertEqual(result["title"], "")
        # python-docx默认会设置author为"python-docx"，这是正常的
        self.assertIn(result["author"], ["", "python-docx"])
        self.assertEqual(result["word_count"], 0)
        self.assertEqual(result["paragraph_count"], 0)
        self.assertEqual(result["table_count"], 0)
        self.assertGreater(result["file_size"], 0)  # 即使是空文档也有基本结构

    def test_get_document_info_file_not_exists(self):
        """测试获取不存在文件的信息应该失败"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.docx")

        with self.assertRaises(FileError) as context:
            get_document_info(non_existent_file)
        self.assertIn("文件不存在", str(context.exception))

    def test_get_document_info_invalid_format(self):
        """测试获取非docx文件的信息应该失败"""
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("这不是docx文件")

        with self.assertRaises(FileError) as context:
            get_document_info(txt_file)
        self.assertIn("文件格式不支持", str(context.exception))

    def test_get_document_info_empty_filepath(self):
        """测试空文件路径应该失败"""
        with self.assertRaises(ValidationError) as context:
            get_document_info(filepath="")
        self.assertIn("文件路径不能为空", str(context.exception))

    def test_get_document_info_return_fields(self):
        """测试返回结果包含所有必需的字段"""
        # 创建文档
        create_document(
            filepath=self.test_file,
            title="完整测试文档",
            author="测试用户"
        )

        # 获取文档信息
        result = get_document_info(filepath=self.test_file)

        # 检查所有必需字段是否存在
        required_fields = [
            "message", "file_path", "title", "author", "subject",
            "keywords", "created", "modified", "last_modified_by",
            "revision", "page_count", "word_count", "paragraph_count",
            "table_count", "file_size"
        ]

        for field in required_fields:
            self.assertIn(field, result, f"缺少字段: {field}")


if __name__ == '__main__':
    unittest.main()