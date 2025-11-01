from django.db import models

class Command(models.Model):
	name = models.CharField(max_length=80)
	slug = models.CharField(max_length=80, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name + " - " + self.created_at.strftime("%m/%d/%Y %H:%M:%S")

	class Meta:
		ordering = ['name']
		

class Raspberry(models.Model):
	name = models.CharField(max_length=80)
	slug = models.CharField(max_length=80, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name + " - " + self.created_at.strftime("%m/%d/%Y %H:%M:%S")

	class Meta:
		ordering = ['name']
		
class History(models.Model):
	raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE, to_field='slug', db_column='raspberry_slug')
	command = models.ForeignKey(Command, on_delete=models.CASCADE, to_field='slug', db_column='command_slug')
	status = models.CharField(max_length=30, default='pending')
	result = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.raspberry.slug + " - " + self.created_at.strftime("%m/%d/%Y %H:%M:%S")

	class Meta:
		ordering = ['created_at']