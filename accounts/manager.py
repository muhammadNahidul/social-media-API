from django.contrib.auth.base_user import BaseUserManager


class Managers(BaseUserManager):
    def create_user(self, email, password= None, **extra_fields):
        try:
            if not email:
                raise ValueError("Email Not Required")
            
            email= self.normalize_email(email=email)
            user= self.model(email=email, **extra_fields)
            user.set_password(password)
            
            user.save(using= self._db)

            return user
        except Exception as e:
            print(e)

        
    def create_superuser(self, email, password= None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)