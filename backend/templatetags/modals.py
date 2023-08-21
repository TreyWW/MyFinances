from django import template
register = template.Library()

# @register.inclusion_tag('core/components/modal.html')
# def ripple_ui_modal(modals):
#     return {'modals': modals}