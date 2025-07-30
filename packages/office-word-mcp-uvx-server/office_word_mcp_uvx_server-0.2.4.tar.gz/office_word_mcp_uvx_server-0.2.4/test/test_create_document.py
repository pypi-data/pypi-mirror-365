"""测试create_document功能的单元测试"""

import os
import tempfile
import unittest
from pathlib import Path

# 添加src目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from word_mcp.create_document import create_document
from word_mcp.exceptions import FileError, DocumentError, ValidationError


class TestCreateDocument(unittest.TestCase):
    """测试create_document功能的单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_document.docx")

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_document_success(self):
        """测试成功创建文档"""
        result = create_document(
            filepath=self.test_file,
            title="测试文档",
            author="测试作者"
        )

        self.assertTrue(result["created"])
        self.assertEqual(result["title"], "测试文档")
        self.assertEqual(result["author"], "测试作者")
        self.assertEqual(result["file_path"], self.test_file)
        self.assertTrue(os.path.exists(self.test_file))

    def test_create_document_no_metadata(self):
        """测试创建文档但不设置元数据"""
        result = create_document(filepath=self.test_file)

        self.assertTrue(result["created"])
        self.assertEqual(result["title"], "")
        self.assertEqual(result["author"], "")
        self.assertTrue(os.path.exists(self.test_file))

    def test_create_document_auto_extension(self):
        """测试自动添加.docx扩展名"""
        file_without_ext = os.path.join(self.temp_dir, "test_no_ext")
        result = create_document(filepath=file_without_ext)

        self.assertTrue(result["created"])
        self.assertTrue(result["file_path"].endswith(".docx"))
        self.assertTrue(os.path.exists(result["file_path"]))

    def test_create_document_already_exists(self):
        """测试创建已存在的文档应该失败"""
        # 先创建文档
        create_document(filepath=self.test_file)

        # 尝试创建同名文档应该失败
        with self.assertRaises(FileError) as context:
            create_document(filepath=self.test_file)
        self.assertIn("文件已存在", str(context.exception))

    def test_create_document_empty_filepath(self):
        """测试空文件路径应该失败"""
        with self.assertRaises(ValidationError) as context:
            create_document(filepath="")
        self.assertIn("文件路径不能为空", str(context.exception))

    def test_create_document_create_directory(self):
        """测试创建文档时自动创建目录"""
        nested_dir = os.path.join(self.temp_dir, "subdir", "nested")
        nested_file = os.path.join(nested_dir, "test.docx")

        result = create_document(filepath=nested_file, title="嵌套目录测试")

        self.assertTrue(result["created"])
        self.assertTrue(os.path.exists(nested_file))
        self.assertTrue(os.path.exists(nested_dir))

    def test_create_document_invalid_directory(self):
        """测试在无法写入的目录创建文档"""
        # 这个测试在某些系统上可能需要特殊权限，先跳过
        pass


if __name__ == '__main__':
    unittest.main()