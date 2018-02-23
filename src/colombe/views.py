from django.views.generic import TemplateView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse

from .models import BlockList, Subscription
from .forms import BlockListForm


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if user.is_authenticated:
            context["block_lists"] = user.blocklist_set.all()
            context["subscriptions"] = user.subscription_set.all().select_related('block_list')

        return context


class BlockListListView(ListView):
    model = BlockList
    template_name = "blocklist_list.html"


@method_decorator(login_required, name='dispatch')
class BlockListCreateView(CreateView):
    model = BlockList
    template_name = "blocklist_form.html"
    form_class = BlockListForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user

        twitter = self.request.user.twitter
        user_ids = []
        for name in self.request.POST.get('users').split('\r\n'):
            user_id = twitter.get_user_id_from_screen_name(name)
            if user_id:
                user_ids.append(user_id)

        self.object.users = user_ids

        return super().form_valid(form)


class BlockListDetailView(TemplateView):
    template_name = "blocklist_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        block_list = BlockList.objects.get(pk=self.kwargs.get("pk"))
        context["block_list"] = block_list

        if self.request.user.is_authenticated:
            context["subscribed"] = False
            if Subscription.objects.filter(user=self.request.user, block_list=block_list).exists():
                context["subscribed"] = True

        return context


@method_decorator(login_required, name='dispatch')
class BlockListUpdateView(UpdateView):
    model = BlockList
    form_class = BlockListForm
    template_name = "blocklist_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        twitter = self.request.user.twitter
        users = []
        for user_id in self.object.users:
            name = twitter.get_user_screen_name_from_id(user_id)
            if name:
                users.append(name)
        context["users"] = '\r\n'.join(users)

        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        as_id = self.request.POST.get('users_as_id') == 'on'

        twitter = self.request.user.twitter
        user_ids = []
        for name in self.request.POST.get('users').split('\r\n'):
            if as_id:
                try:
                    user_id = int(name)
                except ValueError:
                    continue
            else:
                user_id = twitter.get_user_id_from_screen_name(name)

            if user_id:
                user_ids.append(user_id)

        self.object.users = user_ids
        self.object.save()

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BlockListDeleteView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        BlockList.objects.get(pk=self.kwargs.get('pk')).delete()
        return reverse('home')


@method_decorator(login_required, name='dispatch')
class BlockListSubscribeView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        block_list = BlockList.objects.get(pk=self.kwargs.get('pk'))
        self.request.user.subscribe_to_block_list(block_list)

        return block_list.get_absolute_url()


@method_decorator(login_required, name='dispatch')
class BlockListUnSubscribeView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        block_list = BlockList.objects.get(pk=self.kwargs.get('pk'))
        self.request.user.unsubscribe_to_block_list(block_list)

        return block_list.get_absolute_url()
