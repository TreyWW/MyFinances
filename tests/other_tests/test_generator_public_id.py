import unittest
from unittest.mock import MagicMock
from django.core.exceptions import ValidationError
from django.db import models
from backend.utils.generator_public_id import generate_public_id

# Mock Django model for testing
class Invoice(models.Model):
    public_id = models.CharField(max_length=100, blank=True, null=True)

class TestGeneratePublicId(unittest.TestCase):
    def setUp(self):
        """
        This method will run before every test.
        Here we prepare any necessary setup for the tests.
        """
        # Create a mock Invoice model instance
        self.invoice = Invoice()

    def test_generate_public_id_format(self):
        """
        Test if the generated public_id is in the correct format: <prefix>-<uuid>.
        """
        public_id = generate_public_id(self.invoice)
        
        # Ensure it starts with the correct prefix (first 3 letters of class name)
        self.assertTrue(public_id.startswith("inv-"))
        
        # Check that the public_id contains an 8-character UUID after the prefix
        self.assertEqual(len(public_id.split("-")[1]), 8)
        
    def test_generate_unique_public_id(self):
        """
        Test if the generated public_id is unique.
        """
        # Mock the database query to simulate an existing public_id
        Invoice.objects.filter = MagicMock(return_value=[MagicMock()])  # Simulate that there is an existing public_id
        
        # Call the generate_public_id method, which should check for uniqueness
        public_id = generate_public_id(self.invoice)
        
        # Ensure that the public_id is unique and has the correct format
        self.assertTrue(public_id.startswith("inv-"))
        self.assertEqual(len(public_id.split("-")[1]), 8)
        
        # Ensure that filter was called to check for existing IDs
        Invoice.objects.filter.assert_called_once()

    def test_generate_public_id_invalid_entity(self):
        """
        Test if the function raises a ValidationError for invalid entities.
        """
        with self.assertRaises(ValidationError):
            # Pass a non-model instance (e.g., a simple dictionary)
            generate_public_id({})  # Invalid input, not a Django model instance

    def test_generate_public_id_unique_in_database(self):
        """
        Test if the public_id is unique in the database.
        """
        # Mocking the existence of a public_id in the database
        existing_invoice = Invoice(public_id="inv-12345678")
        existing_invoice.save()  # Save the mock invoice with the public_id in the database
        
        # Simulate the creation of a new invoice and the public_id generation
        new_invoice = Invoice()
        new_public_id = generate_public_id(new_invoice)
        
        # Assert that the public_id for the new invoice is different from the existing one
        self.assertNotEqual(new_public_id, existing_invoice.public_id)
    
    def test_generate_public_id_with_multiple_calls(self):
        """
        Test if the public_id is unique across multiple calls.
        """
        # Mock the database query to simulate no public_id existing
        Invoice.objects.filter = MagicMock(return_value=[])
        
        # Generate multiple public_ids and check they are unique
        public_id_1 = generate_public_id(self.invoice)
        public_id_2 = generate_public_id(self.invoice)
        
        self.assertNotEqual(public_id_1, public_id_2)

if __name__ == "__main__":
    unittest.main()
