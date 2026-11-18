from django.db import models


class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name
    
class Permission(models.Model):
    permission_id = models.BigAutoField(primary_key=True)
    permission_name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.permission_name
    
    
class RolePermission(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions"
    )
    
    permission = models.ForeignKey(
        Permission,
        on_delete=models.PROTECT,
        related_name="role_permissions"
    )
    
    class Meta: 
        constraints = [
            models.UniqueConstraint(
                fields=["role","permission"],
                name="unique_role_permission"
            )
        ]
    
    def __str__(self):
        return f"{self.role.role_name} - {self.permission.permission_name}"
