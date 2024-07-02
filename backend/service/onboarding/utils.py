def generate_unique_slug(manager, field, slug):
    """
    Generate a unique slug for a model instance.

    Args:
        manager (django.db.models.Manager): The model manager instance.
        field (str): The name of the field to check for uniqueness.
        slug (str): The initial slug value.

    Returns:
        str: A unique slug value.
    """
    # Get the model instance with the given slug
    instance = manager.filter(**{field: slug})

    # If no instance exists with the given slug, return it
    if not instance.exists():
        return slug

    # Otherwise, append a unique suffix to the slug
    suffix = 1
    unique_slug = f"{slug}-{suffix}"

    while manager.filter(**{field: unique_slug}).exists():
        suffix += 1
        unique_slug = f"{slug}-{suffix}"

    return unique_slug
