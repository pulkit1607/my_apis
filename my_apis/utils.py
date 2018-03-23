from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class SendEmail(object):
    def __init__(self, request=None, headers=None, sender=None, from_name=None, backend=None , file=[]):
        self.request = request
        self.headers = headers
        self.file = file

        if from_name:
            self.from_name = from_name
        else:
            self.from_name = settings.DEFAULT_FROM_EMAIL_NAME

        if sender:
            self.sender = sender
        else:
            self.sender = settings.DEFAULT_FROM_EMAIL

    def send(self, recipient, template_path, context, subject, bcc_email=[]):
        """
        send email function with template_path. will do both rendering & send in this function.
        should not change the interface.
        """

        body = self.email_render(template_path, context)
        self.send_email(recipient, subject, body, bcc_email)

    def send_email(self, recipient, subject, body, bcc_email):
        """
        send email with rendered subject and body
        """
        if bcc_email:
            msg = EmailMultiAlternatives(subject, subject, self.sender, recipient, bcc=bcc_email)
        else:
            msg = EmailMultiAlternatives(subject, subject, self.sender, recipient)

        msg.attach_alternative(body, "text/html")

        if self.file:
            for file in self.file:
                msg.attach_file(file)
        msg.send()

    def email_render(self, template_path, context):
        """
        wrapper to generate email subject and body
        """
        body = render_to_string(template_path, context)

        return body



def create_username(name):
    # create the unique username of every new user by using its name
    name = ''.join(e for e in name if e.isalnum())
    name = name[:29]
    base_name = name
    ctr = 1

    while True:
        try:
            user = User.objects.get(username=name)
            name = base_name + (str(ctr))
            ctr += 1
        except:
            break

    return name
