def get_diff(old_instance, new_instance):
    """
    Compare two instances and return a dictionary of changes.
    
    Parameters:
    old_instance (object): The original instance before changes.
    new_instance (object): The modified instance after changes.

    Returns:
    dict: A dictionary containing the fields that have changed and their old and new values.
    """
    changes = {}
    
    old_data = old_instance.__dict__
    new_data = new_instance.__dict__

    for key in old_data:
        if key not in ['_state']:  # Ignore Django's internal state
            old_value = old_data[key]
            new_value = new_data.get(key)

            if old_value != new_value:
                changes[key] = {
                    'old': old_value,
                    'new': new_value
                }

    return changes


def format_diff(changes):
    """
    Format the changes into a human-readable string.

    Parameters:
    changes (dict): A dictionary of changes.

    Returns:
    str: A formatted string representing the changes.
    """
    formatted_changes = []
    
    for field, change in changes.items():
        formatted_changes.append(f"{field}: {change['old']} -> {change['new']}")

    return "\n".join(formatted_changes)