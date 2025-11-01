from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User

class CustomUserAdmin(UserAdmin):
    # Campos a mostrar en la lista del admin
    list_display = ('email', 'username', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'groups', 'created_at')
    
    # Campos para la edición (sin los campos auto)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas del sistema', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Campos para la creación de usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Registra el modelo
admin.site.register(User, CustomUserAdmin)