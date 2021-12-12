from django.views.generic import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about_author.html'


class AboutTechView(TemplateView):
    template_name = 'about_tech.html'
