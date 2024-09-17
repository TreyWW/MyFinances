window.validate_sort_code = function validate_sort_code(value) {
  // Remove any non-numeric characters
  value = value.replace(/\D/g, '');

  // Ensure the value is no longer than 9 characters (123-123-123)
  if (value.length > 6) {
    value = value.slice(0, 6);
  }

  // Format the value as "12-34-56"
  if (value.length >= 2) {
    value = value.slice(0, 2) + "-" + value.slice(2);
  }
  if (value.length >= 5) {
    value = value.slice(0, 5) + "-" + value.slice(5);
  }

  return value;
}

window.validate_account_number = function validate_account_number(value) {
  // Remove any non-numeric characters
  value = value.replace(/\D/g, '');

  // Ensure the value is no longer than 16 characters (1234-1234-1234-1234)
  if (value.length > 8) {
    value = value.slice(0, 8);
  }

  return value;
}
