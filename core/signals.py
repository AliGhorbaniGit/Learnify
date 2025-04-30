from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import UserProfile, CustomUser
from course.models import CourseAdditionRequest
from ticket.models import Ticket, TicketResponse


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_created_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()


@receiver(post_save, sender=CourseAdditionRequest)
def make_user_as_teacher_and_sent_confirm_ticket(sender, instance, **kwargs):
    if instance.status == 'a':
        user_profile = UserProfile.objects.get(user=instance.user)
        user_profile.is_teacher = True
        user_profile.save()

        ticket = Ticket.objects.filter(title='Application to Add a Course').first()
        ticket.status = 'Resolved'
        ticket.save()

        admin_user = CustomUser.objects.filter(is_staff=True).first()
        response_ticket = TicketResponse.objects.create(
            ticket=ticket,
            response_text=f' Dear {user_profile} , We are pleased to inform you that your request to add the course '
                          f'has been approved! Thank you for your valuable contribution to our learning community.'
                          f'You can now add the course using the "Add Course" option in your profile menu. '
                          f'If you have any questions or need further assistance, '
                          f'please feel free to reach out.Happy learning!'
                          f'Edrock',
            admin_user=admin_user
        )

        response_ticket.save()
