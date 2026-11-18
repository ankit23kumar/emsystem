from django.db import models

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True, db_column="userId")
    first_name = models.CharField(max_length= 40, db_column="firstname")
    last_name = models.CharField(max_length=40, db_column ="lastname")
    email = models.EmailField(unique= True)
    password = models.CharField(max_length= 128)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    
    role = models.ForeignKey(
        "roles.Role",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users"
    )
    
    def __str__(self):
        return self.email