"""Internal zone: reserved, and empty on purpose.

This namespace exists so that restricted internal functions have an obvious
home the day they are needed, instead of being improvised into the dashboard
zone. Nothing is exposed here yet.

Anything added must be explicitly opened: the zone default is
``core.permissions.DenyAll``.
"""

app_name = "internal"

urlpatterns: list = []
