"""Contact module's unit tests."""
import unittest

from rcr.contact import Contact


class TestContact(unittest.TestCase):
    def setUp(self) -> None:
        self.contact = Contact.get_instance()
        return super().setUp()

    def test_1_add(self):
        user_connection = (("localhost", 12345), "connection")
        self.assertEqual(self.contact.add(user_connection), 1)
        self.assertEqual(self.contact.add(user_connection), 2)
        self.assertEqual(self.contact.add(user_connection), 3)

    def test_2_list(self):
        self.assertEqual(self.contact.list(), [1, 2, 3])

    def test_3_get(self):
        expected_user_connection = (("localhost", 12345), "connection")
        self.assertEqual(self.contact.get(1), expected_user_connection)

    def test_4_remove(self):
        self.assertTrue(self.contact.remove(1))
        self.assertFalse(self.contact.remove(10))

    def test_5_get_after_remove(self):
        self.assertIsNone(self.contact.get(1))

    def test_6_list_after_remove(self):
        self.assertEqual(self.contact.list(), [2, 3])

    def test_7_add_after_remove(self):
        user_connection = (("", 12345), "connection11")
        self.assertEqual(self.contact.add(user_connection), 1)
        self.assertEqual(self.contact.get(1), user_connection)

        user_connection = (("", 12345), "connection12")
        self.assertEqual(self.contact.add(user_connection), 4)
        self.assertEqual(self.contact.get(4), user_connection)

    def test_8_list_after_new_add(self):
        self.assertEqual(self.contact.list(), [2, 3, 1, 4])
