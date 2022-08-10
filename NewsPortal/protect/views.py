from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class MyView(PermissionRequiredMixin, View):
    permission_required = ('<app>.<action>.<model>',
                           '<app>.<action>.<model>')


class AddProduct(PermissionRequiredMixin, CreateView):
    permission_required = ("shop.add_authors", )