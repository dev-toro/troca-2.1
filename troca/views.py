# -*- coding: utf-8 -*-

import datetime
import string
import random 
import base64
import hashlib
import hmac
import json as simplejson
import time

from django.views.generic import View, FormView, UpdateView, CreateView, DetailView, ListView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from forms import UserForm, UserProfileForm, ProjectForm, UserLoginForm, SkillForm, NewPasswordForm
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from registration.signals import user_activated
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache

from django.dispatch import receiver
from django.shortcuts import redirect
from django.http import Http404

from django.template import defaultfilters
from django.template.defaultfilters import slugify
from pure_pagination.mixins import PaginationMixin
from django.contrib.contenttypes.models import ContentType
from itertools import chain

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

# Import the models
from django.contrib.auth.models import User
from models import Project, Skills_categories, Skills, UserProfile, Collaboration, CambioContrasena, Comment, Respond
from django_messages.models import Message
from django_messages.forms import ComposeForm
from django_messages.utils import format_quote, get_user_model, get_username_field
from django import template

from operator import attrgetter

def get_cadena_aleatoria(tam=50):
	"""
	Genera una cadena aleatoria de tamaño tam.
	args:
		tam (int): tamaño de la cadena a generar.
	return:
		str: cadena de texto aleatoria.
	"""
	chars=string.ascii_uppercase + string.digits +string.ascii_lowercase
	return ''.join(random.choice(chars) for _ in range(tam))

def get_proyects_user_gives(usu,user):
	"""
	Busca los proyectos en los que un usauario puede colaborar entre todos los proyectos activos.
	args:
		usu (UserProfile): Perfil del usuario.
		user (user): Usuario.
	return:
		[Project]: Proyectos encontrados ordenados desde el más reciente.
	"""
	user_skills=set(usu.category.all())
	projects = Project.objects.all().filter(isActive=True).filter(num_needs__lt=100).exclude(user = user).order_by('-date')
	proyects_user_gives=[]
	for p in projects:
		#cat=set(p.category.all()) & user_skills
		if is_userSkills_gives_to_project(user_skills,p): # if len( cat)>0:
			proyects_user_gives.append(p)	
	return proyects_user_gives

def is_userSkills_gives_to_project(usu_skills, project):	# Set(user_skills)
	"""
	Compara las necesidades de un proyecto con las habilidades de un usuario para determinar si el usuario puede colaborar (trocar o donar) en el proyecto.
	args:
		usu_skills (Set(Skills)): Habilidades del usuario.
		project (Project): Proyecto a comparar.
	return:
		 bool: True si puede colaborar, False en caso contrario.
	"""
	cat=set(project.category.all()) & usu_skills
	return len( cat)>0
	
def is_user_gives_to_project(usu, project):	
	"""
	Compara las necesidades de un proyecto con las habilidades de un usuario para determinar si el usuario puede colaborar (trocar o donar) en el proyecto.
	args:
		usu (UserProfile): Habilidades del usuario.
		project (Project): Proyecto a comparar.
	return:
		 bool: True si puede colaborar, False en caso contrario.
	"""
	return is_userSkills_gives_to_project(set(usu.category.all()),project)
	
def solicitar_cambio_contrasena(response,nombre_usuario):
	"""
	Crea una solicitud para cambiar la contraseña a un usuario y envía un correo al usuario.
	args:
		response.
		nombre_usuario (str): Nombre del usuario que quiere realizar el cambio de contraseña.
	return:
		 HttpResponseRedirect: redirecciona al inicio.
	"""
	usuario =User.objects.get(username=nombre_usuario)
	now = datetime.datetime.now()
	# crea un id con la fecha y una cadena aleatoria.
	id= str(now).replace(" ","").replace(":","").replace(".","").replace("-","")+ get_cadena_aleatoria(35);	
	camcon=CambioContrasena(user=usuario,id=id,isActive=True)
	camcon.save()	
	s = "/nueva_contrasena/" + camcon.id     
	# envía un correo al usuario que quiere cambiar su contraseña.
	subject, from_email, to = 'Troca.cc', 'comunlaboratorio@gmail.com', usuario.email
	text_content = 'Has Solicitado un cambio en tu contrasena!'
	html_content = '<p>Para realizar el cambio de contrasena sigue el enlace <a href="http://troca.cc:8080'+ s +'"><strong> '+usuario.username +'</strong> </a></p>'
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()	
	return  HttpResponseRedirect('/')


@login_required
def cambiar_contrasena_usuario(response, contrasena, nombre):	
	"""
	Cambia la contraseña de un usuario.
	args:
		response.
		contrasena (str): Nueva contraseña.
		nombre (str): Nombre del usuario que quiere realizar el cambio de contraseña.
	return:
		 HttpResponseRedirect: redirecciona a las configuraciones del usuario.
	"""
	usua=User.objects.get(username=nombre)
	usua.set_password(contrasena)
	usua.save()
# 	u= auth.authenticate(username=usua.username, password=contrasena)
# 	print("CAMBIO CANTRASENAAAAA \n"+str(u)+"\n"+str(usua.username)+"\n"+str(contrasena))
# 	if u is not None and u.is_active:
# 		auth.login(request=self.request, user=u)
# 	return HttpResponseRedirect('/')
	return HttpResponseRedirect('/configuracion/'+usua.username)

	
# us: Nombre del usuario de destino.
# tipoMensaje: Texto para ver en la bandeja de entrada.
# mensaje: Mensaje en html que se va a enviar.
def enviar_correo(us, tipoMensaje, mensaje):
	"""
	Envía un correo a un usuario.
	args:
		us (str): Nombre del usuario de destino.
		tipoMensaje (str): Texto para ver en la bandeja de entrada.
		mensaje (str): Mensaje en html que se va a enviar.
	return:
		 bool: True.
	"""
	usuario= User.objects.get(username=us)
	subject, from_email, to = 'Troca.cc', 'comunlaboratorio@gmail.com', usuario.email
	text_content = tipoMensaje
	html_content = mensaje
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()
	return True



class AboutView(TemplateView):
    template_name = "about.html"
    
class OurPeople(TemplateView):
    template_name = "ourpeople.html"
	
