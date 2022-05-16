from django.shortcuts import render, redirect


def home(request):
    return redirect('/WB/')
    return render(request, 'home.html')  # not needed as a redirect is used
