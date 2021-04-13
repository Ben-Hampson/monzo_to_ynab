from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.contrib import messages
from pprint import pprint
import csv

# Create your views here.
def index(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        print(uploaded_file.size)
        print(uploaded_file.content_type)
        
        if uploaded_file.content_type != "text/csv":
            print("Please select a .csv file.")
            messages.error(request, "Please select a .csv file.")
            return redirect('home')

        if uploaded_file.size > 1000000:
            messages.error(request, f"This file is too big ({uploaded_file.size / 1000000:.2f}MB). Please choose a CSV file that is 1MB or less.")
            print("File too big.")
            return redirect('home')

        monzo_content = uploaded_file.read()
        monzo = monzo_content.decode('UTF-8').split('\n')
        
        monzo_csv = csv.DictReader(monzo)
        ynab_dict = []
        try:
            for row in monzo_csv:
                ynab_row = {
                    'Date': row['Date'],
                    'Payee': row['Name'],
                    'Memo': row['Notes and #tags'],
                    'Outflow': row['Money Out'].strip('-'),
                    'Inflow': row['Money In'],
                }
                ynab_dict.append(ynab_row)
        except KeyError as e:
            error_msg = "Error: Expected CSV column header not found:" + f" {e}"
            print(error_msg)
            messages.error(request, error_msg)
            return redirect('home')

        response = HttpResponse(content_type='text/csv')

        fieldnames = ['Date', 'Payee', 'Memo', 'Outflow', 'Inflow']
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in ynab_dict:
            writer.writerow(row)
        
        response['Content-Disposition'] = 'attachment; filename="YNAB.csv"'

        return response

    return render(request, 'conv/index.html')