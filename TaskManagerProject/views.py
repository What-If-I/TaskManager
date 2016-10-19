from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from .forms import RegistrationForm
from django.urls.base import reverse
from django.shortcuts import redirect


class RegistrationView(FormView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    success_url = 'register/done/'

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(self.request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('register-success'))

        else:
            return self.render_to_response(context={
                'form': form,
            })


class RegistrationDoneView(TemplateView):
    template_name = 'registration/success.html'
