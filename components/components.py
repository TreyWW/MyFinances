import os
from pathlib import Path

from django_components import component

from settings.helpers import get_var
import logging

import logging

logger = logging.getLogger(__name__)


# Your base component class
class SimpleComponent(component.Component):
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(**kwargs)
        return context_data


list_of_components_registered = []
list_of_created_classes = []


# Function to register components based on directory structure
def register_components(base_path, component_base_class):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.startswith("+") and file.endswith(".html"):
                # Generate the template name from the file path
                template_name = os.path.relpath(os.path.join(root, file), base_path)
                # Convert the template name to a component name
                component_name = template_name.replace(os.path.sep, ":").replace("+", "")[:-5]
                component_name = component_name.replace(":", ":")
                # Generate a class name from the component name
                class_name = "".join(part.capitalize() for part in component_name.split(":"))

                def class_decorator(cls):
                    # Add the @component.register decorator to the dynamically generated class
                    list_of_components_registered.append(component_name)
                    class_name_with_decoration = component.register(component_name)(cls)
                    return class_name_with_decoration

                # Create a class with the specified decorator
                component_class = type(
                    class_name,
                    (component_base_class,),
                    {"template_name": template_name},
                )
                component_class = class_decorator(component_class)

                # Print the class name and template name for debugging
                list_of_created_classes.append(component_class.__name__)
                # print(f"Class Name: {component_class.__name__}, Template Name: {template_name}")
                # list_of_created_classes


# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Register components in the "components" folder
DIR = os.path.join(BASE_DIR, "components")
register_components(DIR, SimpleComponent)

# Register components in the "frontend/templates" folder
DIR = os.path.join(BASE_DIR, "frontend/templates")
register_components(DIR, SimpleComponent)

all_components = [f"{a}    {b}" for a, b in zip(list_of_components_registered, list_of_created_classes)]

logging.debug(f"[BACKEND] Registered GLOBAL components: {all_components}")
logging.debug(f"[BACKEND] Registered component usable names: {list_of_components_registered}")
