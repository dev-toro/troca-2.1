from django import template
from troca.models import Project, Skills_categories, Skills, UserProfile, Collaboration, CambioContrasena, Comment
register = template.Library()

@register.simple_tag
def get_skill(user):
    userProfile = UserProfile.objects.get(user=user) 
    obj = user_profile.category.all()
    return obj


@register.filter(name='user_gives') # 0:no puede nada | 1:puede donar | 2:puede trocar
def is_user_gives_to_project(usu, project):	# Set(user_skills)   
	estado=0;
	cat=set({})
	if usu and project.user != usu.user:
		cat=set(project.category.all()) & set(usu.category.all())
		if len( cat)>0:
			estado=1;
			userProjects = Project.objects.all().filter(user=usu.user).filter(isActive=True)	# Proyectos del usuario
			needs_userProjects=set([]) # crea un set vacio para las necesidades del usuario
			for y in userProjects.all():
				needs_userProjects.update(y.category.all()) # agrega las necesidades nuevas al set
			autor_profile = UserProfile.objects.get(user=project.user)
			autor_skills = set(autor_profile.category.all()) # set de habilidades del autor del proyecto
			cat_rev=autor_skills&needs_userProjects
			if len( cat_rev)>0:
				estado=2      
	print(str(project)+"\n"+str(project.user)+"\n"+str(autor_profile)+"\n")
	return estado
 
@register.filter(name='trueques_no_leidos') 
def trueques_no_leidos(usu):	
	col = len(Collaboration.objects.all().filter(autor=usu).filter(visto=False))
	res=""
	if col>0:
		res="("+str(col)+")"
	return res

@register.filter(name='comentarios_no_leidos') 
def comentarios_no_leidos(usu):	
	col = len(Comment.objects.all().filter(userProject=usu).exclude(userComment=usu).filter(visto=False))
	res=""
	if col>0:
		res="("+str(col)+")"
	return res

@register.filter(name='get_responds') 
def get_responds(com):	
	return com.responds.all();

@register.filter(name='get_html_responds') 
def get_html_responds(pk):
	print(str(com));
	res= '<div class="respuesta">';
	res +='<div class="fotoComentario" style="display: inline-block; width:30px;">';
	res +='<a href="/perfil/'+str(com.userRespond.id)+'">';
	res +='<div class="img-container-user circular" style="background-image: url(\''+str(com.userProfileRespond.avatar_url.url_700x700)+'\');  width:30px;  height:30px;">';
	res +='</div>';
	res +='</a>';
	res +='</div>';
	res +='<div class="infoComentario" style="display: inline-block;">';
	res +='<h5 class="mb0"><a href="/perfil/'+str(com.userRespond.id)+'">'+str(com.userRespond.username)+'</a> </h5> ';
	res +='<p class="mb0 comentario">';
	res +='"'+str(com.respond)+'"';
	res +='</p>';
	res +='</div>';
	res +='</div>';
	return res;	
	


  
  