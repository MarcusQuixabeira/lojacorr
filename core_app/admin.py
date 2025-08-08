from django.contrib import admin
from .models import Insured

@admin.register(Insured)
class InsuredAdmin(admin.ModelAdmin):
    list_display = ["name", "cpf", "email"]
    exclude = ['password']
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
    
        
