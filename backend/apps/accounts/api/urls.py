"""URL fragments exported by the accounts app.

An app publishes one list per API zone it participates in. config/api/*.py
mounts them. The app never decides its own prefix, and the zone never reaches
inside the app for view classes.
"""

from django.urls import path

from apps.accounts.api.views.auth import LoginView, LogoutView, RegisterView

auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

client_urlpatterns: list = []
dashboard_urlpatterns: list = []
