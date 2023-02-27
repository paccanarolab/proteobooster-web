from django.http import HttpResponse
from django.shortcuts import render
from django import forms
from .models import Protein


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

# Create your views here.
class HomePageForm(forms.Form):
    protein_accession = forms.CharField(required=True)

def home(request):
    if request.method == "POST":
        home_page_form = HomePageForm(request.POST)
        if home_page_form.is_valid():
            return render(request, "home.html")
    return render(request, "home.html") 

def protein(request, protein_accession):
    return render(request, "home.html") 

def organism(request, organism_taxon_id):
    return render(request, "home.html") 

def interaction(request, first_accession, second_accession):
    return render(request, "home.html") 

def interolog(request, first_accession, second_accession):
    return render(request, "home.html") 

def complex(request, predicted_complex_id):
    return render(request, "home.html") 

def go_term(request, go_term_goid):
    return render(request, "home.html") 


# API
def get_proteins(request):
    data = "fail"
    if request.method == "GET":
        data = {"message":"success"}
    mimetype = "application/json"
    return HttpResponse(content=data, content_type=mimetype)

