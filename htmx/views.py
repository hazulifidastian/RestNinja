from django.shortcuts import render


def hello(request):
    return render(request, "htmx/hello.html")


def contact(request):
    return render(request, "htmx/contact.html")
