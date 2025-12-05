from django.core.mail import send_mail

from django.conf import settings

from .models import UserRegisters

import random
def send_otp_email_via(email):
    try:
        otp= random.randint(100000, 999999)
        subject= 'your verification mail'
        message= f'Your otp {otp}'

        email_form= settings.EMAIL_HOST_USER
        send_mail(subject, message, email_form, [email])

        try:
            user= UserRegisters.objects.get(email=email)
            user.otp= otp

            user.save()
        except user.DoesNotExist():
            print(f"your email {email} does't exits")

        
    except Exception as e:
        print(f"Error sending otp {otp}")
        return None