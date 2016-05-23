from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import Home, Project_view, RecomendedProjects_view, AboutView, OurPeople, Create_skill, Edit_project, Profile, Category_view, Category_view_filter, Sub_category_view_filter, Users_view, Settings, Create_project, Register, Login, Create_profile, Trueques, Set_Password, solicitar_cambio_contrasena, cambiar_contrasena_usuario, Dashboard, register_comment, ProjectComments, UserComments, ProjectComment
import views
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns(
    '',
    url(r'^likes/', include('phileo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', Home.as_view(), name='index'),
    url(r'^proyecto/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', Project_view.as_view(), name='project'),
    url(r'^proyecto/editar/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', Edit_project.as_view(), name='editproject'),
    url(r'^perfil/(?P<slug>[-_\w]+)/$', Profile.as_view(), name='profile'),
	url(r'^dashboard/(?P<slug>[-_\w]+)/$', Dashboard.as_view(), name='dashboard'),
    url(r'^descubre/$', Category_view.as_view() , name='category'),
	url(r'^colabora/(?P<tipo>\w+)/$', RecomendedProjects_view.as_view() , name='matches'),
    url(r'^descubre/(?P<category>\w+)/$', Category_view_filter.as_view(), name='subcategory'),
    url(r'^descubre/(?P<category>\w+)/(?P<subcategory>\w+)/$', Sub_category_view_filter.as_view(), name='detailsubcategory'),
    url(r'^encuentra/$', Users_view.as_view() , name='encuentra'),
    url(r'^register/$', Register.as_view(), name='register'), 
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^register/perfil/$', Create_profile.as_view(), name='createprofile'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^configuracion/(?P<username>\w+)/$', login_required(Settings.as_view()), name='settings'),
    url(r'^crea/$', login_required(Create_project.as_view()), name='create'),
    url(r'^crea/habilidad/$', login_required(Create_skill.as_view()), name='createSkill'),
    url(r'^froala_editor/', include('froala_editor.urls')),
    #url(r'^mensajes/', include('postman.urls', app_name='postman')),
    url(r'^colaborar/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', login_required(views.register_collaborator), name='collaborate'),
    url(r'^colaboraciones/(?P<username>\w+)/(?P<tipo>\w+)/$', login_required(Trueques.as_view()), name='trueques'),
    url(r'^colaboraciones/cerrar/(?P<collaboration>\w+)/(?P<type_true>[0-9])/$', views.Close_trueque, name='cerrarTrueque'),
    url(r'^acerca_de_troca$', AboutView.as_view(), name='about'),
    url(r'^quienes_somos', OurPeople.as_view(), name='ourpeople'),
	(r'^mensajes/', include('django_messages.urls')),
	url(r'^feedback/', include('feedback_form.urls')),
	url(r'^cerrar_perfil/(?P<username>\w+)/$', views.cerrar_usuario, name='cerrarPerfil'),
	url(r'^cerrar_proyecto/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', views.cerrar_proyecto, name='cerrarProyecto'),
	url(r'^nueva_contrasena/(?P<slug>\w+)/$', Set_Password.as_view(), name='nueva_contrasena'),
	url(r'^cambiar_contrasena/(?P<nombre_usuario>\w+)/$', solicitar_cambio_contrasena, name='solicitar_cambio_contrasena'),
	url(r'^cambiar_contrasena_usuario/(?P<contrasena>\w+)/(?P<nombre>\w+)/$', cambiar_contrasena_usuario, name='cambiar_contrasena_usuario'),
	url(r'^comentar/(?P<usernameComment>\w+)/(?P<projectSlug>[-_\w]+)/(?P<comment>\w+)/$', login_required(register_comment), name='register_comment'),
	url(r'^comentarios/(?P<slug>[-_\w]+)/$', ProjectComments.as_view(), name='get_project_comments'),
	url(r'^comentario/(?P<pk>[0-9]+)/$', ProjectComment.as_view(), name='get_comment'),
	url(r'^comentarios/usuario/(?P<slug>\w+)/$', UserComments.as_view(), name='get_user_comments'),
)

urlpatterns += staticfiles_urlpatterns()

# urlpatterns += patterns('',
#     url(r'^articles/comments/', include('django_comments.urls')),
# )

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )

