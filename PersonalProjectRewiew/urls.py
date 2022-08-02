"""PersonalProjectRewiew URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from Anecdotes.views import AnecdoteApiView, AnecdoteDetailsApiView, CommentApiView, RateApiView, ReactionApiView
from Users.views import UserApiView, UserEditApiView, UserDeactivateApiView, UserDeleteApiView

# should add endpoint that return anecdotes by given categories (multi-select) someday - already have logic in
# previous review project
urlpatterns = [
    path('admin/', admin.site.urls),
    path('anecdote/', AnecdoteApiView.as_view()),
    path('anecdote/<int:id>/', AnecdoteDetailsApiView.as_view()),
    path('anecdote/<int:id>/comment/', CommentApiView.as_view()),
    path('anecdote/<int:id>/rate/', RateApiView.as_view()),
    path('anecdote/<int:id>/reaction/', ReactionApiView.as_view()),
    path('user/register/', UserApiView.as_view()),
    path('user/profile/', UserApiView.as_view()),
    path('user/edit/', UserEditApiView.as_view()),
    path('user/delete/', UserDeleteApiView.as_view()),
    path('user/deactivate/', UserDeactivateApiView.as_view()),
    path(rf'user/<int:id>/<slug:response_>/', UserApiView.as_view())
]
