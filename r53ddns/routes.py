from fresco import Route, GET, POST, PUT, DELETE

import views

__routes__ = [
    Route('/users', views.User),
    Route('/', views.Root),
]

