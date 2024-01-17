from django import forms
from .models import ImageModel


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = ['id','dob','image']



class PatientForm(forms.Form):
    id = forms.CharField()
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], widget=forms.RadioSelect)
    date_of_birth = forms.DateField()
    image = forms.ImageField()