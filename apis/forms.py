from django import forms
from django.contrib.auth.models import User

from apis.models import HotelBranch, Menu, ContactForm, Profile, Order
from my_apis.utils import create_username

class AddLocationForm(forms.ModelForm):

    class Meta:
        model=HotelBranch
        exclude = ('hotel', 'lat', 'long', 'location', 'objects')

class AddMenuForm(forms.ModelForm):

    class Meta:
        model = Menu
        exclude = ('hotel', )

class ContactUsForm(forms.ModelForm):

    class Meta:
        model = ContactForm
        exclude = {}


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('date', 'time', 'number_of_persons', 'special_notes')

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control login-inputs','placeholder':'Email ID'}),
                             error_messages={'required':'Email is required'})
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control login-inputs','placeholder':'Password'}),
                             error_messages={'required':'Password is required'})
    # captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        if forms.Form.is_valid(self):
            try:
                user = User.objects.get(email__iexact=self.cleaned_data['email'])
            except:
                raise forms.ValidationError("The email or password provided was incorrect.")

            if not user.check_password(self.cleaned_data['password']):
                raise forms.ValidationError("The email or password provided was incorrect.")

        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control login-inputs', 'placeholder': 'Email Address'}),
                             error_messages={'required':'Email is required'})

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError('This email is not attached to a user account.')
        except User.MultipleObjectsReturned:
            raise forms.ValidationError('Multiple accounts found. Please contact the admins.')

        return email


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-lg', 'placeholder': 'Password'}), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-lg', 'placeholder': 'Confirm Password'}), min_length=8)

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return self.cleaned_data['password']


class SignupForm(forms.ModelForm):
    first_name = forms.RegexField(regex=r'(?u)^[\s\w.@+-]+$',
                                    widget=forms.TextInput(attrs={'class':'form-control signup-inputs', 'placeholder': 'First Name'}),
                                    error_messages={'invalid': "Only letters, numbers and @/./+/-/_ characters accepted.",
                                                    'required': "First name is required"})
    last_name = forms.RegexField(regex=r'(?u)^[\s\w.@+-]+$',
                                    widget=forms.TextInput(attrs={'class':'form-control signup-inputs', 'placeholder': 'Last Name'}),
                                    error_messages = {'invalid': "Only letters, numbers and @/./+/-/_ characters accepted.",
                                                        'required': "Last name is required"})
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control signup-inputs', 'placeholder': 'Email'}),
                                error_messages={'required':"Email is required"})
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control signup-inputs', 'placeholder': 'Password'}),
                                min_length=8,
                                error_messages={'required':"Password is required"})
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control signup-inputs', 'placeholder': 'Confirm Password'}),
                                        min_length=8,
                                        error_messages={'required': "Password is required"})
    # captcha = CaptchaField()

    class Meta:
        model = Profile
        fields = ('contact',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['contact'].widget.attrs.update({'class': 'form-control input-lg', 'placeholder' :'Mobile Number'})

    def clean_email(self):
        try:
            existing_user = User.objects.get(email__iexact=self.cleaned_data['email'])
            if existing_user:
                self._errors["email"] = self.error_class(["An account already exists under this email address. Please use the forgot password function to log in."])
        except User.MultipleObjectsReturned:
            self._errors["email"] = self.error_class(["An account already exists under this email address. Please use the forgot password function to log in."])
        except:
            pass

        return self.cleaned_data['email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return self.cleaned_data['password']

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        return cleaned_data

    def save(self):
        user = User.objects.create_user(create_username(self.cleaned_data['first_name'].title() + self.cleaned_data['last_name'].title()), self.cleaned_data['email'], self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name'].title()
        user.last_name = self.cleaned_data['last_name'].title()
        user.is_active = False
        user.save()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.contact = self.cleaned_data['contact']
        profile.save()
        return profile


