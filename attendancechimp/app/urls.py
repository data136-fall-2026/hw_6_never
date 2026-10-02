from django.urls import path
from . import views

urlpatterns = [
    # HW2
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    # HW4
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    path('new', views.new, name='new'),
    path('createUser', views.createUser, name='createUser'),
    # HW5.1
    path('new_course', views.new_course, name='course_create'),
    path('new_lecture', views.new_lecture, name='qr_create'),
    path('new_qr_upload', views.new_qr_upload, name='qr_upload'),
    # HW5.2
    path('createCourse/', views.createCourse, name='createCourse'),
    # HW5.3
    path('createLecture/', views.createLecture, name='createLecture'),
    # HW5.4
    path('createQRCodeUpload/', views.createQRCodeUpload, name='createQRCodeUpload'),
   # HM5.5
    path('dumpUploads', views.dumpUploads, name='dumpUploads'),
]
