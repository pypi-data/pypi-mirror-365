import unittest

from pr_properties import pr_properties
from pr_properties.pr_properties import PropertiesHandler


class Test(unittest.TestCase):
    def test_03(self):
        for i in range(100):
            p = pr_properties
            p.read(r"./pool.properties")
            p.write()

    def test_04(self):
        for i in range(100):
            p = PropertiesHandler(r"./pool.properties").read()
            p['master.database'] = f'test_{i}'
            p.write()

    def test_01(self):
        p = pr_properties
        p.read(r"./pool.properties")
        # 新增
        p['999'] = 99
        # 写入新增的内容
        p.write()

    def test_02(self):
        p = PropertiesHandler(r"./pool.properties").read()
        print(p.get('kk'))
        print('dumps', p)
        p['000'] = 3333
        p[2] = 33331
        p['ks.1'] = 4
        p['ks.2'] = 4
        # 修改删除
        p['kk'] = 35
        del p['ks.2']
        print('\n' + p.__str__())
        p.write()
