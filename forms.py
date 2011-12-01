from django import forms
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput())
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(render_value=False))
    user = None

    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"],
                            password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError("This account is currently inactive.")
        else:
            raise forms.ValidationError("The username and/or password you specified are not correct.")
        
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            django_login(request, self.user)
            request.session.set_expiry(0)
            return True
        return False


class CustomDisplayModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.display_fx = kwargs.pop("display_fx")
        super(CustomDisplayModelChoiceField, self).__init__(*args, **kwargs)
    
    def label_from_instance(self, obj):
         return self.display_fx(obj)