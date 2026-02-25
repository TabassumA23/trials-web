import json
from django.conf import settings
from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.dateparse import parse_datetime

from .models import TrialParticipation, Trial, User, TrialQuestionAnswer, TrialQuestion, TrialReview, TrialOption,TrialSpecificSelection
from .forms import LoginForm, SignUpForm, UpdatePassForm, UpdateUserForm

# Authenticate login before Vue SPA redirect
def login_user(request: HttpRequest) -> HttpResponse:
    """ Function to validate a potenital registered user. """
    if request.method == "POST":
        form = LoginForm(request.POST)
        # Clean values if valid and authenticate
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(username=username, password=password)
            # Rendering Vue SPA if user is found
            if user is not None:
                auth.login(request, user)
                # Saving user id in variable to add to redirect as query
                user_id=user.id
                return redirect(settings.LOGIN_REDIRECT_URL+'?u=%s' %user_id)
            else:
                # Show failed authentication
                return render(request, "api/auth/login.html", {"form": form, "message": 'Username or password invalid, please try again.'})
    else:
        form = LoginForm()
    return render(request, "api/auth/login.html", {"form": form})


# Authenticate signup and login before Vue SPA redirect
def signup_user(request: HttpRequest) -> HttpResponse:
    """ Function to register a new user. """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        # Clean values if valid and authenticate
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            phone_number = form.cleaned_data.get("phone_number")
            password = form.cleaned_data["password"]
            selected_trial = form.cleaned_data["selected_trial"]
            selected_trial_option_id = form.cleaned_data["selected_trial_option"]
            # user_type field commented out in your model
            # user_type = form.cleaned_data.get("user_type", UserType.CUSTOMER)

            selected_trial_option = selected_trial.options.filter(
                id=selected_trial_option_id
            ).first()
            if selected_trial_option is None:
                form.add_error(
                    "selected_trial_option",
                    "Please select a valid option for the selected trial.",
                )
                return render(
                    request,
                    "api/auth/signup.html",
                    {"form": form, "trials": Trial.objects.select_related("question").prefetch_related("options").all()},
                )

            # Check if username already exists before creating account
            if not User.objects.filter(username=username).exists():
                # Create a new user with input form details
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                user.first_name = first_name
                user.last_name = last_name
                user.date_of_birth = date_of_birth
                user.phone_number = phone_number
                # user.user_type = user_type  # Uncomment if you re-enable user_type
                user.save()

                # Save trial enrollment and answer captured during signup
                TrialParticipation.objects.create(user=user, trial=selected_trial)
                TrialQuestionAnswer.objects.create(
                    user=user,
                    question=selected_trial.question,
                    answer_text=selected_trial_option.name,
                )
                TrialSpecificSelection.objects.create(
                    user=user,
                    option=selected_trial_option,
                )

                # Log in the new user
                auth.login(request, user)

                # Redirect to Vue SPA with user ID
                user_id = user.id
                return redirect(f"{settings.LOGIN_REDIRECT_URL}?u={user_id}")
            else:
                # Show failed user creation
                return render(
                    request,
                    "api/auth/signup.html",
                    {
                        "form": form,
                        "trials": Trial.objects.select_related("question").prefetch_related("options").all(),
                        "message": "User already exists with that username. Please try again.",
                    },
                )
    else:
        form = SignUpForm()
    return render(
        request,
        "api/auth/signup.html",
        {"form": form, "trials": Trial.objects.select_related("question").prefetch_related("options").all()},
    )
        
@login_required
# Logout user below
def logout_user(request: HttpRequest) -> HttpResponse:
    """ Function to logout a user. """
    auth.logout(request)
    return redirect(settings.LOGIN_URL)


# APIs for user model below


