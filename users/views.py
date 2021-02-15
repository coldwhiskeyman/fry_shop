from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView

from shops.models import Promotion, Purchase
from users.forms import DepositForm, RegisterForm
from users.models import User


class UserLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse('index')


class UserLogoutView(LogoutView):
    next_page = '/'


class UserCreateView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse('index')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)

        login(self.request, user)

        return HttpResponseRedirect(self.get_success_url())


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    login_url = '/users/login'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)

        promotions_cache_key = f'promotions:{self.request.user.username}'
        promotions = Promotion.objects.all()
        cache.get_or_set(promotions_cache_key, promotions, 600)

        context['promotions'] = promotions
        context['form'] = DepositForm()
        purchase_history = Purchase.objects.filter(user=self.request.user, complete=True)
        context['purchase_history'] = purchase_history

        return context


class DepositView(FormView):
    form_class = DepositForm

    def form_valid(self, form):
        amount = int(self.request.POST['amount'])
        user = self.request.user
        user.balance += amount
        user.save()
        return super(DepositView, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk': self.request.user.id})
