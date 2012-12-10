import os

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


class ValidatedFileField(forms.FileField):
    def __init__(self, file_extensions, content_types,
                 max_file_size=None, *args, **kwargs):
        super(ValidatedFileField, self).__init__(*args, **kwargs)
        self.file_extensions = [f.lower().replace('.', '')
                                for f in file_extensions]
        self.content_types = content_types
        self.max_file_size = max_file_size

    def clean(self, data, initial=None):
        from django.template.defaultfilters import filesizeformat
        if not data and initial:
            return initial
        f = super(ValidatedFileField, self).clean(data)
        if not f:
            return f
        if self.max_file_size and self.max_file_size < f.size:
            raise forms.ValidationError('Files cannot exceed %s in size' %
                                        filesizeformat(self.max_file_size))
        # not allowing files without an extension, really a preference thing
        if not f.name or f.name.find('.') == -1:
            raise forms.ValidationError('Does not appear to be a valid file')
        extension = os.path.splitext(f.name)[-1].lower().replace('.', '')
        if not extension in self.file_extensions or \
        not f.content_type in self.content_types:
            raise forms.ValidationError('Accepted file types: %s' %\
                                        ' '.join(self.file_extensions))
        return super(ValidatedFileField, self).clean(data)
