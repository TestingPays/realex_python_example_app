from django.conf.urls import url
from python_realex_payment import views as application

urlpatterns = [

    url(r'^$', application.main, name='index'),
    url(r'^auth', application.auth, name='charges'),
    url(r'^threedsecure$', application.three_d_secure, name='threedsecure'),
    url(r'^threedsverifysig/', application.three_ds_verify_signed, name='threedsverifysig'),
]
