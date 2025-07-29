import unittest
from odeta import odeta

class Testodeta(unittest.TestCase):
    def setUp(self):
        self.db = odeta(":memory:")
        self.users = self.db.table("users")

    def test_put_and_fetch(self):
        user_id = self.users.put({"name": "Bob Johnson"})
        users = self.users.fetch()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['name'], "Bob Johnson")

    def test_fetch_with_query(self):
        self.users.put({"name": "Bob Johnson"})
        self.users.put({"name": "Alice Smith"})
        users = self.users.fetch({"name": "Bob Johnson"})
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['name'], "Bob Johnson")

if __name__ == '__main__':
    unittest.main()