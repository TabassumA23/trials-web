from django.contrib import admin
from .models import (
    User, Trial, TrialQuestion, TrialOption, TrialParticipation,
    TrialQuestionAnswer, TrialSpecificSelection, TrialReview
)

# Register the trial participation through model
class TrialParticipationInline(admin.TabularInline):
    model = User.trialParticipation.through
    fk_name = 'user'

# Register the trial question answer through model
class TrialQuestionAnswerInline(admin.TabularInline):
    model = User.trialQuestionAnswer.through
    fk_name = 'user'

# Register the trial specific selection through model
class TrialSpecificSelectionInline(admin.TabularInline):
    model = User.trialSpecificSelection.through
    fk_name = 'user'

# Register the user model to the admin panel
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (TrialParticipationInline, TrialQuestionAnswerInline, TrialSpecificSelectionInline)

# Register the Trial model
@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'question')
    search_fields = ('name', 'user__first_name', 'user__last_name')
    list_filter = ('question',)

# Register the TrialQuestion model
@admin.register(TrialQuestion)
class TrialQuestionAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Register the TrialOption model
@admin.register(TrialOption)
class TrialOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'question')

# Register the TrialReview model
@admin.register(TrialReview)
class TrialReviewAdmin(admin.ModelAdmin):
    list_display = ('trial', 'user', 'rating', 'date')
    search_fields = ('trial__name', 'user__first_name', 'user__last_name')
    list_filter = ('rating',)