@login_required
def users_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for the Users"""
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method == 'POST':
        try:
            POST = json.loads(request.body)
            required_fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'password', 'phone_number']
            missing_fields = [field for field in required_fields if field not in POST]
            if missing_fields:
                return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

            # Optional trial participation, question answers, and specific selections
            trial_ids = POST.get('trial_ids', [])                # list of Trial IDs
            question_answers = POST.get('question_answers', [])  # list of dicts: {question_id, answer_text}
            option_ids = POST.get('option_ids', [])              # list of TrialOption IDs

            # Create user
            user = User.objects.create(
                first_name=POST['first_name'],
                last_name=POST['last_name'],
                email=POST['email'],
                phone_number=phone_number,
                date_of_birth=POST['date_of_birth'],
                password=POST['password'],
            )

             # Add trials (TrialParticipation)
            for trial_id in trial_ids:
                trial = Trial.objects.get(id=trial_id)
                TrialParticipation.objects.create(user=user, trial=trial)

            # Add question answers (TrialQuestionAnswer)
            for qa in question_answers:
                question = TrialQuestion.objects.get(id=qa['question_id'])
                answer_text = qa.get('answer_text', 'chosenAnswer')
                TrialQuestionAnswer.objects.create(user=user, question=question, answer_text=answer_text)

            # Add specific selections (TrialSpecificSelection)
            for option_id in option_ids:
                option = TrialOption.objects.get(id=option_id)
                TrialSpecificSelection.objects.create(user=user, option=option)

            return JsonResponse(user.as_dict(), status=201)
            return JsonResponse(user.as_dict(), status=201)
       # Handle missing related objects
        except (Trial.DoesNotExist, TrialQuestion.DoesNotExist, TrialOption.DoesNotExist):
            return JsonResponse({"error": "Invalid trial, question, or option ID provided."}, status=400)

        # General error
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # GET Method
    return JsonResponse({
        'users': [
            user.as_dict()
            for user in User.objects.all()
        ]
    })

@login_required
def user_api(request: HttpRequest, user_id: int) -> JsonResponse:
    """API endpoint for a single user"""
    if request.user.id != user_id and not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # PUT method to update user fields
    if request.method == 'PUT':
        try:
            PUT = json.loads(request.body)
            user.first_name = PUT.get("first_name", user.first_name)
            user.last_name = PUT.get("last_name", user.last_name)
            user.email = PUT.get("email", user.email)
            user.phone_number = PUT.get("phone_number", user.phone_number)
            user.date_of_birth = PUT.get("date_of_birth", user.date_of_birth)
            user.password = PUT.get("password", user.password)
            user.save()
            return JsonResponse({"success": "User updated successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # DELETE method
    if request.method == 'DELETE':
        user.delete()
        return JsonResponse({}, status=204)


    # GET method
    return JsonResponse(user.as_dict())


# APIs for chosen model below
# APIs for TrialParticipation (Chosen trial)
def trial_participations_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for TrialParticipation"""

    if request.method == 'POST':
        POST = json.loads(request.body)
        user = User.objects.get(id=POST['user_id'])
        trial = Trial.objects.get(id=POST['trial_id'])
        participation = TrialParticipation.objects.create(user=user, trial=trial)
        return JsonResponse(participation.as_dict())

    return JsonResponse({
        'trial_participations': [tp.as_dict() for tp in TrialParticipation.objects.all()]
    })


def trial_participation_api(request: HttpRequest, tp_id: int) -> JsonResponse:
    """API endpoint for a single TrialParticipation"""
    try:
        tp = TrialParticipation.objects.get(id=tp_id)
    except TrialParticipation.DoesNotExist:
        return JsonResponse({"error": "TrialParticipation not found."}, status=404)

    if request.method == 'DELETE':
        tp.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(tp.as_dict())

@login_required
def update_password(request: HttpRequest) -> HttpResponse:
    """ Function to validate a potenital registered user. """
    if request.method == "POST":
        form = UpdatePassForm(request.POST)  # Use a form specifically for password updates
        if form.is_valid():
            password = form.cleaned_data["password"]

            try:
                if not password:
                    return JsonResponse({"error": "Password is required."}, status=400)

                # Use the currently logged-in user to update the password
                user = request.user
                user.set_password(password)  # Hash and set the new password
                user.save() 
                return redirect(settings.LOGIN_URL)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        # Return form errors if invalid
        return render(request, "api/auth/updatePass.html", {"form": form, "errors": form.errors})

    # For GET requests, display the form
    else:
        form = UpdatePassForm()
    return render(request, "api/auth/updatePass.html", {"form": form})


