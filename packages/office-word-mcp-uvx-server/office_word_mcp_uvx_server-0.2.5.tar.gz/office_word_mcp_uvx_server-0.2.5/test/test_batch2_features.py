"""测试第二批5个功能的综合测试"""

import os
import tempfile
import unittest
from pathlib import Path

# 添加src目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from word_mcp.create_document import create_document
from word_mcp.add_paragraph import add_paragraph
from word_mcp.add_table import add_table
from word_mcp.add_page_break import add_page_break
from word_mcp.delete_paragraph import delete_paragraph
from word_mcp.create_custom_style import create_custom_style
from word_mcp.format_text import format_text
from word_mcp.get_document_text import get_document_text
from word_mcp.exceptions import FileError, DocumentError, ValidationError


class TestBatch2Features(unittest.TestCase):
    """测试第二批5个功能的综合测试类"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_document.docx")

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_table_basic(self):
        """测试基本的添加表格功能"""
        create_document(filepath=self.test_file)

        result = add_table(
            filepath=self.test_file,
            rows=2,
            cols=3
        )

        self.assertIn("成功向文档添加2x3表格", result["message"])
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["cols"], 3)
        self.assertFalse(result["data_provided"])

    def test_add_table_with_data(self):
        """测试添加带数据的表格"""
        create_document(filepath=self.test_file)

        data = [["标题1", "标题2"], ["数据1", "数据2"]]
        result = add_table(
            filepath=self.test_file,
            rows=2,
            cols=2,
            data=data
        )

        self.assertTrue(result["data_provided"])
        self.assertEqual(result["cells_filled"], 4)

    def test_add_page_break_basic(self):
        """测试基本的添加分页符功能"""
        create_document(filepath=self.test_file)

        result = add_page_break(filepath=self.test_file)

        self.assertIn("成功向文档添加分页符", result["message"])
        self.assertTrue(result["page_break_added"])

    def test_delete_paragraph_basic(self):
        """测试基本的删除段落功能"""
        create_document(filepath=self.test_file)

        # 先添加两个段落
        add_paragraph(filepath=self.test_file, text="第一个段落")
        add_paragraph(filepath=self.test_file, text="第二个段落")

        # 删除第一个段落（索引0）
        result = delete_paragraph(
            filepath=self.test_file,
            paragraph_index=0
        )

        self.assertIn("成功删除段落0", result["message"])
        self.assertEqual(result["paragraph_index"], 0)
        self.assertIn("第一个段落", result["paragraph_text"])

    def test_create_custom_style_basic(self):
        """测试基本的创建自定义样式功能"""
        create_document(filepath=self.test_file)

        result = create_custom_style(
            filepath=self.test_file,
            style_name="测试样式",
            bold=True,
            font_size=14
        )

        self.assertIn("成功创建自定义样式", result["message"])
        self.assertEqual(result["style_name"], "测试样式")
        self.assertTrue(result["properties"]["bold"])
        self.assertEqual(result["properties"]["font_size"], 14)

    def test_format_text_basic(self):
        """测试基本的格式化文本功能"""
        create_document(filepath=self.test_file)

        # 添加一个段落
        add_paragraph(filepath=self.test_file, text="这是一个测试段落")

        # 格式化前5个字符
        result = format_text(
            filepath=self.test_file,
            paragraph_index=0,
            start_pos=0,
            end_pos=5,
            bold=True,
            color="red"
        )

        self.assertIn("成功格式化文本", result["message"])
        self.assertEqual(result["target_text"], "这是一个测")
        self.assertTrue(result["format_applied"]["bold"])
        self.assertEqual(result["format_applied"]["color"], "red")

    def test_error_handling(self):
        """测试错误处理"""
        # 文件不存在的情况
        non_existent = os.path.join(self.temp_dir, "non_existent.docx")

        with self.assertRaises(FileError):
            add_table(filepath=non_existent, rows=2, cols=2)

        with self.assertRaises(FileError):
            add_page_break(filepath=non_existent)

        with self.assertRaises(FileError):
            delete_paragraph(filepath=non_existent, paragraph_index=0)

        # 参数验证错误
        create_document(filepath=self.test_file)

        with self.assertRaises(ValidationError):
            add_table(filepath=self.test_file, rows=0, cols=2)

        with self.assertRaises(ValidationError):
            delete_paragraph(filepath=self.test_file, paragraph_index=-1)

        with self.assertRaises(ValidationError):
            create_custom_style(filepath=self.test_file, style_name="")

    def test_comprehensive_workflow(self):
        """测试综合工作流程"""
        # 1. 创建文档
        create_document(filepath=self.test_file, title="综合测试文档")

        # 2. 创建自定义样式
        create_custom_style(
            filepath=self.test_file,
            style_name="重要提示",
            bold=True,
            color="red",
            font_size=16
        )

        # 3. 添加段落
        add_paragraph(filepath=self.test_file, text="这是第一个段落，包含重要信息。")

        # 4. 格式化部分文本
        format_text(
            filepath=self.test_file,
            paragraph_index=0,
            start_pos=5,
            end_pos=8,
            bold=True,
            italic=True
        )

        # 5. 添加表格
        table_data = [["项目", "数值"], ["A", "100"], ["B", "200"]]
        add_table(
            filepath=self.test_file,
            rows=3,
            cols=2,
            data=table_data
        )

        # 6. 添加分页符
        add_page_break(filepath=self.test_file)

        # 7. 添加另一个段落
        add_paragraph(filepath=self.test_file, text="这是第二页的内容。")

        # 验证文档内容
        doc_text = get_document_text(self.test_file)
        self.assertIn("第一个段落", doc_text["text"])
        self.assertIn("第二页", doc_text["text"])

    def test_table_size_limits(self):
        """测试表格大小限制"""
        create_document(filepath=self.test_file)

        # 测试过大的表格
        with self.assertRaises(ValidationError):
            add_table(filepath=self.test_file, rows=101, cols=2)

        with self.assertRaises(ValidationError):
            add_table(filepath=self.test_file, rows=2, cols=51)

    def test_style_duplication(self):
        """测试样式重复创建"""
        create_document(filepath=self.test_file)

        # 创建第一个样式
        create_custom_style(filepath=self.test_file, style_name="重复样式", bold=True)

        # 尝试创建同名样式应该失败
        with self.assertRaises(ValidationError):
            create_custom_style(filepath=self.test_file, style_name="重复样式", italic=True)

    def test_format_text_edge_cases(self):
        """测试格式化文本的边界情况"""
        create_document(filepath=self.test_file)
        add_paragraph(filepath=self.test_file, text="短文本")

        # 测试无效的位置
        with self.assertRaises(ValidationError):
            format_text(
                filepath=self.test_file,
                paragraph_index=0,
                start_pos=5,
                end_pos=10  # 超出文本长度
            )

        # 测试开始位置大于等于结束位置
        with self.assertRaises(ValidationError):
            format_text(
                filepath=self.test_file,
                paragraph_index=0,
                start_pos=2,
                end_pos=2
            )


if __name__ == '__main__':
    unittest.main()