from django.contrib.auth.models import User
from django import template
from troca.models import UserProfile, Project, Skills, Skills_categories
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='get_project_author')
@stringfilter
def get_project_author(value):
	context = User.get_context_data(username=value)
	obj = UserProfile.objects.get(user=user.id)
	return {'author': obj}

@register.simple_tag
def getAllCollabs():
	obj = set(Collaboration.objects.all().filter(autor=us))
	obj = obj | set(Collaboration.objects.all().filter(collaborator=us))
	return obj

@register.simple_tag
def get_user_profile(usu, null):	
	return UserProfile.objects.get(user=user.id)



