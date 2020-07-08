from flask_login import current_user
from wtforms import SelectMultipleField, widgets


# класс для поля с несколькими чекбоксами
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

