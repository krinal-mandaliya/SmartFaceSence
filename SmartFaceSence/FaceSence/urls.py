from django.urls import path
from . import views


urlpatterns = [
    path("login/",views.login,name="login"),
    path("index/",views.index,name="index"),
    path("flat/",views.flat,name="flat"),
    path("person/",views.person,name="person"),
    path("visitor/",views.visitor,name="visitor"),
    path("output/",views.output,name="output"),
    path("upload_img",views.upload_img,name="upload_img"),
    path("",views.homepage,name="homepage"),
    path('compare/', views.compare, name="compare"),
    path('compare1/', views.compare1, name="compare1"),
    path("signup/",views.signup,name="signup"),
    path("upload/",views.upload,name="upload"),
    path("scan/",views.scan,name="scan"),
    path("search_images/", views.search_images, name="search_images"),
    path("admin1",views.admin1,name="admin1"),
    path("send_forget_password_mail",views.send_forget_password_mail,name="send_forget_password_mail"),
    path('ForgetPassword/' , views.ForgetPassword , name="ForgetPassword"),
    path('ChangePassword/<str:token>/' , views.ChangePassword , name="ChangePassword"),
    path("editProfile/",views.editProfile,name="editProfile")
]