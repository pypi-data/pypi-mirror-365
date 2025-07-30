"""运行所有新功能测试的脚本"""

import os
import sys
import unittest

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_new_feature_tests():
    """运行所有新功能的测试"""
    # 导入所有测试模块
    from test_create_document import TestCreateDocument
    from test_get_document_info import TestGetDocumentInfo
    from test_get_document_text import TestGetDocumentText
    from test_get_document_outline import TestGetDocumentOutline

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加各个测试类
    suite.addTests(loader.loadTestsFromTestCase(TestCreateDocument))
    suite.addTests(loader.loadTestsFromTestCase(TestGetDocumentInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestGetDocumentText))
    suite.addTests(loader.loadTestsFromTestCase(TestGetDocumentOutline))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果统计
    print(f"\n{'='*60}")
    print(f"测试结果总结:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print(f"\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print(f"\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n成功率: {success_rate:.1f}%")
    print(f"{'='*60}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_new_feature_tests()
    sys.exit(0 if success else 1)