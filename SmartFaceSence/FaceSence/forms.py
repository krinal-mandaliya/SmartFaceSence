from django import forms
from .models import *

class Signup_form(forms.ModelForm):
    confirmpassword = forms.CharField(max_length=30, widget=forms.PasswordInput())

    class Meta:
        model = Signup
        fields = ["name_office", "name_head", "address", "email_admin", "password"]
        widgets = {
            'password': forms.PasswordInput(),  # Ensure password input is hidden
        }

class Upload_imgForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["image"]

class Person_imgForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["person_name", "dob", "face_image", "doj", "scan_image", "person_email", "phoneno", "type_person"]

class FlatForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = ["block_no", "total_floor", "flat_no", "flat_type", "status", "alloted_to"]

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['visitor_name', 'mobile_no', 'address', 'visitor_image', 'flat_id', 'whome_to_meet', 'proof']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ['email_admin', 'name_office', 'name_head']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize the form fields if needed
        self.fields['email_admin'].widget.attrs['readonly'] = True