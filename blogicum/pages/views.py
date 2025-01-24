from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


class RegistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:profile')


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def handler500(request):
    return render(request, 'pages/500.html', status=500)


def handler404(request, exception):
    return render(request, 'pages/404.html', status=404)


def handler403csrf(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
