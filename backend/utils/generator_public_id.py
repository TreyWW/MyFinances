import uuid
from django.core.exceptions import ValidationError
from django.db import models

UUID_LENGTH = 8
PREFIX_LENGTH = 3


def generate_public_id(entity: models.Model) -> str:
    """
    Generates a unique public ID for a given entity, based on its class type.
    The ID is in the format: <prefix>-<unique_id>. The prefix is based on
    the first three letters of the class name (e.g., 'invoice' -> 'inv').
    This function ensures that the generated ID does not already exist in the database.

    Args:
        entity (models.Model): The entity (Django model instance) for which to generate the public ID.

    Returns:
        str: A unique public ID string.
    
    Raises:
        ValidationError: If the provided entity is not a valid Django model instance.
    """
    # Validate that the provided entity is a Django model instance
    _validate_entity(entity)

    # Generate the public ID prefix using the first 3 letters of the class name
    prefix = _get_class_prefix(entity)

    # Generate a unique public ID that does not already exist in the database
    public_id = _generate_unique_public_id(entity, prefix)

    return public_id


def _validate_entity(entity: models.Model):
    """
    Validates that the entity is a valid Django model instance.

    Args:
        entity (models.Model): The entity to validate.

    Raises:
        ValidationError: If the entity is not a valid Django model instance.
    """
    if not isinstance(entity, models.Model):
        raise ValidationError("The entity provided is not a valid Django model instance.")


def _get_class_prefix(entity: models.Model) -> str:
    """
    Extracts the first N letters of the class name of the entity to form the prefix.

    Args:
        entity (models.Model): The entity for which to extract the class name.

    Returns:
        str: The prefix derived from the class name.
    """
    class_name = entity.__class__.__name__.lower()
    return class_name[:PREFIX_LENGTH]


def _generate_unique_public_id(entity: models.Model, prefix: str) -> str:
    """
    Generates a unique public ID based on the provided prefix. It ensures that the ID
    does not already exist in the database by checking and regenerating the ID if needed.

    Args:
        entity (models.Model): The entity for which to generate the public ID.
        prefix (str): The prefix for the public ID.

    Returns:
        str: A unique public ID string.
    """
    # Generate a unique UUID and truncate it to the specified length
    unique_id = str(uuid.uuid4())[:UUID_LENGTH]
    public_id = f"{prefix}-{unique_id}"

    # Check if the public_id already exists in the database
    while entity.__class__.objects.filter(public_id=public_id).exists():
        # Regenerate the unique ID if it exists in the database
        unique_id = str(uuid.uuid4())[:UUID_LENGTH]
        public_id = f"{prefix}-{unique_id}"

    return public_id
