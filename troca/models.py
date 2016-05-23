import string
import random

from django.db import models
from django.contrib.auth.models import User
from thumbs import ImageWithThumbsField
from django.template.defaultfilters import slugify
from froala_editor.fields import FroalaField


# Skills models

class Skills_categories(models.Model):
	title = models.CharField(max_length=128)
	slug = models.SlugField(max_length=100, unique=True)
	description = models.TextField(max_length=500)
	
	def __unicode__(self): 
		return self.title

class Skills(models.Model):
	title = models.CharField(max_length=128)
	category = models.ForeignKey(Skills_categories, related_name='skill_category')
	slug = models.SlugField(max_length=100, unique=True)
	description = models.TextField(max_length=500)
	
	def __unicode__(self): 
		return self.title
	
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    category = models.ManyToManyField(Skills)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    about = models.TextField(max_length=400)
    date = models.DateField(auto_now_add=True)
    avatar_url = ImageWithThumbsField(upload_to='media/profile_images/thumb', sizes=((700,700),(60,60)))
    

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username
        

# Project model 

class Project(models.Model):
	user = models.ForeignKey(User)									# Usuario que creo el proyecto
	category = models.ManyToManyField(Skills, related_name='proyect_category')				# Necesidades del proyecto
	category_supp = models.ManyToManyField(Skills, related_name='proyect_category_supp',blank=True)	# Necesidades satisfechas
	title = models.CharField(max_length=128)				# Titulo del proyecto
	date = models.DateField(auto_now_add=True)			# Fecha de creacion del proyecto
	expire_date = models.DateField()								# Fecha de expiracion del proyecto
	summary = FroalaField(options={									# Campo de texto con el resumen
        'inlineMode': False, }, theme='troca')
	content = FroalaField(options={									# Campo de texto con la descripcion del proyecto
        'inlineMode': False, }, theme='troca')
	needs = FroalaField(options={										# Campo de texto con las necesidades
        'inlineMode': False, }, theme='troca')
	thumbnail_url = ImageWithThumbsField(upload_to='media/project_images/thumb', sizes=((700,700),(300,300)))
																									# url del proyecto
	slug = models.SlugField(max_length=100, unique=True)	# texto plano del nombre
	highlighted = models.BooleanField(default=False);			#
	num_needs = models.IntegerField(default=0)			#cantidad de necesidades (100=Completo)
	isActive = models.BooleanField(default=True)
	
	def __unicode__(self): 
		return self.title
		
class Collaboration(models.Model):
	project = models.ForeignKey(Project,related_name='autor_proyect') 
	collaboratorProject = models.ForeignKey(Project,related_name='collaborator_proyect', blank=True, null=True)
	date = models.DateField(auto_now_add=True)
	collaborator = models.ForeignKey(User,related_name='collaborator')
	autor = models.ForeignKey(User,related_name='auto')
	collaboratorSkill = models.ForeignKey(Skills,related_name='skill_collaborator')
	autorSkill = models.ForeignKey(Skills,related_name='skill_autor', blank=True, null=True)
	isActive = models.IntegerField(default=0) # no_aceptado=0 | aceptado=1 | declinado=-1
	visto = models.BooleanField(default=False)
	
	def __unicode__(self):
		return unicode("The user: " + str(self.collaborator) + " collaborates in: " + str(self.project.slug) + " with: " + str(self.collaboratorSkill.slug) + "| " + str(self.isActive))

class CambioContrasena(models.Model):
	user = models.ForeignKey(User) # Usuario que pide cambio de contrasena
	id = models.CharField(max_length=80,primary_key=True) # identificador del pedido para caambiar la contrasena
	isActive = models.BooleanField(default=True)	
	def __unicode__(self):
		return unicode(str(self.user)+" | Passeord reset: "+("Incomplete" if self.isActive else "Complete"))
	
class Respond(models.Model):
	userRespond = models.ForeignKey(User,related_name='user_respond') # Usuario que hace el comentario
	userProfileRespond=models.ForeignKey(UserProfile) # perfil del usuario que hace el comentario
	userComment = models.ForeignKey(User,related_name='autor_comment') # Usuario dueno del proyecto al que se hace el comentario
	commentID = models.IntegerField(default=0) # Comentario al que se responde
	date = models.DateField(auto_now_add=True)
	created = models.DateTimeField(auto_now_add=True)
	respond = models.CharField(max_length=500)
	isActive = models.BooleanField(default=True)
	visto = models.BooleanField(default=False)
	def __unicode__(self):
# 		return unicode("The user: " + str(self.userComment) + " comment in: " + str(self.project.slug) +" by "+ str(self.userProject)+ " on " + str(self.date) + ".\n" + str(self.comment))
		return unicode("The user: " + str(self.userRespond) + " responds's comment "+" by "+ str(self.userComment)+ " on " + str(self.date));

	
class Comment(models.Model):
	userComment = models.ForeignKey(User,related_name='user_comment') # Usuario que hace el comentario
	userProfileComment=models.ForeignKey(UserProfile) # perfil del usuario que hace el comentario
	userProject = models.ForeignKey(User,related_name='user_project') # Usuario dueno del proyecto al que se hace el comentario
	project = models.ForeignKey(Project,related_name='project') # proyecto al que se hace el comentario 
	date = models.DateField(auto_now_add=True)
	created = models.DateTimeField(auto_now_add=True)
	comment = models.CharField(max_length=500)
	isActive = models.BooleanField(default=True)
	visto = models.BooleanField(default=False)
	responds = models.ManyToManyField(Respond)
	def __unicode__(self):
# 		return unicode("The user: " + str(self.userComment) + " comment in: " + str(self.project.slug) +" by "+ str(self.userProject)+ " on " + str(self.date) + ".\n" + str(self.comment))
		return unicode("The user: " + str(self.userComment) +" comment in: " + str(self.project.slug) +" by "+ str(self.userProject)+ " on " + str(self.date));