class Create_skill(CreateView):
	""" Vista de la página de formulario para crear una nueva habilidad """
	template_name = 'create_skill.html'
	form_class = SkillForm
	model = Skills

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(Create_skill, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		skill = form.save(commit=False)
		skill.slug = defaultfilters.slugify(skill.title)
		skill.save()
		form.save_m2m()
		return HttpResponseRedirect('/')

class Trueques(PaginationMixin,ListView):
		""" Vista de la página donde se muestran los trueques de un usuario """
		template_name = 'trueques_view.html'
		model = Collaboration
		paginate_by = 3		
			#-------------------------------------------------------------------------------------------------
			#-------------------------------------------------------------------------------------------------
			#-------------------------------------------------------------------------------------------------
		def get_context_data(self, **kwargs):
			context = super(Trueques, self).get_context_data(**kwargs)
			tipo=self.kwargs['tipo']
			context['tipo']=tipo
			_collaborator = User.objects.get(username=self.kwargs['username']) # usuario del perfil.
			#print(_collaborator)
			_UserColab = Collaboration.objects.all().filter(collaborator=_collaborator) # colaboraciones hechas por el usuario.
			rev_collaborations = Collaboration.objects.all().filter(autor=_collaborator) # colaboraciones hechas para el usuario.
			#print ("REV_COLAB"+str(rev_collaborations))
			messages_in = Message.objects.inbox_for(_collaborator)
			messages_out = Message.objects.outbox_for(_collaborator)
			conversationIn = {}
			conversationOut = {}	
			# Diccionario de colaboraciones
			collaborators_profiles = {}			
			colaboraciones_del_usuario={}
			colaboraciones_para_el_usuario={}
			
			# guarda una lista de  colaboraciones en un diccionario con el nombre del usuario con quien interactúa como llave.
			for col in _UserColab:
				if  (tipo == "hechas" and col.isActive == 0) or (tipo == "pasadas" and col.isActive != 0) :
					#_profile= UserProfile.objects.get(user=col.autor) 
					_profile=col.autor
					if colaboraciones_del_usuario.get(_profile):
						colaboraciones_del_usuario[_profile].append(col)
					else:
						colaboraciones_del_usuario[_profile]=[col]
						conversationIn[_profile.username] = []				
						conversationOut[_profile.username] = []			

					collaborators_profiles[_profile]=UserProfile.objects.get(user=_profile)
				
			for col in rev_collaborations:
				if  (tipo == "nuevas" and col.isActive == 0) or (tipo == "pasadas" and col.isActive != 0) :
					#_profile= UserProfile.objects.get(user=col.collaborator) 
					_profile=col.collaborator
					if colaboraciones_para_el_usuario.get(_profile):
						colaboraciones_para_el_usuario[_profile].append(col)
					else:
						colaboraciones_para_el_usuario[_profile]=[col]
						conversationIn[_profile.username] = []				
						conversationOut[_profile.username] = []			
					collaborators_profiles[_profile]=UserProfile.objects.get(user=_profile)

			
			# guardar las conversaciones que llegan por usuario que las manda
			for y in messages_in:
				us=y.sender.username
				if conversationIn.get(us):
					conversationIn[us].append(y)
				else:
					conversationIn[us] = [y]			
				#print(str(x) + " and " + str(y))
				
			# guardar las conversaciones que se envian por usuario al que se mandan
			for y in messages_out:
				us=y.recipient.username
				if conversationOut.get(us):
					conversationOut[us].append(y)
				else:
					conversationOut[us] = [y]								
				#print(str(x) + " and " + str(y))			
			context['userColabs'] = colaboraciones_del_usuario
			context['revColabs'] = colaboraciones_para_el_usuario
			context['colabsProfiles'] =collaborators_profiles
			print("USERS:\n"+str(collaborators_profiles))
			context['message_in'] = conversationIn
			context['message_out'] = conversationOut		
			
			# marca las colaboraciones como vistas
			col = Collaboration.objects.all().filter(autor=_collaborator).filter(visto=False)
			for co in col:
				co.visto=True
				co.save();
			return context
		#-------------------------------------------------------------------------------------------------
		#-------------------------------------------------------------------------------------------------
		#-------------------------------------------------------------------------------------------------
		
#     def get_context_data(self, **kwargs):
#         context = super(Trueques, self).get_context_data(**kwargs)
#         _collaborator = User.objects.get(username=self.kwargs['username'])
#         _UserColab = Collaboration.objects.all().filter(collaborator=_collaborator)
				
#         messages_in = Message.objects.inbox_for(_collaborator)
#         messages_out = Message.objects.outbox_for(_collaborator)
   
#         rev_collaborations = []
#         conversationIn = {}
#         conversationOut = {}

#         for x in messages_in:
#             rev_collaborations.append(x.sender)
#             rev_collaborations.append(x.recipient)  
#         #for y in messages_out:
#             #rev_collaborations.append(x.sender)
#             #rev_collaborations.append(x.recipient)              
        
#         _result = list(set(rev_collaborations))
#         #print("the resultant pals who have emailes with me are" + str(_result)) #the resultant pals who have emailes with me are
#         index = 0

#         for y in messages_in:
#             conversationIn[y.id] = [y]
#             index += 1
#             #print(str(x) + " and " + str(y))
#         for y in messages_out:
#             conversationOut[y.id] = [y]
#             index += 1
#             #print(str(x) + " and " + str(y))

#         context['userColabs'] = _UserColab
#         context['message_in'] = conversationIn
#         context['message_out'] = conversationOut
	              
#         rev_collaborations = {}
#         collaborators_profiles = {}
#         donation = {}
#         isDonation = False
#         _allColab = Collaboration.objects.all()
#         index = 0
    
#         for c in _allColab: # Recorra todoas las colaboraciones (c) (Collaboration) del usuario loggeado
#             cp = Project.objects.get(pk=c.project.pk) # Obtenga los proyectos (cp) de cada colaboracion (c)
#             _profile = UserProfile.objects.get(user=c.collaborator) #  Obtena el perfil del usuario que hizo la colaboraciond (c) conmigo (_collaborator)
#             #print("usuario loggeado: " + str(_collaborator) + " es igual a? " + str(cp.user))
#             if  cp.user == _collaborator: #  and c.isActive | Si el usuario de ese proyecto (cp) es igual del usuario loggeado (_collaborator) entonces recibi una colaboracion
#                 #print("hay trueque")
#                 collaborators_profiles[c.collaborator] = [_profile] # Guarde el perfil
#                 rev_collaborations[index] = [c] # Guarde la colaboracion (c)
#                 index += 1
                
#         for c in _allColab:
#             cp = Project.objects.get(pk=c.project.pk) # coja ese proyectp (cp)
#             _profile = UserProfile.objects.get(user=cp.user) #  Obtena el perfil del usuario (_profile) de ese proyecto (cp)
#             keysList = list(collaborators_profiles.keys())
#             if _collaborator == c.collaborator and _profile.user not in keysList : # and c.isActive revise si el usuario loggeado (_collaborator) tiene alguna / donacion
#                 #print("hay donacion")
#                 isDonation = True
#                 donation[_profile] = [c]
#                 index += 1            
        
#         context['isDonation'] = isDonation
#         context['donation'] = donation
#         #print("donacion? = " + str(isDonation))
        
#         context['revColabs'] = rev_collaborations
#         context['colabsProfiles'] = collaborators_profiles
        
#         return context
			
		def get_queryset(self):
			qs = super(Trueques, self).get_queryset()

			_collaborator = User.objects.get(username=self.kwargs['username'])

			
			rev_collaborations = []

			for c in qs:
					cp = Project.objects.get(pk=c.project.pk)
					if  cp.user == _collaborator: # and c.isActive
							rev_collaborations.append(c.collaborator)                

			_result = list(set(rev_collaborations))
			#print(str(_result))

			return _result

@login_required    
def Close_trueque(request, collaboration,type_true ):   
	"""
	Acepta o cancela un trueque.
	Si se acepta un trueque se elimina del proyecto la necesidad suplida.
	Se cancelan los trueques relacionados a la necesidad suplida.
	Se envia un correo a los usuarios de las collaboraciones actualizadas (aceptadas o canceladas).
	args:
		request.
		collaboration (Collaboration): Trueque que se va a cerrar.
		type_true (int): Entero que representa si se aceptó el trueque, type_true = 1: se acepta el trueque, type_true != 1: se cancela el trueque.
	return:
		 HttpResponseRedirect: Redirecciona a la página de colaboraciones que ya no están activas (aceptadas o canceladas).
	"""
	#print("TIPO_____________ "+type_true)
	if type_true == "1": # se acepta el trueque
		collaboration = Collaboration.objects.get(id=collaboration)

		autor_project=collaboration.project
		collaborator_project=collaboration.collaboratorProject

		autor_skill_to_collaborator=collaboration.autorSkill
		collaborator_skill_to_autor=collaboration.collaboratorSkill

		autor_project.category.remove(collaborator_skill_to_autor)
		autor_project.category_supp.add(collaborator_skill_to_autor)
		# se evía el correo.		
		mensaje="El usuario <strong>"+str(collaboration.autor)+"</strong> Ha aceptado el trueque que has realizado en el proyecto  <strong>"+str(autor_project)+"</strong> donde has ofrecido tu habilidad de <strong> "+str(collaborator_skill_to_autor)+"</strong>"			
		if collaborator_project:
			collaborator_project.category.remove(autor_skill_to_collaborator)
			collaborator_project.category_supp.add(autor_skill_to_collaborator)
			mensaje=mensaje+"\n a cambio de tu habilidad <strong>"+str(autor_skill_to_collaborator)+"</strong> en su proyecto <strong>"+str(collaborator_project)+"</strong>."
		else:
			mensaje=mensaje+"."
		enviar_correo(collaboration.collaborator,"Se ha aceptado un trueque",mensaje)
		# se marca la colaboración como aceptada
		collaboration.isActive = 1
		collaboration.save()		

		collabs_canceladas=get_trueques(autor_project,collaborator_skill_to_autor,collaboration)
	#	print("CANCELADAS 1 \n" + str(collabs_canceladas) )
	# Se cancelan las colaboraciones que ofrecen la misma habilidad.
		for cc in collabs_canceladas:
			cc.isActive= -1
			cc.save()
			mensaje="El usuario <strong>"+str(cc.autor)+"</strong> ya ha suplido la necesidad de <strong>"+str(cc.collaboratorSkill)+"</strong> para el proyecto <strong>"+str(cc.project)+"</strong>."
			enviar_correo(cc.collaborator,"Se ha declinado un trueque",mensaje)
		if collaborator_project:
			r_collabs_canceladas=get_trueques(collaborator_project,autor_skill_to_collaborator,collaboration)
			print("CANCELADAS 2 \n" + str(r_collabs_canceladas) )
			for rcc in r_collabs_canceladas:
				rcc.isActive= -2
				rcc.save()
				mensaje="El usuario <strong>"+str(rcc.autor)+"</strong> ya ha suplido la necesidad de <strong>"+str(rcc.collaboratorSkill)+"</strong> para el proyecto <strong>"+str(rcc.project)+"</strong>."
				enviar_correo(rcc.collaborator,"Se ha declinado un trueque",mensaje)
			
	#	print(str(collaboration.isActive))	
	else: # la colaboración no fue aceptada
		collaboration = Collaboration.objects.get(id=collaboration)
		collaboration.isActive = -1
		collaboration.save()
		mensaje="El usuario <strong>"+str(collaboration.autor)+"</strong> ha declinado el trueque que has realizado en el proyecto  <strong>"+str(collaboration.project)+"</strong> donde has ofrecido la habilidad de <strong> "+str(collaboration.collaboratorSkill)+"</strong>."
		enviar_correo(collaboration.collaborator,"Se ha declinado un trueque",mensaje)
		
	s = "/colaboraciones/" + collaboration.project.user.username+"/pasadas"
	return HttpResponseRedirect(s)



@login_required  
def get_trueques(project,skill,colla):
	"""
	Retorna las colaboraciones propuestas a un proyecto que se ofrezca una determinada habilidad, y diferente a una colaboracion especifica.
	Se usa para obtener las colaboraciones que se van a rechazar al aceptar un trueque.
	args:
		project (Project): proyecto al que se le buscarán las colaboraciones.
		skill (Skills): habilidad recibida por el proyecto.
		colla (Collaboration): Colaboración para excluir de la lista.
	return:
		 set(Collaboration): conjunto de colaboraciones a cancelar.
	"""
	collaboration = set(Collaboration.objects.all().filter(project=project).filter(collaboratorSkill=skill))
	r_collaboration = set(Collaboration.objects.all().filter(collaboratorProject=project).filter(autorSkill=skill))
	trueques=collaboration|r_collaboration
	if colla in trueques:
		trueques.remove(colla)
	return trueques

@login_required  
def get_trueques_usuario(usua):
	"""
	Retorna las colaboraciones activas relacionadas a un usuario determinado.
	args:
		usua (UserProfile): perfil del usuario del que se quieren encotrar la colaboraciones.
	return:
		 set(Collaboration): colaboraciones a del usuario.
	"""
	collaboration = set(Collaboration.objects.all().filter(isActive=0).filter(collaborator=usua.user)) # hechas
	collaboration.update(Collaboration.objects.all().filter(isActive=0).filter(autor=usua.user)) # recibidas		
	return collaboration
	
class Home(ListView):
	""" Vista de la página de inicio """
	template_name = 'index.html'
	model = Project
	def get_context_data(self, **kwargs):
		context = super(Home, self).get_context_data(**kwargs)
		_selProjects = Project.objects.all().filter(highlighted=True).filter(isActive=True).filter(num_needs__lt=100)
		context['selected'] = _selProjects
		selectedProjectsAuthors = {}
		for x in _selProjects:
			userProfile = UserProfile.objects.get(user=x.user) 
			obj = userProfile.category.all()
			selectedProjectsAuthors[x.title] = [obj]
		context['selectedAuthor'] = selectedProjectsAuthors
		_qs = Project.objects.all().filter(isActive=True).filter(num_needs__lt=100)
		qs = _qs.order_by('-date')[:4]
		skills = {}
		for x in qs:
			userProfile = UserProfile.objects.get(user=x.user) 
			obj = userProfile.category.all()
			skills[x.title] = [obj]
		context['skillsP'] = skills
		return context

	def get_queryset(self):
		qs = super(Home, self).get_queryset()
		return qs.order_by('-date')[:4]

class Users_view(PaginationMixin,ListView):
	template_name = 'users_view.html'
	model = UserProfile
	paginate_by = 8

	def get_context_data(self, **kwargs):
		context = super(Users_view, self).get_context_data(**kwargs)
		return context

	def get_queryset(self):
		qs = super(Users_view, self).get_queryset()
		return qs.order_by('-date')

class RecomendedProjects_view(PaginationMixin,ListView):
	""" Vista de la página donde se muestran los proyectos filtrados por : trocables, donables y caducables """
	template_name = 'recomendedProject_view.html'
	model = Project
	paginate_by = 8

	def get_context_data(self, **kwargs):
		context = super(RecomendedProjects_view, self).get_context_data(**kwargs)
		context['tipo']=self.kwargs['tipo']
		# guarda la cantidad de proyectos en cada categoría de habilidades
		_cat = {}
		cat = Skills_categories.objects.all()
		for x in cat:
			_subCat = Skills.objects.all().filter(category = x)
			count = set([])
			for y in _subCat:
				count.update( Project.objects.all().filter(isActive=True).filter(category = y))	
			_cat[x] = [len(count)]
		context['categories'] = _cat
# 		print(str(_cat))
		if self.request.user.is_authenticated():
			user = self.request.user
			try: 
				userProfile = UserProfile.objects.get(user=user)
				context['loggedUser'] = userProfile
				context['hasProfile'] = True
			except UserProfile.DoesNotExist:
				context['hasProfile'] = False
		return context  
	
	def get_queryset(self):			
		tipo=self.kwargs['tipo']
		# filtra los proyectos segun el tipo que se quiera buscar
		if self.request.user.is_authenticated():
			user = self.request.user
			userProfile = UserProfile.objects.get(user=user)
# 			tipo=self.kwargs['tipo']
			if tipo == "caducados":		
				return getProjectsByFilter(userProfile,-1)
			elif tipo == "donacion":
				return getProjectsByFilter(userProfile,1)
			elif tipo == "trueque":
				return getProjectsByFilter(userProfile,2)
			elif tipo == "mios":
				return Project.objects.all().filter(isActive=True).filter(user=userProfile.user)
			else:
				return getProjectsByFilter(userProfile,0)
		else:
			if tipo == "caducados":		
				return Project.objects.all().filter(isActive=True).filter(num_needs__gte = 100)
			else:
				return Project.objects.all().filter(isActive=True).filter(num_needs__lt = 100)
			
class Category_view(PaginationMixin,ListView):
	""" Vista de la página donde se muetran todos los poryectos """
	template_name = 'category_view.html'
	model = Project
	paginate_by = 8

	def get_context_data(self, **kwargs):
		context = super(Category_view, self).get_context_data(**kwargs)

		_cat = {}
		cat = Skills_categories.objects.all()        
		for x in cat:
			_subCat = Skills.objects.all().filter(category = x)
			count = set([])
			for y in _subCat:
				count.update(Project.objects.all().filter(isActive=True).filter(category = y))
			_cat[x] = [len(count)]

		context['categories'] = _cat

		print(str(_cat))

		qs = Project.objects.all().filter(isActive=True).filter(num_needs__lt=100)
		skills = {}
		for x in qs:
			userProfile = UserProfile.objects.get(user=x.user) 
			obj = userProfile.category.all()
			skills[x.title] = [obj]

		context['skills'] = skills

		if self.request.user.is_authenticated():
			user = self.request.user

			try: 
				userProfile = UserProfile.objects.get(user=user)
				context['matchProjects'] = get_proyects_user_gives(userProfile,user)
				context['loggedUser'] = userProfile
				context['hasProfile'] = True
			except UserProfile.DoesNotExist:
				context['hasProfile'] = False

		return context  
	def get_queryset(self):
		qs = super(Category_view, self).get_queryset()
		return qs.order_by('-date')

class Category_view_filter(PaginationMixin, ListView):
	""" Vista de la página donde se muetran los poryectos filtrados por categorías """
	template_name = 'sub_category_view.html'
	model = Project
	paginate_by = 8

	def get_context_data(self, **kwargs):
		context = super(Category_view_filter, self).get_context_data(**kwargs)
		cat = Skills_categories.objects.all().get(slug=self.kwargs['category'])

		_cat = {}
		_subCat = Skills.objects.all().filter(category=cat)
		count = 0
		for x in _subCat:
			count = Project.objects.all().filter(isActive=True).filter(num_needs__lt=100).filter(category = x).count()
			_cat[x] = [count]

		context['sub_categories'] = _cat
		context['main_category'] = cat

		if self.request.user.is_authenticated():
			user = self.request.user
			try: 
				userProfile = UserProfile.objects.get(user=user)
				context['loggedUser'] = userProfile
				context['hasProfile'] = True
			except UserProfile.DoesNotExist:
				context['hasProfile'] = False

		return context

	def get_queryset(self):
		qs = super(Category_view_filter, self).get_queryset()
		cat = Skills_categories.objects.all().filter(slug=self.kwargs['category'])
		sub_cat = Skills.objects.all().filter(category=cat)
		return qs.filter(category=sub_cat).distinct()

class Sub_category_view_filter(PaginationMixin, ListView):
	""" Vista de la página donde se muetran los poryectos filtrados por Hailidades """
	template_name = 'foundation/detail_sub_category.html'
	model = Project
	paginate_by = 9

	def get_context_data(self, **kwargs):
		context = super(Sub_category_view_filter, self).get_context_data(**kwargs)
		cat = Skills_categories.objects.all().get(slug=self.kwargs['category'])
		_cat = Skills.objects.all().get(slug=self.kwargs['subcategory'])
		context['main_category'] = cat
		context['subcategory'] = _cat

		if self.request.user.is_authenticated():
			user = self.request.user
			try: 
				userProfile = UserProfile.objects.get(user=user)
				context['loggedUser'] = userProfile
				context['hasProfile'] = True
			except UserProfile.DoesNotExist:
				context['hasProfile'] = False

		return context

	def get_queryset(self):
			qs = super(Sub_category_view_filter, self).get_queryset()
			cat = Skills.objects.all().filter(slug=self.kwargs['subcategory'])
			return qs.filter(category=cat)


			
			
class Project_view(DetailView):
	""" Vista de la página donde se muestra la información de un proyecto """
	template_name = 'project.html'
	model = Project
	slug_field = 'slug'	
		#---------------------------------------------------------------------------------------------------------------------------
		#--------------------------------------------------------------------------------------------------------------------------
		#---------------------------------------------------------------------------------------------------------------------------
		
	def get_context_data(self, **kwargs):
		context = super(Project_view, self).get_context_data(**kwargs)
		author = User.objects.get(username=self.kwargs['username'])
		user_profile = UserProfile.objects.get(user=author.id) # -----> Author
		project = Project.objects.get(slug=self.kwargs['slug'])
		colabs = Collaboration.objects.all().filter(collaboratorProject=project) # guarde todas las colaboraciones de ese proyecto
		rev_colabs = Collaboration.objects.all().filter(project=project) # guarde todas las colaboraciones de ese proyecto
		context['author'] = user_profile
		context['author_user'] = author
		contType = ContentType.objects.get(app_label='troca', model='project').id
		context['contType'] = contType
		supp_needs = set(project.category_supp.all())	# Necesidades Satisfechas
		needs = set(project.category.all())			# Necesidades del proyecto
		context['colaborations'] = supp_needs # Guarda las necesidades que ya han sido satisfechas
		context['collaborators'] = colabs
		context['rev_collaborators'] = rev_colabs
		#print("COLABSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS\n"+str(colabs))
		mensaje_error="Puedes ayudar en el proyecto" # mensaje por defecto cuando no hay colaboraciones
			
		print("------------>" + str(colabs))
		#----------- Get colaborators profiles-------->
		userColab = set()	# Colaboradores del proyecto
		for x in colabs:
			userColab.add(UserProfile.objects.get(user=x.autor))
		for x in rev_colabs:
			userColab.add(UserProfile.objects.get(user=x.collaborator))
		print("----->---->--->" + str(userColab))
		context['collaboratorsProfile'] = userColab # Guarda los usuarios de esas colaboracione y su foto
		
		if self.request.user.is_authenticated():
			user = self.request.user
			try: 
				userProfile = UserProfile.objects.get(user=user)				# -----> User
				context['hasProfile'] = True
				userProjects = Project.objects.all().filter(user=user).filter(isActive=True)	# Proyectos del usuario
				author_skills = user_profile.category.all()							# Habilidades del usuario
				context['loggedUser'] = userProfile
				context['loggedUserProjects'] = userProjects
				#context['auskills'] = author_skills
				userGives = {}
				userRecives = {}
				context['isReverseMatch'] = False
				context['isMatch'] = False
				
				if userProfile.id != user_profile.id:
	#----------------------> Que puede aportar el usuario al proyecto? <----------------
					user_skills=set(userProfile.category.all())		# Habilidades del usuario
					match = needs & user_skills										# guarde los match aca (category) (interseccion entre habilidades del usuario y necesidades del proyecto)   
					#print ("El proyecto tiene estas necesidades: " + str(needs))
					#print ("El Usuario tiene estas habilidades: " + str(user_skills))
					#print ("hay match con estas habilidades: " + str(match))

					if len(match):
						index=0
						context['isMatch'] = True # Hay una posibilidad de intercambio
						for r in match:
							index += 1
							s = "Alternativa " + str(index)
							userGives[s] = [r.title ,r.slug]
							#print ("asdsadasdasda \n"+str(userGives))
					else:
						supp_match = supp_needs & user_skills
						if len(supp_match):
							mensaje_error="El proyecto ya ha recibido ayuda en: \n"
							indice=0
							for sm in supp_match:
								if indice>0:
									mensaje_error+=", "
								mensaje_error+=sm.title
								indice+=1;
						else:
							mensaje_error="No hay opciones de colaboracion"
							
	#----------------------> Que puede aportar el autor del proyecto al usuario logged? <----------------
					rev_colabs = [] # guarde las colaboraciones        
					# Se recorren los proyectos del usuario y se buscas las habilidades que necesita 
					needs_userProjects=set([]) # crea un set vacio para las necesidades del usuario
					for y in userProjects.all():
						needs_userProjects.update(y.category.all()) # agrega las necesidades nuevas al set
					autor_skills = set(user_profile.category.all()) # set de habilidades del autor del proyecto
					# Intersecta las habilidades que requiere el proyecto con las habilidades que puede ofrecer el autor del proyeto 
					rev_match = needs_userProjects & autor_skills # guarde los match aca (category) (interseccion entre habilidades del autor y necesidades de los proyectos del usuario)   
					#print ("El usuario tiene estas necesidades: " + str(needs_userProjects))
					#print ("El autor del proyecto tiene estas habilidades: " + str(autor_skills))
					#print ("hay match con estas habilidades: " + str(rev_match))
					if len(rev_match): # Si el match entre lo que requiere el usuario y ofrece el autor no es vacio
						context['isReverseMatch'] = True # Hay una posibilidad de intercambio	
						contadorProyectos={} # crea un contador para las hailidades de cada proyecto
						for pr in userProjects.all().filter():
							contadorProyectos[pr.title]=0 # inicia el contador en 0
							for r in rev_match:		
								if r in pr.category.all(): # si la habilidad se encuentra en las necesidades del proyecto
									contadorProyectos[pr.title]+=1 # aumente el contador
									n=contadorProyectos[pr.title]
									s = pr.title+" "+str(n) # etiqueta para guardar la habilidad (nombrbre del proyecto y contador)
									#s = "Alternativa "+str(n)
									userRecives[s] =[r.title ,r.slug,pr.title]  # guarda la habildad con la etiqueta 
					else:
						if context['isMatch']:
							mensaje_error="Puedes donar" 
				else:
					mensaje_error="El Usuario eres tu" 
				#userRecives=sorted(userRecives, key=
				#print("Log puede dar: " + str(userGives) + "\n y puede recivir: " + str(userRecives))
				context['userRecives'] = userRecives
				context['userGives'] = userGives
				context['mensajeError']=mensaje_error
				print ("ERRORRRRRRRRR \n"+mensaje_error)
			except UserProfile.DoesNotExist:
				context['hasProfile'] = False
		return context

		
		#---------------------------------------------------------------------------------------------------------------------------
		#---------------------------------------------------------------------------------------------------------------------------
		#---------------------------------------------------------------------------------------------------------------------------
			
# 	def get_context_data(self, **kwargs):
# 			context = super(Project_view, self).get_context_data(**kwargs)

# 			author = User.objects.get(username=self.kwargs['username'])
# 			user_profile = UserProfile.objects.get(user=author.id) 
# 			project = Project.objects.get(slug=self.kwargs['slug'])

# 			colabs = Collaboration.objects.all().filter(project=project) # guarde todas las colaboraciones de ese proyecto

# 			context['author'] = user_profile
# 			context['author_user'] = author

# 			contType = ContentType.objects.get(app_label='troca', model='project').id
# 			context['contType'] = contType

# 			userColab = {}
# 			supp_needs = []
# 			needs = []

# 			for x in project.category.all():
# 					needs.append(x)    

# 			for x in colabs:
# 					userColab_user = User.objects.get(username=x.collaborator)
# 					userColab_profile = UserProfile.objects.get(user=userColab_user)
# 					userColab[userColab_profile] = x
# 					if x.collaboratorSkill in needs and x.isActive:
# 							supp_needs.append(x.collaboratorSkill)

# 			#print("tutut " + str(supp_needs))

# 			context['colaborations'] = supp_needs # Guarda las necesidades que ya han sido satisfechas
# 			context['collaborators'] = userColab # Guarda los usuarios de esas colaboracione y su foto

# 			#print(str(userColab))

# 			if self.request.user.is_authenticated():
# 					user = self.request.user

# 					try: 
# 							userProfile = UserProfile.objects.get(user=user) 
# 							context['hasProfile'] = True

# 							userProjects = Project.objects.all().filter(user=user)  
# 							author_skills = user_profile.category.all()            

# 							context['loggedUser'] = userProfile
# 							context['loggedUserProjects'] = userProjects
# 							#context['auskills'] = author_skills

# 							userGives = {}
# 							userRecives = {}

# 							context['isReverseMatch'] = False
# 							context['isMatch'] = False
# 							match = [] # guarde los match aca (category)        

# 							index = 1

# 							#----------------------> Que puede aportar el usuario logged al proyecto? <----------------

# 							for x in userProfile.category.all(): # Rocorro las habilidades del usuario logeado (x) (category)
# 									for y in project.category.all(): # Recorro las necesidades del proyecto (y) (category)    
# 											if x.slug == y.slug: # SI la habilidad (x) y la nececidad (y) coinciden                        
# 													match.append(x) # con cuales habilidades? guardelas en una lista (x) (category)

# 							print ("hay match con estas habilidades: " + str(match))


# 							if colabs.exists(): # Si existen colaboraciones

# 									print ("existen estas colaboraciones: " + str(colabs))

# 									for i in colabs: # Recorro los  match
# 											for r in match: # Recorro las colaboraciones / coincidencias
# 													#print(str(i.collaboratorSkill.slug) + " / " + str(r.slug))
# 													if  i.collaborator.id != user.id and not i.isActive: #  r.slug == i.collaboratorSkill.slug and and i.isActive Si el usuario de la colaboracion es difetente al usuario logged |||| i.project == project and 
# 															# Y la habilidad de esa colaboracion (i) es diferente a las habilidades (match) del usuario (x)  Past--> |||||if i.collaboratorSkill.slug != r.slug and i.project == project and i.isActive:||
# 															print("usuario loggeadp:" + str(user.id) + " contra " + str(i.collaborator.id)) 
# 															context['isMatch'] = True # Hay una posibilidad de intercambio
# 															s = "Alternativa " + str(index)
# 															userGives[s] = [r.slug]       
# 															index += 1 

# 													else:
# 															context['isMatch'] = False

# 							else: # No existen colaboraciones ---> entonces muestreme todas los (match) coincidencias
# 									for r in match:
# 											context['isMatch'] = True # Hay una posibilidad de intercambio
# 											s = "Alternativa " + str(index)
# 											userGives[s] = [r.slug]
# 											index += 1


# 							#----------------------> Que puede aportar el autor del proyecto al usuario logged? <----------------

# 							rev_match = [] # guarde los match aca (category)
# 							rev_colabs = [] # guarde las colaboraciones        

# 							for x in user_profile.category.all(): # Recorro las habilidaes del autor del proyecto (x)
# 									for y in userProjects.all(): # Recorro los proyectos del usuario loggeado (y)    
# 											for yy in y.category.all():    # Colecto las necesidades de todos los proyectos del usuario loggeado (yy)    
# 													if x.slug == yy.slug: # coinciden?
# 															context['isReverseMatch'] = True # You can give and recive
# 															rev_match.append(x)
# 															colabs = Collaboration.objects.all().filter(project=y)

# 															if colabs.exists():

# 																	for i in colabs:
# 																			if i.collaboratorSkill.slug != x.slug and i.isActive:
# 																					_reciverProject = y
# 																					userRecives[_reciverProject.title] = [yy.slug]

# 																			elif i.isActive == False:
# 																					_reciverProject = y
# 																					userRecives[_reciverProject.title] = [yy.slug]
# 															else:
# 																	_reciverProject = y
# 																	userRecives[_reciverProject.title] = [yy.slug]

# 									#print("Log puede dar: " + str(userGives) + " y puede recivir: " + str(userRecives))

# 							context['userRecives'] = userRecives
# 							context['userGives'] = userGives

# 					except UserProfile.DoesNotExist:
# 							context['hasProfile'] = False



# 			return context

# filt ->  -1:cerrado  |  0:todos  |  1:donaciones  |  2:trueques
def getProjectsByFilter(usu, filt):
	"""
	Busca una lista de proyectos según un filtro dado.
	args:
		usu (UserProfile): perfil de usuario.
		filt (int): valor del filtro. filt=-1: proyectos cerrados. filt=0:todos los proyectos. filt=1:donaciones. filt=2:trueques.
	return:
		 [Project]: Lista de proyectos encontrados.
	"""
	if(filt>0):
		estado=0;
		useSkills=set({})  
		useSkills.update(usu.category.all())	
		proyectos= Project.objects.all().filter(isActive=True)
		userProjects = proyectos.filter(user=usu.user)	# Proyectos del usuario
		proyectos=proyectos.filter(num_needs__lt = 100)
		needs_userProjects=set([]) # crea un set vacio para las necesidades del usuario  
		for y in userProjects.all():
			needs_userProjects.update(y.category.all()) # agrega las necesidades nuevas al set
		donaciones=[]
		trueques=[]

		for p in proyectos:
			tipo=getDonacionOTrueque(usu,p,useSkills,needs_userProjects)
			if tipo == 1:
				donaciones.append(p)
			elif tipo == 2:
				trueques.append(p)
		if filt == 1:
			return donaciones
		elif filt == 2:
			return trueques		
	elif filt == 0:
		return Project.objects.all().filter(isActive=True)
	elif filt < 0:
		return Project.objects.all().filter(isActive=True).filter(num_needs__gte = 100)
	return set({})

# 0:no puede nada | 1:puede donar | 2:puede trocar
def getDonacionOTrueque(usu, project, userSkills, user_nedds):
	"""
	Busca la relación entre un usuario y un proyecto dependiendo de las habilidades y necesidades de ambos.
	args:
		usu (UserProfile): perfil de usuario.
		project (Project): proyecto a comparar.
		userSkills (set(Skills)): conjunto con las habilidades del usuario.
		user_nedds (set(Skills)): conjunto con las necesidades del usuario.
	return:
		 int: 0 si no se puede donar ni trocar, 1 si se puede donar, 2 si se puede trocar.
	"""
	cat_proj=set({})
	estado=0
	if usu and project.user != usu.user:
		cat=set(project.category.all()) & userSkills
		if len( cat)>0:
			estado=1;      
			autor_profile = UserProfile.objects.get(user=project.user)
			autor_skills = set(autor_profile.category.all()) # set de habilidades del autor del proyecto
			cat_rev=autor_skills&user_nedds
			if len( cat_rev)>0:
				estado=2      
	return estado



@login_required
def register_collaborator(request, username, slug):
	"""
	Registra una nueva colaboración a un proyecto.
	args:
		request.
		username (str): Nombre del usuario.
		slug (str): Slug del proyecto.
	return:
		 HttpResponseRedirect: Redirecciona a las colaboraciones propuestas por el usuario.
	"""
	slug=slug.split(" ")[0]
	project_base = Project.objects.get(slug=slug)
	loggedUser = User.objects.get(username=username) 	
	skill_given_loggedUser = Skills.objects.get(slug=request.POST['gives'])
	project_author = User.objects.get(username=project_base.user)
	
	# ---- Register collaborator in base project
	# ----- Calculate % of complatness of the project
	#numNeeds = project_base.category.count()    
	#project_base.num_needs = (project_base.num_needs)+(100/numNeeds)
	#project_base.save()
	# ---- Register collaborator in logged user project
	req = request.POST.get('receives', False)
	#print("REQQQQQQQQQQQQQQQ\n"+str(req))
	if req:
		a, b = req.split("/")
		#a=a.split(" ")[0]
		project_loggedUser = Project.objects.get(title=a)
		skill_recived_loggedUser = Skills.objects.get(slug=b)
		col=Collaboration.objects.all().filter(project=project_base).filter(collaborator=loggedUser).filter(collaboratorSkill=skill_given_loggedUser).filter(collaboratorProject=project_loggedUser).filter(autor=project_author).filter(autorSkill=skill_recived_loggedUser)
		if(not col):
			_new_collab = Collaboration(project=project_base, collaborator=loggedUser, collaboratorSkill=skill_given_loggedUser,collaboratorProject=project_loggedUser, autor=project_author, autorSkill=skill_recived_loggedUser, isActive = False);
			_new_collab.save()
	else: 		
		col=Collaboration.objects.all().filter(project=project_base).filter( collaborator=loggedUser).filter(collaboratorSkill=skill_given_loggedUser).filter(autor=project_author)
		if(not col):
			new_collab = Collaboration(project=project_base, collaborator=loggedUser, collaboratorSkill=skill_given_loggedUser, autor=project_author ,isActive = False);
			new_collab.save()
		
			# ----- Calculate % of complatness of the project
			#_numNeeds = project_loggedUser.category.count()    
			#project_loggedUser.num_needs = (project_loggedUser.num_needs)+(100/_numNeeds)
			#project_loggedUser.save()
			#print("Usuario " + username + " Quiere colaborar en " + slug + " prestando el servicio de " + request.POST['gives'] + " y recibiendo " + b + " in the project " + a)

	# send notification email to user	
	s = "/colaboraciones/" + loggedUser.username+"/hechas"    
	subject, from_email, to = 'Troca.cc', 'comunlaboratorio@gmail.com', project_author.email
	text_content = 'Has recibido una nueva colaboracion!'
	html_content = '<p>El usuario <strong>' + str(loggedUser) + '</strong> quiere colaborar en tu proyecto <a href="http://troca.cc'+ s +'">' + '<strong>' + str(project_base.title) + '</strong>' + '</a></p>'
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()
	return HttpResponseRedirect(s)

def getRespuesta(com):
	"""
	HTML de la respuesta a un comentario.
	No se usa.
	args:		
		com (Comment): Comentario.
	return:
		 str: HTML del comentario.
	"""
	res= '<div class="respuesta">';
	res +='<div class="fotoComentario" style="display: inline-block; width:30px;">';
	res +='<a href="/perfil/'+str(com.userComment.id)+'">';
	res +='<div class="img-container-user circular" style="background-image: url(\''+str(com.userProfileComment.avatar_url.url_700x700 )+'\');  width:30px;  height:30px;">';
	res +='</div>';
	res +='</a>';
	res +='</div>';
	res +='<div class="infoComentario" style="display: inline-block;">';
	res +='<h5 class="mb0"><a href="/perfil/'+str(com.userComment.id)+'">'+str(com.userComment.username)+'</a> </h5> ';
	res +='<p class="mb0 comentario">';
	res +='"'+(com.comment)+'"';
	res +='</p>';
	res +='</div>';
	res +='</div>';
	return res;	
	
@login_required
def register_comment(request, usernameComment, projectSlug,comment):
	"""
	Registra un nuevo comentario.
	envía un correo al autor del proyecto.
	args:
		request.
		usernameComment (str): Nombre del usuario.
		projectSlug (str): Slug del proyecto.
		comment (str): comentario.
	return:
		 HttpResponseRedirect: Redirecciona a los comentarios del proyecto.
	"""
	userNC = User.objects.get(username=usernameComment);
	userProfileNC = UserProfile.objects.get(user=userNC);
	commenta=request.GET["mensaje"];
	mensaje="";
	s="/";
	retorno="";
	if comment=="respuesta":
		print("SIIIIII");
		com=Comment.objects.get(pk=projectSlug);
		new_respond = Respond(userRespond = userNC,	userProfileRespond=userProfileNC,	userComment = com.userComment, commentID = com.pk,	respond = commenta);
		new_respond.save();
		com.responds.add(new_respond);
		com.save();
		mensaje="El usuario <a href='/perfil/"+str(userNC.id)+"'><b>"+str(userNC.username)+"</b></a> ha respondido a un comentario tuyo hecho en el proyecto "+str(com.project.title)+".<br>";
		mensaje+="\""+commenta+"\"."	
		print("SIIIIII111111");
		enviar_correo(com.userComment.username, "Has recibido un comentario de "+str(userNC.username), mensaje)	
		s="/comentario/"+projectSlug;
# 		retorno=  getRespuesta(com);
		print("SIIIIII22222222222");
	else:
		print("NOOOOO");
		project_base = Project.objects.get(slug=projectSlug);
		userProject=project_base.user;
		new_comment=Comment(	userComment = userNC,	userProfileComment=userProfileNC,	userProject = userProject,	project = project_base,	comment = commenta	);
		new_comment.save();
		mensaje="El usuario <a href='/perfil/"+str(userNC.id)+"'><b>"+str(userNC.username)+"</b></a> Ha hecho un comentario en tu proyecto "+str(project_base.title)+".<br>";
		
		mensaje+="\""+commenta+"\"."	
		enviar_correo(userProject.username, "Has recibido un comentario de "+str(userNC.username), mensaje)	
		s="/comentarios/"+project_base.slug;
# 		retorno = HttpResponseRedirect(s);
		
	
	return  HttpResponseRedirect(s);

def get_project_comments(project):
	"""
	Busca los comentarios de un proyecto.
	args:
		project (Project): proyecto del que se quieren obtener los comentarios.
	return:
		 [Comment]: comentarios del proyecto.
	"""
# 	project_base = Project.objects.get(slug=projectSlug);
	comentarios=Comment.objects.all().filter(isActive=True).filter(project=project).order_by('-created');	
	return comentarios;

class ProjectComments(DetailView):
	""" Vista para los comentarios de un proyecto """
	template_name = 'comentario_vista.html'
	model = Project
	slug_field = 'slug'	
	
	def get_context_data(self, **kwargs):
		context = super(ProjectComments, self).get_context_data(**kwargs)		
		project = Project.objects.get(slug=self.kwargs['slug'])
		comments=get_project_comments(project);		
		context["comments"]=comments;
		context["mostrarProyecto"]=False;
		contTypeComment = ContentType.objects.get(app_label='troca', model='comment').id;
		context['contTypeComment']=contTypeComment;
# 		responses={};
# 		for c in comments:
# 			responses[c.pk]= c.responds.all();
# 			print("COMENTARIOOOOOOO\n"+str(responses));
# 		context['responds']=responses;
		
		return context

class ProjectComment(DetailView):
	""" Vista para las respuestas de un comentario """
	template_name = 'comentario_responds.html'
	model = Comment
	
	def get_context_data(self, **kwargs):
		context = super(ProjectComment, self).get_context_data(**kwargs)		
		comment=Comment.objects.get(pk=self.kwargs['pk']);
		context["comment"]=comment;
		context["mostrarProyecto"]=False;
		contTypeComment = ContentType.objects.get(app_label='troca', model='comment').id;
		context['contTypeComment']=contTypeComment;
		return context

	
class UserComments(DetailView):
	""" Vista de la página de comentarios de un usuario """
	template_name = 'comentarios_user_view.html'
	model = User
	slug_field='username'
# 	Trueques(  User.objects.get(a
	def get_context_data(self, **kwargs):			
		context = super(UserComments, self).get_context_data(**kwargs)		
		_user = User.objects.get(username=self.kwargs['slug'])
		context['user']=_user;
		allComm=Comment.objects.all().filter(isActive=True);
		
		com=allComm.filter(userProject=_user).order_by('-created').exclude(userComment=_user);
		context["commentsR"]=com;
		
		com=allComm.filter(userComment=_user).order_by('-created');
		context["commentsH"]=com;
		
		context["mostrarProyecto"]=True;
		com = allComm.filter(userProject=_user).filter(visto=False)
		
		for co in com:
			co.visto=True;
			co.save();
			
		contTypeComment = ContentType.objects.get(app_label='troca', model='comment').id;
		context['contTypeComment']=contTypeComment;			
		return context

	


# class UserProjects(PaginationMixin,ListView):
# 	template_name = 'dashboard.html'
# 	model = Project
# 	slug_field = 'username'
# 	paginate_by = 8

# 	def get_context_data(self, **kwargs):
# 		context = super(UserProjects, self).get_context_data(**kwargs)
# 		_user = User.objects.get(username=self.kwargs['username'])
# 		context['user'] = Project.objects.all().filter(user=_user)
		
# 		context['hasProjects'] = user_projects.exists()
# 		context['projects'] = user_projects
# 		return context



class Profile(PaginationMixin, DetailView):
	""" Vista del perfil del usuario """
	template_name = 'user_profile.html'
	model = UserProfile
	slug_field = 'user'
	paginate_by = 8

	def get_context_data(self, **kwargs):
		context = super(Profile, self).get_context_data(**kwargs)
		_user = User.objects.get(id=self.kwargs['slug'])
		user_projects = Project.objects.all().filter(user=_user)
		context['hasProjects'] = user_projects.exists()
		context['projects'] = user_projects
		context['isProfile'] = True
		contType = ContentType.objects.get(app_label='troca', model='userprofile').id
		context['contType'] = contType

		return context

	def get_queryset(self):
		qs = super(Profile, self).get_queryset()
		return qs.order_by('-date')

	def get(self, request, *args, **kwargs):
		try:
			self.object = self.get_object()
		except Http404:
			# redirect here
			return redirect('/register/perfil/')
		context = self.get_context_data(object=self.object)
		return self.render_to_response(context)
	
# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
	"""
	Cierra la sesión activa.
	args:
		request.
	return:
		 HttpResponseRedirect: Redirecciona al iicio.
	"""
	# Since we know the user is logged in, we can now just log them out.
	logout(request)
	# Take the user back to the homepage.
	return HttpResponseRedirect('/')

class Create_profile(CreateView):
	""" Vista de la página donde se ingresan los detalles del perfil de usuario """
	template_name = 'create_profile.html'
	form_class = UserProfileForm
	model = UserProfile

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(Create_profile, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		user_profile = form.save(commit=False)
		user_profile.user = self.request.user
		user_profile.save()
		form.save_m2m()
# 		return HttpResponseRedirect('/')
		return HttpResponseRedirect('/dashboard/'+ str(user_profile.user.id))

class Settings(UpdateView):
	""" Vista de la página donde se editan los detalles del perfil de usuario """
	template_name = 'settings.html'
	form_class = UserProfileForm
	model = UserProfile
	state = False

	def get_state(self):
		return state

	def get_object(self, queryset=None):
		user = User.objects.get(username=self.kwargs['username'])
		obj = UserProfile.objects.get(user=user.id)
		return obj

	def form_valid(self, form):
		userProfile = form.save()
		s = "/dashboard/"
# 		s = "/perfil/"
		s = s + str(userProfile.user.id);
		return HttpResponseRedirect(s)

class Edit_project(UpdateView):
	""" Vista de la página donde se editan los detalles de un proyecto """
	template_name = 'edit_project.html'
	form_class = ProjectForm
	model = Project
	
	def get_context_data(self, **kwargs):
		context = super(Edit_project, self).get_context_data(**kwargs)
		context['slug']=self.kwargs['slug'];
		return context

	def form_valid(self, form):
		project = form.save()
		project.slug = defaultfilters.slugify(project.title)
		project.save()
		s = "/proyecto/"
		s = s + project.user.username + "/" + project.slug;
		return HttpResponseRedirect(s)

class Create_project(CreateView):
	""" Vista de la página donde se ingresan los detalles de un proyecto """
	template_name = 'create.html'
	form_class = ProjectForm
	model = Project

	def form_valid(self, form):
		project = form.save(commit=False)
		project.user = self.request.user
		project.slug = defaultfilters.slugify(project.title)
		project.save()
		form.save_m2m()
		s = "/proyecto/"
		s = s + project.user.username + "/" + project.slug;
		return HttpResponseRedirect(s)

@receiver(user_activated)
def login_on_activation(sender, user, request, **kwargs):
	"""Logs in the user after activation"""
	user.backend = 'django.contrib.auth.backends.ModelBackend'
	login(request, user)
	#auth_login(request, user) 
	# Registers the function with the django-registration user_activated signal
	user_activated.connect(login_on_activation) 
    

class Register(CreateView):
	""" Vista de la página de formulario donde se registra un nuevo usuario """
	template_name = 'register.html'
	form_class = UserForm
	model = User

	def form_valid(self, form):
		user = form.save(commit=False)
		user.username = user.username.lower()
		user.set_password(user.password)
		user.save()
		user_activated.send(sender=self, user=user, request=self.request)
		p=form.data["password"]
		u= auth.authenticate(username=user.username, password=p)
		if u is not None and u.is_active:
			auth.login(request=self.request, user=u)
		return HttpResponseRedirect('/register/perfil/')
		

@login_required
def cerrar_usuario(request, username):
	"""
	Desactiva el perfil de un usuario.
	args:
		request.
		username (str): Nombre del usuario.
	return:
		 HttpResponseRedirect: redirecciona al inicio.
	"""
	usu = User.objects.get(username=username)
	usu.is_active=False	
	usu.save()
	logout(request)
	return HttpResponseRedirect('/')

@login_required
def cerrar_proyecto(request, username,slug):
	"""
	Desactiva un proyecto.
	Envía correo a los usuarios que tenian colaboraciones con el proyecto.
	args:
		request.
		username (str): Nombre del usuario.
		slug (str): Slug del proyecto.
	return:
		 HttpResponseRedirect: redirecciona a los proyectos del usuario.
	"""
# 	usu = User.objects.get(username=username);
	proj=Project.objects.get(slug=slug);
# 	proj.isActive=False
	bol=not proj.isActive;
	proj.isActive=bol;
	proj.save();
	
# 	--------CERRAR LOS TRUEQUES-------
	coll=Collaboration.objects.filter(isActive__gte = 0);
	
	if not bol:
		collabs_canceladas=coll.filter(project=proj);
		for cc in collabs_canceladas:
			cc.isActive= -3
			cc.save()
			mensaje="El usuario <strong>"+str(cc.autor)+"</strong> ha eliminado su proyecto <strong>"+str(cc.project)+"</strong>."
			enviar_correo(cc.collaborator,"Se ha declinado un trueque",mensaje)

		r_collabs_canceladas= coll.filter(collaboratorProject=proj);
		for rcc in r_collabs_canceladas:
			rcc.isActive= -3
			rcc.save()
			mensaje="El usuario <strong>"+str(rcc.collaborator)+"</strong> ha eliminado su proyecto "+str(rcc.collaboratorProject)+"</strong>."
			enviar_correo(rcc.autor,"Se ha declinado un trueque",mensaje)
	
	proys=Comment.objects.filter(project=proj);
	for pr in proys:
		pr.isActive=bol;
		pr.save();	
	return HttpResponseRedirect('/colabora/mios/')
	
class Login(FormView):
	""" Vista de la página de formulario donde se maneja el inicio de sesión """
	template_name = 'login.html'
	form_class = UserLoginForm
	success_url = '/dashboard/'

	redirect_field_name = REDIRECT_FIELD_NAME
	@method_decorator(sensitive_post_parameters('password'))
	@method_decorator(csrf_protect)
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		# Sets a test cookie to make sure the user has cookies enabled
		request.session.set_test_cookie()
		return super(Login, self).dispatch(request, *args, **kwargs)
	def form_valid(self, form):
		auth_login(self.request, form.get_user())
		if self.request.session.test_cookie_worked():
			self.request.session.delete_test_cookie()

		return super(Login, self).form_valid(form)

	def get_success_url(self):
		redirect_to = self.request.REQUEST.get(self.redirect_field_name)
		if not is_safe_url(url=redirect_to, host=self.request.get_host()):
			redirect_to = self.success_url+str(self.request.user.id)
		return redirect_to
# 				return redirect_to
        
class Set_Password(UpdateView):
	""" Vista de la página de formulario deonde se actualiza la contraseña """
	template_name = 'password.html'
	slug_field = 'id'
	form_class = NewPasswordForm
	model= CambioContrasena 
	
	def user_password_update(request,nueva_contrasena,id_cambio_contrasena,self):
		solicitud_cambio=CambioContrasena.objects.all().get(id=id_cambio_contrasena)
		usua=solicitud_cambio.user
		usua.set_password(nueva_contrasena)
		sc=solicitud_cambio.isActive
		solicitud_cambio.isActive=False		
		usua.save()
		solicitud_cambio.save()
		iniciaSesion=False
		u= auth.authenticate(username=usua.username, password=nueva_contrasena)
# 		print("CAMBIO CANTRASENAAAAA \n"+str(u)+"\n"+str(usua.username)+"\n"+str(nueva_contrasena))
		if u is not None and u.is_active:
			auth.login(request=self.request, user=u)
# 			iniciaSesion='/dashboard/'+str(usua.id)
			iniciaSesion='/'
		#return HttpResponseRedirect('/perfil/'+str(usua.id))
		return iniciaSesion
	
	def form_valid(self, form):
		nueva_contrasena= form.data['password']		
		solicitud= CambioContrasena.objects.get(id=self.kwargs['slug'])
		id_cambio_contrasena=solicitud.id
		if solicitud.isActive:			
			dire=self.user_password_update(nueva_contrasena,id_cambio_contrasena,self)
			if(dire):
				return HttpResponseRedirect(dire)
			else:
				return HttpResponseRedirect('/login/')
		else:
			return HttpResponseRedirect('/nueva_contrasena/'+id_cambio_contrasena)

	def get_context_data(self, **kwargs):
		solicitud= CambioContrasena.objects.get(id=self.kwargs['slug'])
		usua= solicitud.user
		context = super(Set_Password, self).get_context_data(**kwargs)
		context['user_P']=usua
		context['solicitud']=solicitud
		return context
	
	

	
class Dashboard(PaginationMixin, DetailView):
	""" Vista de la página Dashboard donde se encuentra las actualizaciones generales pertinentes al usuario """
	template_name = 'dashboard.html'
	model = UserProfile
	slug_field = 'user'
	paginate_by = 8

	def get_context_data(self, **kwargs):
		context = super(Dashboard, self).get_context_data(**kwargs)
		_user = User.objects.get(id=self.kwargs['slug'])
		user_projects = Project.objects.all()
		up=UserProfile.objects.get(user=_user);
		context['collabs'] =    sorted(list(get_trueques_usuario(up)), key=attrgetter('date'), reverse=True) [:5];
		
		com=Comment.objects.all().filter(isActive=True).filter(userProject=_user);
		context['comments'] = sorted( com, key=attrgetter('date'), reverse=True )[:4];
		# 		context['collabs'] =list(get_trueques_usuario(up))[:5];
		# 		print(str(_user)+"----"+str(up.user)+"______cccccccccolllaaabbssss\n"+str(context['collabs']))
		context['hasProjects'] = user_projects.exists()
		context['projects'] = user_projects
		context['isProfile'] = True
		contType = ContentType.objects.get(app_label='troca', model='userprofile').id
		context['contType'] = contType
		contTypeComment = ContentType.objects.get(app_label='troca', model='comment').id;
		context['contTypeComment']=contTypeComment;
		return context
	
	def get_queryset(self):
		qs = super(Dashboard, self).get_queryset()
		return qs.order_by('-date')

	def get(self, request, *args, **kwargs):
		try:
			self.object = self.get_object()
		except Http404:
			# redirect here
			return redirect('/register/perfil/')
		context = self.get_context_data(object=self.object)
		return self.render_to_response(context)
	
	
# DISQUS_SECRET_KEY = 'ENwW3xLVeNgJG9pqdhh0JuGbQN6Ysj43TQz84tiiSO2sHC2rNpLWxXKlM1N71MSd'
# DISQUS_PUBLIC_KEY = 'osaBhgeih4KQOO0g6YjMCqh6ChGOw02ULFKglGAx1bZJOj2eEuJf9ufbqo6GNKWS'


# def get_disqus_sso(user):
# 	# create a JSON packet of our data attributes
# 	data = simplejson.dumps({
# 			'id': user.id,
# 			'username': user.username,
# 			'email': user.email,
# 	})
# 	# encode the data to base64
# 	message = base64.b64encode(data)
# 	# generate a timestamp for signing the message
# 	timestamp = int(time.time())
# 	# generate our hmac signature
# 	sig = hmac.HMAC(DISQUS_SECRET_KEY, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()

# # return a script tag to insert the sso message
# 	return """<script type="text/javascript">
# 		var disqus_config = function() {
# 				this.page.remote_auth_s3 = "%(message)s %(sig)s %(timestamp)s";
# 				this.page.api_key = "%(pub_key)s";
# 		}
# 		</script>""" % dict(message=message,timestamp=timestamp,sig=sig,pub_key=DISQUS_PUBLIC_KEY,)


