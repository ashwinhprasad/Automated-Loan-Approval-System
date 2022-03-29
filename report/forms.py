from django import forms
from .models import SheetModel

class SingleUserDetailForm(forms.Form):

    education_choices = ((1,'Graduate'),(0,'Not Graduate'))
    credit_choices = ((1,'Satisfied'),(0,'Not Satisfied'))
    property_area_choices = ((0,'Rural'),(1,'Semi-Urban'),(2,'Urban'))
    martial_status_choices = ((0,"Yes"),(1,"No"))



    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    education = forms.ChoiceField(choices=education_choices)
    income = forms.IntegerField(max_value=100000000)
    credit = forms.ChoiceField(choices=credit_choices)
    property_area = forms.ChoiceField(choices=property_area_choices)
    amount_term = forms.IntegerField(max_value=100000)
    marital_status = forms.ChoiceField(choices=martial_status_choices)
    loan_amount = forms.IntegerField(max_value=1000000)
    send_mail = forms.BooleanField(label='Send mail to client ?',initial=False,required=False)

class SheetForm(forms.ModelForm):
    mail_send = forms.BooleanField(label='Send mail to client ?',initial=False,required=False)
    class Meta:
        model = SheetModel
        fields = ('sheet',)