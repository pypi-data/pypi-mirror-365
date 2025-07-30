"""测试第三批6个功能的综合测试"""

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
from word_mcp.format_table import format_table
from word_mcp.protect_document import protect_document
from word_mcp.unprotect_document import unprotect_document
from word_mcp.add_footnote_to_document import add_footnote_to_document
from word_mcp.add_endnote_to_document import add_endnote_to_document
from word_mcp.customize_footnote_style import customize_footnote_style
from word_mcp.get_document_text import get_document_text
from word_mcp.exceptions import FileError, DocumentError, ValidationError


class TestBatch3Features(unittest.TestCase):
    """测试第三批6个功能的综合测试类"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_document.docx")

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_format_table_basic(self):
        """测试基本的格式化表格功能"""
        create_document(filepath=self.test_file)

        # 先添加表格
        add_table(filepath=self.test_file, rows=2, cols=2,
                 data=[["标题1", "标题2"], ["数据1", "数据2"]])

        # 格式化表格
        result = format_table(
            filepath=self.test_file,
            table_index=0,
            has_header_row=True,
            border_style="single"
        )

        self.assertIn("成功格式化表格0", result["message"])
        self.assertEqual(result["table_index"], 0)
        self.assertIn("标题行加粗", result["formatting_applied"])
        self.assertEqual(result["table_size"], "2x2")

    def test_format_table_with_shading(self):
        """测试带底纹的表格格式化"""
        create_document(filepath=self.test_file)
        add_table(filepath=self.test_file, rows=2, cols=2)

        shading = [["lightgray", "white"], ["white", "lightgray"]]
        result = format_table(
            filepath=self.test_file,
            table_index=0,
            shading=shading
        )

        self.assertIn("底纹应用到", result["formatting_applied"][0])

    def test_protect_unprotect_document(self):
        """测试文档保护和解除保护"""
        create_document(filepath=self.test_file)
        add_paragraph(filepath=self.test_file, text="测试内容")

        # 保护文档
        protect_result = protect_document(
            filepath=self.test_file,
            password="test123"
        )

        self.assertIn("成功为文档添加密码保护", protect_result["message"])
        self.assertEqual(protect_result["protection_type"], "password")

        # 检查保护元数据文件是否存在
        base_path, _ = os.path.splitext(self.test_file)
        metadata_file = f"{base_path}.protection"
        self.assertTrue(os.path.exists(metadata_file))

        # 解除保护
        unprotect_result = unprotect_document(
            filepath=self.test_file,
            password="test123"
        )

        self.assertIn("成功解除文档密码保护", unprotect_result["message"])
        self.assertTrue(unprotect_result["was_protected"])
        self.assertTrue(unprotect_result["metadata_removed"])

        # 检查元数据文件是否被删除
        self.assertFalse(os.path.exists(metadata_file))

    def test_protect_wrong_password(self):
        """测试错误密码解除保护"""
        create_document(filepath=self.test_file)

        # 保护文档
        protect_document(filepath=self.test_file, password="correct123")

        # 使用错误密码尝试解除保护
        with self.assertRaises(ValidationError) as context:
            unprotect_document(filepath=self.test_file, password="wrong123")
        self.assertIn("密码错误", str(context.exception))

    def test_add_footnote_basic(self):
        """测试基本的添加脚注功能"""
        create_document(filepath=self.test_file)
        add_paragraph(filepath=self.test_file, text="这是测试段落")

        result = add_footnote_to_document(
            filepath=self.test_file,
            paragraph_index=0,
            footnote_text="这是脚注内容"
        )

        self.assertIn("成功向段落0添加脚注", result["message"])
        self.assertEqual(result["paragraph_index"], 0)
        self.assertEqual(result["footnote_text"], "这是脚注内容")
        self.assertEqual(result["footnote_number"], 1)

    def test_add_endnote_basic(self):
        """测试基本的添加尾注功能"""
        create_document(filepath=self.test_file)
        add_paragraph(filepath=self.test_file, text="这是测试段落")

        result = add_endnote_to_document(
            filepath=self.test_file,
            paragraph_index=0,
            endnote_text="这是尾注内容"
        )

        self.assertIn("成功向段落0添加尾注", result["message"])
        self.assertEqual(result["endnote_text"], "这是尾注内容")
        self.assertEqual(result["endnote_symbol"], "†")  # 第一个尾注符号

    def test_customize_footnote_style_basic(self):
        """测试基本的自定义脚注样式功能"""
        create_document(filepath=self.test_file)
        add_paragraph(filepath=self.test_file, text="测试段落")

        # 先添加脚注
        add_footnote_to_document(filepath=self.test_file, paragraph_index=0, footnote_text="脚注1")

        # 自定义脚注样式
        result = customize_footnote_style(
            filepath=self.test_file,
            numbering_format="i, ii, iii",
            font_name="Arial",
            font_size=9
        )

        self.assertIn("成功自定义脚注样式", result["message"])
        self.assertEqual(result["numbering_format"], "i, ii, iii")
        self.assertTrue(result["style_applied"])

    def test_error_handling(self):
        """测试错误处理"""
        # 文件不存在的情况
        non_existent = os.path.join(self.temp_dir, "non_existent.docx")

        with self.assertRaises(FileError):
            format_table(filepath=non_existent, table_index=0)

        with self.assertRaises(FileError):
            protect_document(filepath=non_existent, password="test123")

        with self.assertRaises(FileError):
            add_footnote_to_document(filepath=non_existent, paragraph_index=0, footnote_text="test")

        # 参数验证错误
        create_document(filepath=self.test_file)

        with self.assertRaises(ValidationError):
            format_table(filepath=self.test_file, table_index=-1)

        with self.assertRaises(ValidationError):
            protect_document(filepath=self.test_file, password="")

        with self.assertRaises(ValidationError):
            add_footnote_to_document(filepath=self.test_file, paragraph_index=-1, footnote_text="test")

    def test_comprehensive_workflow(self):
        """测试综合工作流程"""
        # 1. 创建文档
        create_document(filepath=self.test_file, title="综合测试文档")

        # 2. 添加内容
        add_paragraph(filepath=self.test_file, text="这是第一个段落，将添加脚注。")
        add_paragraph(filepath=self.test_file, text="这是第二个段落，将添加尾注。")

        # 3. 添加表格
        table_data = [["功能", "状态"], ["脚注", "完成"], ["尾注", "完成"]]
        add_table(filepath=self.test_file, rows=3, cols=2, data=table_data)

        # 4. 格式化表格
        format_table(
            filepath=self.test_file,
            table_index=0,
            has_header_row=True,
            border_style="single",
            shading=[["lightgray", "lightgray"], ["white", "white"], ["white", "white"]]
        )

        # 5. 添加脚注和尾注
        add_footnote_to_document(filepath=self.test_file, paragraph_index=0, footnote_text="第一个脚注")
        add_endnote_to_document(filepath=self.test_file, paragraph_index=1, endnote_text="第一个尾注")

        # 6. 自定义脚注样式
        customize_footnote_style(
            filepath=self.test_file,
            numbering_format="a, b, c",
            font_size=8
        )

        # 7. 保护文档
        protect_document(filepath=self.test_file, password="workflow123")

        # 8. 验证保护状态
        base_path, _ = os.path.splitext(self.test_file)
        metadata_file = f"{base_path}.protection"
        self.assertTrue(os.path.exists(metadata_file))

        # 9. 解除保护
        unprotect_document(filepath=self.test_file, password="workflow123")

        # 10. 验证最终内容
        doc_text = get_document_text(self.test_file)
        self.assertIn("第一个段落", doc_text["text"])
        self.assertIn("第二个段落", doc_text["text"])

    def test_multiple_footnotes_endnotes(self):
        """测试多个脚注和尾注"""
        create_document(filepath=self.test_file)

        # 添加多个段落
        for i in range(3):
            add_paragraph(filepath=self.test_file, text=f"段落{i+1}")

        # 添加多个脚注
        for i in range(3):
            add_footnote_to_document(
                filepath=self.test_file,
                paragraph_index=i,
                footnote_text=f"脚注{i+1}"
            )

        # 添加多个尾注
        for i in range(3):
            add_endnote_to_document(
                filepath=self.test_file,
                paragraph_index=i,
                endnote_text=f"尾注{i+1}"
            )

        # 验证文档内容
        doc_text = get_document_text(self.test_file)
        self.assertIn("脚注:", doc_text["text"])
        self.assertIn("尾注:", doc_text["text"])

    def test_table_format_edge_cases(self):
        """测试表格格式化的边界情况"""
        create_document(filepath=self.test_file)

        # 测试无效表格索引
        with self.assertRaises(ValidationError):
            format_table(filepath=self.test_file, table_index=0)  # 没有表格

        # 添加表格后测试
        add_table(filepath=self.test_file, rows=1, cols=1, data=[["单元格"]])

        # 测试无效的边框样式
        with self.assertRaises(ValidationError):
            format_table(filepath=self.test_file, table_index=0, border_style="invalid")


if __name__ == '__main__':
    unittest.main()