from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import render_to_response


def index(request):
    return render_to_response("game.html")


def error_404(request):
    """ todo should use the django default mathod """
    return render_to_response("error_404.html")