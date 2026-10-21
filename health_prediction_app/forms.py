# forms.py
from django import forms
import csv
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

class AttributeSelectionForm(forms.Form):
    selected_attributes = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(AttributeSelectionForm, self).__init__(*args, **kwargs)
        
        # Fetch attribute choices from CSV file during initialization
        attribute_choices = self.get_attribute_choices()
        self.fields['selected_attributes'].choices = attribute_choices

    def get_attribute_choices(self):
        with open(APP_DIR / 'data.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            attribute_choices = [(row['Attribute'], row['Attribute']) for row in reader]
        return attribute_choices
