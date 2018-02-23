from django.contrib import admin
from django.contrib.auth.views import logout
from django.urls import path, include

from .views import (
    HomeView, BlockListCreateView, BlockListUpdateView,
    BlockListListView, BlockListDetailView, BlockListDeleteView,
    BlockListSubscribeView, BlockListUnSubscribeView)
from .resources import BlockListResource

urlpatterns = [
    # Internals
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', logout, {'next_page': '/'}, name='logout'),

    # App
    path('', HomeView.as_view(), name='home'),
    path('block-list/', BlockListListView.as_view(), name='block-list-list'),
    path('block-list/add/', BlockListCreateView.as_view(), name='block-list-add'),
    path('block-list/<int:pk>/', BlockListDetailView.as_view(), name='block-list-detail'),
    path('block-list/update/<int:pk>/', BlockListUpdateView.as_view(), name='block-list-update'),
    path('block-list/subscribe/<int:pk>/', BlockListSubscribeView.as_view(), name='subscribe'),
    path('block-list/unsubscribe/<int:pk>/', BlockListUnSubscribeView.as_view(), name='unsubscribe'),
    path('block-list/delete/<int:pk>/', BlockListDeleteView.as_view(), name='block-list-delete'),

    # API
    path('api/block-list/', include(BlockListResource.urls())),
]


from django.conf import settings
from django.conf.urls import include, url

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]