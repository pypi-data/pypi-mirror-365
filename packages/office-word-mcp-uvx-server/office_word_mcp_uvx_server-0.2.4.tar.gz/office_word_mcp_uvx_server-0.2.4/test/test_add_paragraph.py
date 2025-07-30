"""测试add_paragraph功能的单元测试"""

import os
import tempfile
import unittest
from pathlib import Path

# 添加src目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from word_mcp.create_document import create_document
from word_mcp.add_paragraph import add_paragraph
from word_mcp.get_document_text import get_document_text
from word_mcp.exceptions import FileError, DocumentError, ValidationError


class TestAddParagraph(unittest.TestCase):
    """测试add_paragraph功能的单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_document.docx")

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_paragraph_success(self):
        """测试成功添加段落"""
        # 创建测试文档
        create_document(filepath=self.test_file)

        # 添加段落
        result = add_paragraph(
            filepath=self.test_file,
            text="这是一个测试段落，包含重要信息。"
        )

        self.assertIn("成功向文档添加段落", result["message"])
        self.assertEqual(result["text"], "这是一个测试段落，包含重要信息。")
        self.assertEqual(result["style"], "Normal")
        self.assertEqual(result["text_length"], 16)
        self.assertEqual(result["word_count"], 1)  # 中文按字符计算

        # 验证段落确实被添加
        doc_text = get_document_text(self.test_file)
        self.assertIn("这是一个测试段落，包含重要信息。", doc_text["text"])

    def test_add_paragraph_with_style(self):
        """测试添加带样式的段落"""
        create_document(filepath=self.test_file)

        result = add_paragraph(
            filepath=self.test_file,
            text="带样式的段落",
            style="Normal"
        )

        self.assertEqual(result["style"], "Normal")

    def test_add_paragraph_invalid_style(self):
        """测试使用不存在的样式"""
        create_document(filepath=self.test_file)

        result = add_paragraph(
            filepath=self.test_file,
            text="测试段落",
            style="不存在的样式"
        )

        self.assertIn("样式不存在", result["style"])

    def test_add_paragraph_empty_text(self):
        """测试空文本应该失败"""
        create_document(filepath=self.test_file)

        with self.assertRaises(ValidationError) as context:
            add_paragraph(filepath=self.test_file, text="")
        self.assertIn("段落文本不能为空", str(context.exception))

    def test_add_paragraph_file_not_exists(self):
        """测试文件不存在应该失败"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.docx")

        with self.assertRaises(FileError) as context:
            add_paragraph(filepath=non_existent_file, text="测试")
        self.assertIn("文件不存在", str(context.exception))

    def test_add_paragraph_invalid_format(self):
        """测试非docx文件应该失败"""
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("test")

        with self.assertRaises(FileError) as context:
            add_paragraph(filepath=txt_file, text="测试")
        self.assertIn("文件格式不支持", str(context.exception))

    def test_add_paragraph_empty_filepath(self):
        """测试空文件路径应该失败"""
        with self.assertRaises(ValidationError) as context:
            add_paragraph(filepath="", text="测试")
        self.assertIn("文件路径不能为空", str(context.exception))

    def test_add_multiple_paragraphs(self):
        """测试添加多个段落"""
        create_document(filepath=self.test_file)

        # 添加第一个段落
        result1 = add_paragraph(filepath=self.test_file, text="第一个段落")
        self.assertEqual(result1["word_count"], 1)

        # 添加第二个段落
        result2 = add_paragraph(filepath=self.test_file, text="第二个段落，内容更长一些")
        self.assertEqual(result2["word_count"], 1)

        # 验证两个段落都被添加
        doc_text = get_document_text(self.test_file)
        self.assertIn("第一个段落", doc_text["text"])
        self.assertIn("第二个段落，内容更长一些", doc_text["text"])

    def test_add_paragraph_long_text(self):
        """测试添加长文本段落"""
        create_document(filepath=self.test_file)

        long_text = "这是一个很长的段落，" * 50  # 创建长文本
        result = add_paragraph(filepath=self.test_file, text=long_text)

        self.assertEqual(result["text_length"], len(long_text))
        self.assertGreater(result["word_count"], 0)
        self.assertIn("...", result["message"])  # 长文本应该被截断显示


if __name__ == '__main__':
    unittest.main()