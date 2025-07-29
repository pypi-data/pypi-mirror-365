# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-28 14:38
# @Author : 毛鹏
import unittest


from mangotools.data_processor import ObtainRandomData


class TestCacheTool(unittest.TestCase):
    def setUp(self):
        """在每个测试方法前初始化"""
        self.random = ObtainRandomData()

    def test_basic_operations(self):
        """测试基本缓存操作"""
        # 测试设置和获取缓存

        print(self.random.regular('number_random_bigint(digits=2)'))
        print(self.random.regular('randint(left=2,right=5)'))

if __name__ == '__main__':
    unittest.main()