@login_required
def update_username(request: HttpRequest) -> HttpResponse:
    """Function to update the username of the logged-in user."""
    if request.method == "POST":
        form = UpdateUserForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data["new_username"]

            try:
                # Ensure the new username is not already taken
                if User.objects.filter(username=new_username).exists():
                    return render(request, "api/auth/updateUsername.html", {"form": form, "message": "username exists already"})
                    return redirect(settings.LOGIN_URL)

                # Update the username
                user = request.user
                user.username = new_username
                user.save()

                return redirect(settings.LOGIN_URL)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        # Render form with errors if invalid
        return render(request, "api/auth/updateUsername.html", {"form": form, "errors": form.errors})

    # For GET requests, display the form
    else:
        form = UpdateUserForm()
        return render(request, "api/auth/updateUsername.html", {"form": form})
    
# APIs for cuisine model below

# APIs for TrialQuestion (Cuisine equivalent)
def trial_questions_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for TrialQuestion"""

    if request.method == 'POST':
        POST = json.loads(request.body)
        question = TrialQuestion.objects.create(
            name=POST['name'],
        )
        return JsonResponse(question.as_dict())

    return JsonResponse({
        'trial_questions': [q.as_dict() for q in TrialQuestion.objects.all()]
    })

def trial_question_api(request: HttpRequest, question_id: int) -> JsonResponse:
    """API endpoint for a single TrialQuestion"""
    try:
        question = TrialQuestion.objects.get(id=question_id)
    except TrialQuestion.DoesNotExist:
        return JsonResponse({"error": "TrialQuestion not found."}, status=404)

    if request.method == 'PUT':
        PUT = json.loads(request.body)
        question.name = PUT.get("name", question.name)
        question.save()
        return JsonResponse(question.as_dict())

    if request.method == 'DELETE':
        question.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(question.as_dict())

# APIs for chosenCuisine model below
# APIs for TrialQuestionAnswer (ChosenCuisine equivalent)
def trial_question_answers_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for TrialQuestionAnswer"""
    if request.method == 'POST':
        POST = json.loads(request.body)
        user = User.objects.get(id=POST['user_id'])
        question = TrialQuestion.objects.get(id=POST['question_id'])
        answer = POST.get('answer_text', 'chosenAnswer')
        tqa = TrialQuestionAnswer.objects.create(user=user, question=question, answer_text=answer)
        return JsonResponse(tqa.as_dict())

    return JsonResponse({
        'trial_question_answers': [tqa.as_dict() for tqa in TrialQuestionAnswer.objects.all()]
    })
def trial_question_answer_api(request: HttpRequest, tqa_id: int) -> JsonResponse:
    """API endpoint for a single TrialQuestionAnswer"""
    try:
        tqa = TrialQuestionAnswer.objects.get(id=tqa_id)
    except TrialQuestionAnswer.DoesNotExist:
        return JsonResponse({"error": "TrialQuestionAnswer not found."}, status=404)

    if request.method == 'PUT':
        PUT = json.loads(request.body)
        tqa.answer_text = PUT.get("answer_text", tqa.answer_text)
        tqa.save()
        return JsonResponse(tqa.as_dict())

    if request.method == 'DELETE':
        tqa.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(tqa.as_dict())

