from django.db import models
from django.conf import settings


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('InProgress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=200, blank=True, )
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    submit_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        return f'{self.id}: {self.title}'

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-submit_date', ]


class TicketResponse(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='responses', on_delete=models.CASCADE)
    response_text = models.TextField()
    submit_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='responses', on_delete=models.CASCADE)

    def __str__(self):
        return f"Response to {self.ticket.title} by {self.admin_user.username}"

    class Meta:
        verbose_name = ' Ticket Response'
        verbose_name_plural = " Ticket's Responses"
        ordering = ['submit_date', ]
