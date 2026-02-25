from django.urls import path
from . import views
from .views import (
    login_user, logout_user, signup_user,
    users_api, user_api, update_password, update_username,
    trials_api, trial_api,
    trial_participations_api, trial_participation_api,
    trial_questions_api, trial_question_api,
    trial_question_answers_api, trial_question_answer_api,
    trial_options_api, trial_option_api,
    trial_specific_selections_api, trial_specific_selection_api,
    trial_reviews_api, trial_review_api
)

urlpatterns = [
    # Authentication
    path('', login_user, name='user login'),
    path('login/', login_user, name='user login'),
    path('signup/', signup_user, name='user signup'),
    path('updatePass/', update_password, name='update password'),
    path('updateUser/', update_username, name='update user'),
    path('logout/', logout_user, name='user logout'),

    # Users
    path('users/', users_api, name='users api'),
    path('user/<int:user_id>/', user_api, name='user api'),

    # Trials
    path('trials/', trials_api, name='trials api'),
    path('trial/<int:trial_id>/', trial_api, name='trial api'),

    # Trial Participation (Chosen)
    path('trialParticipations/', trial_participations_api, name='trialParticipations api'),
    path('trialParticipation/<int:participation_id>/', trial_participation_api, name='trialParticipation api'),

    # Trial Questions
    path('trialQuestions/', trial_questions_api, name='trialQuestions api'),
    path('trialQuestion/<int:question_id>/', trial_question_api, name='trialQuestion api'),

    # Trial Question Answers (ChosenCuisine)
    path('trialQuestionAnswers/', trial_question_answers_api, name='trialQuestionAnswers api'),
    path('trialQuestionAnswer/<int:answer_id>/', trial_question_answer_api, name='trialQuestionAnswer api'),

    # Trial Options (Allergy)
    path('trialOptions/', trial_options_api, name='trialOptions api'),
    path('trialOption/<int:option_id>/', trial_option_api, name='trialOption api'),

    # Trial Specific Selections (ChosenAllergy)
    path('trialSpecificSelections/', trial_specific_selections_api, name='trialSpecificSelections api'),
    path('trialSpecificSelection/<int:selection_id>/', trial_specific_selection_api, name='trialSpecificSelection api'),

    # Trial Reviews
    path('trialReviews/', trial_reviews_api, name='trialReviews api'),
    path('trialReview/<int:review_id>/', trial_review_api, name='trialReview api'),
]
