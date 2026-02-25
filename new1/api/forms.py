from django import forms
from .models import Trial
# from .models import UserType

# Form for letting user log in
class LoginForm(forms.Form):
    username = forms.CharField(label="Username ", required="true", max_length=100)
    password = forms.CharField(
        label="Password ", 
        max_length=100,
        required="true",
        # Adding a password widget for password 
        widget=forms.PasswordInput()
    )

# Form for letting user change password
class UpdatePassForm(forms.Form):
    username = forms.CharField(label="Username ", required="true", max_length=100)
    password = forms.CharField(
        label="New password ", 
        max_length=100,
        required="true",
        # Adding a password widget for password 
        widget=forms.PasswordInput()
    )

# Form for letting user change username 
class UpdateUserForm(forms.Form):
    current_username = forms.CharField(label="Username ", required="true", max_length=100)
    new_username = forms.CharField(
         
        max_length=100,
        required="true",
        label="New Username",
        widget=forms.TextInput(attrs={"placeholder": "Enter new username"}),
        
    )


# Form for letting user sign up
class SignUpForm(forms.Form):
    first_name = forms.CharField(label="First Name ", max_length=100, required="true")
    last_name = forms.CharField(label="Last Name ", max_length=100, required="true")
    username = forms.CharField(label="Username ", max_length=100, required="true")
    phone_number = forms.CharField(
        label="Phone Number ", max_length=20, required=False
    )
    email = forms.EmailField(label="Email ", required="true")
    date_of_birth = forms.DateField(
        label="Date Of Birth ",
        required="true",
        # Adding a calendar widget for easier date entry
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )
    password = forms.CharField(
        label="Password ", required="true", max_length=100,
        # Adding a password widget for password 
        widget=forms.PasswordInput()
    )
    selected_trial = forms.ModelChoiceField(
        label="Select Trial ",
        queryset=Trial.objects.none(),
        required=True,
        empty_label="Choose a trial",
    )
    trial_question_answer = forms.CharField(
        label="Answer the trial question ",
        required=True,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    consent_to_health_data_processing = forms.BooleanField(
        required=True,
        label="I consent to Cure-Link health data processing for trial matching.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["selected_trial"].queryset = Trial.objects.select_related("question").all()
    # user_type = forms.ChoiceField(
    #     label="User Type",
    #     choices=UserType.choices,
    #     initial=UserType.CUSTOMER,
    #     widget=forms.RadioSelect()
    # )
