from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import logging
from django.core.validators import MinValueValidator
from django.conf import settings




# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler and a stream handler
file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


# Create your models here.


class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Page view count: {self.count}"
# Allergy
class TrialOption(models.Model):
    '''
    Class for the allergy
    '''
    name = models.CharField(max_length=100)
    question = models.ForeignKey('TrialQuestion', on_delete=models.CASCADE, related_name='options', null=True, blank=True)
    
    
    def __str__(self):
        return self.name
    
    '''
    Dictionary
    '''
    def as_dict(self):
        return {
            'id': self.id,
            # Obtains URL pattern for individual cuisine
            'api': reverse('trialOption api', args=[self.id]),
            'name': self.name,
            'question_id': self.question.id if self.question else None,
            
        }
#Cuisine 
class TrialQuestion(models.Model):
    '''
    Class for the cusine
    '''
    name = models.CharField(max_length=100)

    
    def __str__(self):
        return self.name
    
    '''
    Dictionary
    '''
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }
#Restaurant   
class Trial(models.Model):
    """
    Class for a trial
    """
    name = models.CharField(max_length=100)
    question = models.ForeignKey(TrialQuestion, on_delete=models.CASCADE)
    options = models.ManyToManyField(TrialOption)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Owner / creator of trial
    
    def __str__(self):
        return self.name
    
    def as_dict(self):
        return {
            'id': self.id,
            'api': reverse('trial api', args=[self.id]),
            'name': self.name,
            'question_id': self.question.id,
            'question': self.question.name,
            'option_ids': [option.id for option in self.options.all()],
            'options': [option.name for option in self.options.all()],
            'user': {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'id': self.user.id,
            }
        }




    
# Enum for user types
class UserType(models.TextChoices):
    OWNER = 'Owner', 'Owner'
    CUSTOMER = 'Customer', 'Customer'
#Patient
class User(AbstractUser):
    '''
    Class containing the custom user model which inherits the abstract user model from django making use of 
    authentication framework    
    '''
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(default='2000-01-01')
    password = models.CharField(max_length=128)
    # user_type = models.CharField(
    #     max_length=20,
    #     choices=UserType.choices,
    #     default=UserType.CUSTOMER,
    # )  
    trialParticipation = models.ManyToManyField(Trial, through='TrialParticipation', related_name="participants")
    trialQuestionAnswer = models.ManyToManyField(TrialQuestion, through='TrialQuestionAnswer', related_name="answered_by")
    trialSpecificSelection = models.ManyToManyField(TrialOption, through='TrialSpecificSelection', related_name="selected_by")

    def __str__(self):
         return f"{self.first_name} {self.last_name}"
    
    '''
    Dictionary
    '''
    def as_dict(self):
        return {  
            'id': self.id,  
            # Obtains URL pattern for individual user 
            'api': reverse('user api', args=[self.id]),
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth,
            'is_staff': self.is_staff,
            # 'user_type': self.user_type,
        }


#chosen Trial    
#Chosen
#(records a user’s enrollment in a trial)
class TrialParticipation(models.Model):
     """
    This class is the Chosen Model which is a through model 
    which creates a many to many relationship between user and restaurant
    """
     user = models.ForeignKey('User', on_delete=models.CASCADE)
     trial = models.ForeignKey('Trial', on_delete=models.CASCADE)
     #title= models.CharField(max_length=100, default="chosen")
     def as_dict(self):
        return{
            'id': self.id,
            'api': reverse('trialParticipation api', args=[self.id]),
            'user': self.user.id,
            'trial': self.trial.id,
            #'title': self.trial.title,
        }
#ChosenCuisine
class TrialQuestionAnswer(models.Model):
    """
    Through model linking a User to a TrialQuestion they answered.
    Related names kept for reverse queries.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="chosen_questions")
    question = models.ForeignKey('TrialQuestion', on_delete=models.CASCADE, related_name="chosen_by_users")
    answer_text = models.TextField(blank=True, default="chosenAnswer")
    
    def as_dict(self):
        return {
            'id': self.id,
            'api': reverse('trialQuestionAnswer api', args=[self.id]),
            'user': self.user.id,
            'question': self.question.id,
            'answer_text': self.answer_text,
        }
     
#ChosenAllergy
class TrialSpecificSelection(models.Model):
    """
    Through model linking a User to a TrialOption or Allergy they selected.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="selected_options")
    option = models.ForeignKey('TrialOption', on_delete=models.CASCADE, related_name="selected_by_users")

    def as_dict(self):
        return {
            'id': self.id,
            'api': reverse('trialSpecificSelection api', args=[self.id]),
            'user': self.user.id,
            'option': self.option.id,
        }

# #(trial feedback review/ results )

class TrialReview(models.Model):
    """
    Class for trial feedback / review
    """
    name = models.CharField(max_length=255, blank=True)  # Optional title for the review
    trial = models.ForeignKey('Trial', on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()  # Overall rating
    description = models.TextField(max_length=500, blank=True)  # Optional detailed feedback
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="trial_reviews")
    date = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"{self.trial.name} - {self.user.first_name}"

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'trial': {
                'id': self.trial.id,
                'name': self.trial.name,
            },
            'rating': self.rating,
            'description': self.description,
            'date': self.date,
            'user': {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'id': self.user.id,
            }
        }
