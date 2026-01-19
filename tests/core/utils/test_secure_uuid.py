from django.test import SimpleTestCase, override_settings

from backend.core.utils.secure_uuid import get_uuid, revert_uuid


@override_settings(UUID_AES_KEY=b"0123456789abcdef")
class SecureUUIDTestCase(SimpleTestCase):
    def test_same_input_produces_same_uuid(self):
        u1 = get_uuid(12345, "Transaction")
        u2 = get_uuid(12345, "Transaction")

        self.assertEqual(u1, u2)

    def test_different_ids_produce_different_uuids(self):
        u1 = get_uuid(1, "Transaction")
        u2 = get_uuid(2, "Transaction")

        self.assertNotEqual(u1, u2)

    def test_different_model_names_produce_different_uuids(self):
        u1 = get_uuid(42, "Transaction")
        u2 = get_uuid(42, "Account")

        self.assertNotEqual(u1, u2)

    def test_numeric_id_is_recoverable(self):
        original_id = 987654321
        u = get_uuid(original_id, "Invoice")

        recovered_id = revert_uuid(u)

        self.assertEqual(recovered_id, original_id)

    def test_uuid_is_deterministic_for_same_model_name(self):
        u1 = get_uuid(100, "Invoice")
        u2 = get_uuid(100, "Invoice")

        self.assertEqual(u1, u2)

    def test_negative_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_uuid(-1, "Transaction")

    def test_revert_uuid_returns_int(self):
        u = get_uuid(7, "Category")
        recovered_id = revert_uuid(u)

        self.assertIsInstance(recovered_id, int)
