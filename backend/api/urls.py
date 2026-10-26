from django.urls import re_path

from . import views

# Las rutas aceptan con o sin "/" final para que Angular no reciba redirecciones 301 en POST.
urlpatterns = [
    re_path(r'^usuarios/login/?$', views.LoginView.as_view(), name='usuarios-login'),
    re_path(r'^usuarios/registro/?$', views.RegistroView.as_view(), name='usuarios-registro'),
    re_path(r'^catalogo/?$', views.CatalogoListCreateView.as_view(), name='catalogo'),
    re_path(r'^catalogo/(?P<pk>\d+)/?$', views.CatalogoDetailView.as_view(), name='catalogo-detalle'),
    re_path(r'^catalogo/(?P<pk>\d+)/apartar/?$', views.ApartarLoteView.as_view(), name='catalogo-apartar'),
    re_path(r'^apartados/?$', views.ApartadosListView.as_view(), name='apartados'),
    re_path(r'^apartados/(?P<pk>\d+)/estado/?$', views.CambiarEstadoApartadoView.as_view(), name='apartados-estado'),
]