# APIs for chosenCuisine model below
# APIs for TrialSpecificSelection (ChosenAllergy equivalent)
def trial_specific_selections_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for TrialSpecificSelection"""

    if request.method == 'POST':
        POST = json.loads(request.body)
        user = User.objects.get(id=POST['user_id'])
        option = TrialOption.objects.get(id=POST['option_id'])
        selection = TrialSpecificSelection.objects.create(user=user, option=option)
        return JsonResponse(selection.as_dict())

    return JsonResponse({
        'trial_specific_selections': [s.as_dict() for s in TrialSpecificSelection.objects.all()]
    })


def trial_specific_selection_api(request: HttpRequest, selection_id: int) -> JsonResponse:
    """API endpoint for a single TrialSpecificSelection"""
    try:
        selection = TrialSpecificSelection.objects.get(id=selection_id)
    except TrialSpecificSelection.DoesNotExist:
        return JsonResponse({"error": "TrialSpecificSelection not found."}, status=404)

    if request.method == 'DELETE':
        selection.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(selection.as_dict())

# APIs for restaurant model below
# APIs for TrialReview (Review equivalent)
def trial_reviews_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for TrialReview"""

    if request.method == 'POST':
        POST = json.loads(request.body)
        trial = Trial.objects.get(id=POST['trial_id'])
        user = User.objects.get(id=POST['user_id'])
        review = TrialReview.objects.create(
            name=POST.get('name', ''),
            trial=trial,
            rating=POST['rating'],
            description=POST.get('description', ''),
            user=user
        )
        return JsonResponse(review.as_dict())

    return JsonResponse({
        'trial_reviews': [r.as_dict() for r in TrialReview.objects.all()]
    })


def trial_review_api(request: HttpRequest, review_id: int) -> JsonResponse:
    """API endpoint for a single TrialReview"""
    try:
        review = TrialReview.objects.get(id=review_id)
    except TrialReview.DoesNotExist:
        return JsonResponse({"error": "TrialReview not found."}, status=404)

    if request.method == 'PUT':
        PUT = json.loads(request.body)
        review.name = PUT.get("name", review.name)
        review.rating = PUT.get("rating", review.rating)
        review.description = PUT.get("description", review.description)
        review.save()
        return JsonResponse(review.as_dict())

    if request.method == 'DELETE':
        review.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(review.as_dict())

# APIs for cuisine model below
# APIs for TrialOption (Allergy equivalent)
def trial_options_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for TrialOption"""

    if request.method == 'POST':
        POST = json.loads(request.body)
        question = TrialQuestion.objects.get(id=POST['question_id'])
        option = TrialOption.objects.create(
            name=POST['name'],
            question=question,
        )
        return JsonResponse(option.as_dict())

    question_id = request.GET.get("question_id")
    options_qs = TrialOption.objects.all()
    if question_id:
        options_qs = options_qs.filter(question_id=question_id)

    option_list = [option.as_dict() for option in options_qs]
    return JsonResponse({
        'trial_options': option_list,
        'trialOptions': option_list,
    })

def trial_option_api(request: HttpRequest, option_id: int) -> JsonResponse:
    """API endpoint for a single TrialOption"""
    try:
        option = TrialOption.objects.get(id=option_id)
    except TrialOption.DoesNotExist:
        return JsonResponse({"error": "TrialOption not found."}, status=404)

    if request.method == 'PUT':
        PUT = json.loads(request.body)
        option.name = PUT.get("name", option.name)
        if "question_id" in PUT:
            option.question = TrialQuestion.objects.get(id=PUT["question_id"])
        option.save()
        return JsonResponse(option.as_dict())

    if request.method == 'DELETE':
        option.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(option.as_dict())


# APIs for restaurant model below
def trials_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for Trial"""

    if request.method == 'POST':
        POST = json.loads(request.body)
        user = User.objects.get(id=POST['user_id'])
        question = TrialQuestion.objects.get(id=POST['question_id'])
        option_ids = POST.get('option_ids', [])
        trial = Trial.objects.create(
            name=POST['name'],
            user=user,
            question=question
        )
        options = TrialOption.objects.filter(id__in=option_ids, question=question)
        if len(option_ids) != options.count():
            return JsonResponse(
                {"error": "Some selected options do not belong to the selected trial question."},
                status=400,
            )
        trial.options.set(options)
        trial.save()
        return JsonResponse(trial.as_dict())

    return JsonResponse({
        'trials': [trial.as_dict() for trial in Trial.objects.all()]
    })
