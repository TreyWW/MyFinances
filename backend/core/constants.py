# Backend core cosntant.py
"""
Constants used across the application for model field attributes.
"""

# Field length constants
MAX_LENGTH_STANDARD = 100  # Most commonly used max_length
MAX_LENGTH_NAME = 64  # Used for name fields
MAX_LENGTH_DESCRIPTION = 500  # Used for description fields
MAX_LENGTH_EMAIL = 254  # Standard max length for email fields
MAX_LENGTH_FIRST_LAST_NAME = 150  # Used for first and last name fields
MAX_LENGTH_CHOICE_FIELD = 20  # Used for choice fields
MAX_LENGTH_CURRENCY = 3  # Used for currency codes

# Decimal field constants
DECIMAL_MAX_DIGITS = 15
DECIMAL_PLACES = 2

# Common help texts
STAFF_STATUS_HELP_TEXT = "Designates whether the user can log into this admin site."
ACTIVE_STATUS_HELP_TEXT = "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
GROUPS_HELP_TEXT = "The groups this user belongs to. A user will get all permissions granted to each of their groups."
