from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group
import uuid


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email,first_name,last_name, password=None):
        """
        Creates, saves, and returns a User with the given email, first name, last name, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not first_name:
            raise ValueError('The First Name field must be set')
        if not last_name:
            raise ValueError('The Last Name field must be set')
        

        email = self.normalize_email(email).lower()
        user = self.model(email=email,first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save(using=self._db)
        return user
    


AUTH_PROVIDERS = [
    ('email', 'Email'),
    ('google', 'Google'),
    ('facebook', 'Facebook'),
]


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True)
    auth_provider = models.CharField(max_length=50,choices=AUTH_PROVIDERS,default='email'
)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-created_at']
        indexes =[
            models.Index(fields = ['email'])
        ]


    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)
       