def trial_api(request: HttpRequest, trial_id: int) -> JsonResponse:
    """API endpoint for a single Trial"""
    try:
        trial = Trial.objects.get(id=trial_id)
    except Trial.DoesNotExist:
        return JsonResponse({"error": "Trial not found."}, status=404)

    if request.method == 'PUT':
        PUT = json.loads(request.body)
        trial.name = PUT.get("name", trial.name)
        if "question_id" in PUT:
            trial.question = TrialQuestion.objects.get(id=PUT["question_id"])
        if "option_ids" in PUT:
            options = TrialOption.objects.filter(
                id__in=PUT["option_ids"],
                question=trial.question,
            )
            if len(PUT["option_ids"]) != options.count():
                return JsonResponse(
                    {"error": "Some selected options do not belong to the selected trial question."},
                    status=400,
                )
            trial.options.set(options)
        trial.save()
        return JsonResponse(trial.as_dict())

    if request.method == 'DELETE':
        trial.delete()
        return JsonResponse({}, status=204)

    return JsonResponse(trial.as_dict())



    # try:
    #     user = User.objects.get(id=user_id)
    #     wishlists = user.shared_list.all()
    #     return JsonResponse({
    #         "shared_wishlists": [w.as_dict() for w in wishlists]
    #     })
    # except User.DoesNotExist:
    #     return JsonResponse({"error": "User not found."}, status=404)


# # APIs for restaurant model below
# @login_required
# def reservations_api(request: HttpRequest) -> JsonResponse:
#     """API endpoint for the Reservation"""

#     # POST method to create a reservation
#     if request.method == 'POST':
#         try:
#             POST = json.loads(request.body)
#             user_id = POST['user_id']
            
#             print("Received POST data:", POST)  # Debugging line to check POST data

#             # Ensure 'number_of_people' is in the request
#             if 'number_of_people' not in POST:
#                 return JsonResponse({"error": "'number_of_people' is missing"}, status=400)
#             reservation_time = parse_datetime(POST['reservation_time'])
#             if reservation_time is None:
#                 return JsonResponse({"error": "Invalid datetime format."}, status=400)
#             restaurant = Restaurant.objects.get(id=POST['restaurant_id'])
#             reservation = Reservation.objects.create(
#                 restaurant=restaurant,
#                 reservation_time=reservation_time,
#                 number_of_people=POST['number_of_people'],
#                 status=POST['status'],
#                 special_requests=POST.get('special_requests', ''),
#                 user=User.objects.get(id=user_id),
#             )
#             return JsonResponse(reservation.as_dict())

#         except KeyError as e:
#             return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
#         except Restaurant.DoesNotExist:
#             return JsonResponse({"error": "Restaurant not found"}, status=404)
#         except Exception as e:
#             return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

#     # If GET method is used, return all reservations
#     return JsonResponse({
#         'reservations': [
#             reservation.as_dict()
#             for reservation in Reservation.objects.all()
#         ]
#     })

# def reservation_api(request: HttpRequest, reservation_id: int) -> JsonResponse:
#     """API endpoint for a single reservation"""
#     try:
#         reservation = Reservation.objects.get(id=reservation_id)
#     except Reservation.DoesNotExist:
#         return JsonResponse({"error": "Reservation not found."}, status=404)

#     # PUT method to update reservation
#     if request.method == 'PUT':
#         try:
#             PUT = json.loads(request.body)
            
#             reservation.reservation_time = PUT.get("reservation_time", reservation.reservation_time)
#             reservation.number_of_people = PUT.get("number_of_people", reservation.number_of_people)
#             reservation.status = PUT.get("status", reservation.status)
#             reservation.special_requests = PUT.get("special_requests", reservation.special_requests)
#             reservation.save()
#             return JsonResponse(reservation.as_dict())
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     # DELETE method to delete reservation
#     if request.method == 'DELETE':
#         reservation.delete()
#         return JsonResponse({}, status=204)  # 204 No Content

#     # GET reservation data
#     return JsonResponse(reservation.as_dict())
