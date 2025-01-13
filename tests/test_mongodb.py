import unittest
import sys
import os
from bson import ObjectId

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from services.mongodb.mongodb import mongo_db

class TestMongoDB(unittest.TestCase):
    def setUp(self):
        self.collection_name = 'test_collection'
        self.test_document = {
            '_id': ObjectId(),
            'name': 'Test Name',
            'value': 123
        }

    def test_insert_one(self):
        inserted_id = mongo_db.insert_one(self.collection_name, self.test_document)
        self.assertIsNotNone(inserted_id)

    def test_find_one(self):
        mongo_db.insert_one(self.collection_name, self.test_document)
        found_document = mongo_db.find_one(self.collection_name, {'_id': self.test_document['_id']})
        self.assertEqual(found_document['name'], self.test_document['name'])

    def tearDown(self):
        # 清理测试数据
        mongo_db.get_collection(self.collection_name).delete_many({})

if __name__ == '__main__':
    unittest.main()
