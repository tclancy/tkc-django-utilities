from django.contrib.sites.models import Site

from registration.backends.default import DefaultBackend
from registration.models import RegistrationProfile
from registration import signals


class EmailBackend(DefaultBackend):
    
    def register(self, request, **kwargs):
        username, email, password = kwargs['username'], kwargs['username'], kwargs['password1']
        first_name, last_name = kwargs['first_name'], kwargs['last_name']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site,
                                                                    send_email=False)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user