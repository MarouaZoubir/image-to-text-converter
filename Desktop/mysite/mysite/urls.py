
from django.contrib import admin
from django.urls import path
from mysite import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('textToSpeech/', views.textToSpeech, name='textToSpeech'),
    path('convert-to-audio/', views.convert_to_audio, name='convert_to_audio'),
    path('image-processing/', views.image_processing, name='image_processing'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
