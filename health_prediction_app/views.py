# views.py
from django.shortcuts import render
from .forms import AttributeSelectionForm
import csv
from pathlib import Path
import json

APP_DIR = Path(__file__).resolve().parent

def calculate_attribute_sums(request, selected_attributes):
    sums = {col: 0 for col in ['Body', 'Cardiac', 'Pulmonary', 'Muscle', 'Immune', 'Renal', 'Hepatic', 'Metabolic', 'Brain']}
    attribute_count = {col: 0 for col in sums}  # Initialize attribute count for each column

    with open(APP_DIR / 'data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if the attribute in the row is one of the selected attributes
            if row['Attribute'] in selected_attributes:
                # Increment attribute_count only if the value is not '0'
                for col in sums:
                    if float(row.get(col, 0)) != 0:
                        attribute_count[col] += 1
                    sums[col] += float(row.get(col, 0))

    # Calculate averages only for columns with non-zero attribute_count
    averages = {col: sums[col] / attribute_count[col] if attribute_count[col] != 0 else 0 for col in sums}
    
    # Load advice data from JSON file
    with open(APP_DIR / 'advice.json', 'r') as advice_file:
        advice_data = json.load(advice_file)

    # Load precaution data from JSON file
    with open(APP_DIR / 'precautions.json', 'r') as precaution_file:
        precautions_data = json.load(precaution_file)
        
    with open(APP_DIR / 'statements.json', 'r') as statement_file:
        statements_data = json.load(statement_file)

    # Initialize dictionaries to store advice, precautions, and statements for each organ system
    advice_results = {}
    precautions_results = {}
    statement_results = {}

    for system_name, health_score in averages.items():
        # Fetch advice based on health score
        for advice_block in advice_data['advice']:
            if advice_block['system_name'] == system_name:
                advice_range = advice_block['advice_range']
                if advice_range[0] < health_score <= advice_range[1]:
                    advice_results[system_name] = advice_block['health_advices']

        # Fetch precautions based on health score
        for precaution_block in precautions_data['precautions']:
            if precaution_block['system_name'] == system_name:
                precaution_range = precaution_block['precaution_range']
                if precaution_range[0] < health_score <= precaution_range[1]:
                    precautions_results[system_name] = precaution_block['precautions_details']
                    
        for statement_block in statements_data['statements']:
            if statement_block['system_name'] == system_name:
                statement_range = statement_block['health_score_range']
                if statement_range[0] < health_score <= statement_range[1]:
                    statement_info = {
                        'quote': statement_block['quote'],
                        'author': statement_block['author'],
                        'statement': statement_block['statement']
                    }
                    statement_results[system_name] = statement_info
                
                

    # Return the computed averages, advice, and precautions
    return averages, advice_results, precautions_results, statement_results

def attribute_selection_view(request):
    if request.method == 'POST':
        form = AttributeSelectionForm(request.POST)
        if form.is_valid():
            selected_attributes = form.cleaned_data['selected_attributes']
            averages, advice_results, precautions_results, statement_results  = calculate_attribute_sums(request, selected_attributes)
            #print(averages)
            return render(request, 'result_template.html', {
                'averages': averages,
                'advice_results': advice_results,
                'precautions_results': precautions_results,
                'statement_results' : statement_results
            })  # Pass sums to the template context
    else:
        form = AttributeSelectionForm()
    return render(request, 'form_template.html', {'form': form})

