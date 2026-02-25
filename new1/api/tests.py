from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import logging
from django.core.exceptions import ValidationError
import json

from .models import (
    User, Restaurant, Cuisine, Allergy, Reservation, Review,
    Chosen, ChosenCuisine, ChosenAllergy, Friendship,
    Wishlist, WishlistItem, WishlistShare
)

class ExtendedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass", email="user1@example.com")
        self.friend = User.objects.create_user(username="user2", password="pass", email="user2@example.com")
        self.cuisine = Cuisine.objects.create(name="Greek", description="Mediterranean style")
        self.allergy = Allergy.objects.create(name="Peanuts", description="Nut allergy")
        self.restaurant = Restaurant.objects.create(
            name="Taverna",
            cuisine=self.cuisine,
            rating=4,
            seats_available=20,
            location="Seaside",
            user=self.user
        )
        self.restaurant.allergys.add(self.allergy)
        self.wishlist = Wishlist.objects.create(name="Try Soon", owner=self.user)
        self.review = Review.objects.create(
            name="Great food",
            restaurant=self.restaurant,
            rating=5,
            food_rating=5,
            service_rating=4,
            ambience_rating=5,
            description="Excellent place",
            user=self.user,
            date=timezone.now()
        )

    def test_invalid_user_email(self):
        user = User.objects.create_user(
            username="invalid_email_user",
            email="invalid-email",  # No '@' but still allowed in model
            password="pass"
        )
        self.assertEqual(user.email, "invalid-email")

    def test_negative_reservation_people(self):
        reservation = Reservation(
        user=self.user,
        restaurant=self.restaurant,
        reservation_time=timezone.now(),
        number_of_people=-1,
        status=0,
        special_requests="Window"
        )
        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_models_str(self):
        self.assertEqual(str(self.allergy), "Peanuts")
        self.assertEqual(str(self.review), "Taverna")
        self.assertEqual(str(self.restaurant), "Taverna")
        self.user.first_name = "user1"
        self.user.last_name = "test"
        self.user.save()
        self.assertEqual(str(self.user), "user1 test")

    def test_friendship_creation(self):
        friend = Friendship.objects.create(user=self.user, friend=self.friend)
        self.assertEqual(friend.friend.username, "user2")

    def test_chosen_items(self):
        Chosen.objects.create(user=self.user, restaurant=self.restaurant)
        ChosenCuisine.objects.create(user=self.user, cuisine=self.cuisine)
        ChosenAllergy.objects.create(user=self.user, allergy=self.allergy)
        self.assertEqual(Chosen.objects.count(), 1)
        self.assertEqual(ChosenCuisine.objects.count(), 1)
        self.assertEqual(ChosenAllergy.objects.count(), 1)

    def test_wishlist_item_and_share(self):
        WishlistItem.objects.create(wishlist=self.wishlist, restaurant=self.restaurant, owner=self.user)
        WishlistShare.objects.create(wishlist=self.wishlist, user=self.friend, can_edit=True)
        self.assertEqual(WishlistItem.objects.count(), 1)
        self.assertEqual(WishlistShare.objects.count(), 1)

    def test_users_api_post(self):
        data = {
            "first_name": "Anna", "last_name": "Smith", "email": "anna@ex.com",
            "date_of_birth": "2000-01-01", "password": "secret"
        }
        res = self.client.post(reverse("users api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 201)

    def test_user_api_put_delete(self):
        update = {"first_name": "Updated"}
        res = self.client.put(reverse("user api", args=[self.user.id]), json.dumps(update), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        res = self.client.delete(reverse("user api", args=[self.user.id]))
        self.assertIn(res.status_code, [200, 204])

    def test_recommendation_api(self):
        data = {
            "allergys": [self.allergy.id],
            "cuisines": [self.cuisine.id]
        }
        res = self.client.post(reverse("recommend restaurants"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("restaurants", res.json())

    def test_share_wishlist(self):
        data = {"shared_with": [self.friend.id]}
        res = self.client.put(reverse("share_wishlist", args=[self.wishlist.id]), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)

    def test_review_as_dict(self):
        data = self.review.as_dict()
        self.assertEqual(data["restaurant"], self.restaurant.name)
        self.assertEqual(data["user"]["first_name"], self.user.first_name)

    def test_reservation_api_crud(self):
        self.client.login(username="user1", password="testpass")
        self.client.force_login(self.user)

        data = {
            "user_id": self.user.id,
            "restaurant_id": self.restaurant.id,
            "reservation_time": timezone.now().isoformat(),
            "number_of_people": 2,
            "status": 0,
            "special_requests": "Quiet table"
        }
        res = self.client.post(reverse("reservations api"), json.dumps(data), content_type="application/json")
        print("API Response:", res.content)
        self.assertEqual(res.status_code, 200)

        reservation_id = res.json().get("id")

        # Update
        update = {"number_of_people": 4}
        res = self.client.put(reverse("reservation api", args=[reservation_id]), json.dumps(update), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # Delete
        res = self.client.delete(reverse("reservation api", args=[reservation_id]))
        self.assertEqual(res.status_code, 204)

    def test_review_api_crud(self):
        # Create
        data = {
            "restaurant_id": self.restaurant.id,
            "user_id": self.user.id,
            "name": "Decent",
            "rating": 4,
            "food_rating": 4,
            "service_rating": 4,
            "ambience_rating": 3,
            "description": "Good overall"
        }
        res = self.client.post(reverse("reviews api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        review_id = res.json().get("id")

        # Update
        update = {"rating": 5}
        res = self.client.put(reverse("review api", args=[review_id]), json.dumps(update), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # Delete
        res = self.client.delete(reverse("review api", args=[review_id]))
        self.assertEqual(res.status_code, 204)

    # def test_auth_required_for_protected_views(self):
    #     self.client.logout()

    #     protected_url = reverse("wishlist_api", args=[self.wishlist.id])
    #     res = self.client.get(protected_url)

    #     self.assertNotEqual(res.status_code, 200)
    #     self.assertIn(res.status_code, [302, 403, 401])

    
        # client = Client()
        # res = client.get(reverse("wishlist api", args=[self.wishlist.id]))
        # self.assertNotEqual(res.status_code, 200)

        # self.client.logout()
        # res = self.client.get(reverse("wishlist api", args=[self.wishlist.id]))
        # self.assertNotEqual(res.status_code, 200)

    def test_owner_can_only_delete_their_wishlist(self):
        # Try deleting as someone else
        self.client.force_login(self.friend)
        res = self.client.delete(reverse("wishlist api", args=[self.wishlist.id]))
        self.assertIn(res.status_code, [403, 401])

    

    def test_prevent_duplicate_friendships(self):
        logging.info('Testing prevent duplicate friendships')
        Friendship.objects.create(user=self.user, friend=self.friend)
        try:
            Friendship.objects.create(user=self.user, friend=self.friend)
        except Exception as e:
            logging.error('Error occurred while creating duplicate friendship: %s', e)
            self.fail('Duplicate friendship was not prevented')

    def test_users_api_missing_fields(self):
        data = {"email": "incomplete@example.com"}
        res = self.client.post(reverse("users api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing fields", res.json().get("error", ""))

    from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import logging
from django.core.exceptions import ValidationError
import json

from .models import (
    User, Restaurant, Cuisine, Allergy, Reservation, Review,
    Chosen, ChosenCuisine, ChosenAllergy, Friendship,
    Wishlist, WishlistItem, WishlistShare
)

class ExtendedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass", email="user1@example.com")
        self.friend = User.objects.create_user(username="user2", password="pass", email="user2@example.com")
        self.cuisine = Cuisine.objects.create(name="Greek", description="Mediterranean style")
        self.allergy = Allergy.objects.create(name="Peanuts", description="Nut allergy")
        self.restaurant = Restaurant.objects.create(
            name="Taverna",
            cuisine=self.cuisine,
            rating=4,
            seats_available=20,
            location="Seaside",
            user=self.user
        )
        self.restaurant.allergys.add(self.allergy)
        self.wishlist = Wishlist.objects.create(name="Try Soon", owner=self.user)
        self.review = Review.objects.create(
            name="Great food",
            restaurant=self.restaurant,
            rating=5,
            food_rating=5,
            service_rating=4,
            ambience_rating=5,
            description="Excellent place",
            user=self.user,
            date=timezone.now()
        )

    def test_invalid_user_email(self):
        user = User.objects.create_user(
            username="invalid_email_user",
            email="invalid-email",  # No '@' but still allowed in model
            password="pass"
        )
        self.assertEqual(user.email, "invalid-email")

    def test_negative_reservation_people(self):
        reservation = Reservation(
        user=self.user,
        restaurant=self.restaurant,
        reservation_time=timezone.now(),
        number_of_people=-1,
        status=0,
        special_requests="Window"
        )
        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_models_str(self):
        self.assertEqual(str(self.allergy), "Peanuts")
        self.assertEqual(str(self.review), "Taverna")
        self.assertEqual(str(self.restaurant), "Taverna")
        self.user.first_name = "user1"
        self.user.last_name = "test"
        self.user.save()
        self.assertEqual(str(self.user), "user1 test")

    def test_friendship_creation(self):
        friend = Friendship.objects.create(user=self.user, friend=self.friend)
        self.assertEqual(friend.friend.username, "user2")

    def test_chosen_items(self):
        Chosen.objects.create(user=self.user, restaurant=self.restaurant)
        ChosenCuisine.objects.create(user=self.user, cuisine=self.cuisine)
        ChosenAllergy.objects.create(user=self.user, allergy=self.allergy)
        self.assertEqual(Chosen.objects.count(), 1)
        self.assertEqual(ChosenCuisine.objects.count(), 1)
        self.assertEqual(ChosenAllergy.objects.count(), 1)

    def test_wishlist_item_and_share(self):
        WishlistItem.objects.create(wishlist=self.wishlist, restaurant=self.restaurant, owner=self.user)
        WishlistShare.objects.create(wishlist=self.wishlist, user=self.friend, can_edit=True)
        self.assertEqual(WishlistItem.objects.count(), 1)
        self.assertEqual(WishlistShare.objects.count(), 1)

    def test_users_api_post(self):
        data = {
            "first_name": "Anna", "last_name": "Smith", "email": "anna@ex.com",
            "date_of_birth": "2000-01-01", "password": "secret"
        }
        res = self.client.post(reverse("users api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 201)

    def test_user_api_put_delete(self):
        update = {"first_name": "Updated"}
        res = self.client.put(reverse("user api", args=[self.user.id]), json.dumps(update), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        res = self.client.delete(reverse("user api", args=[self.user.id]))
        self.assertIn(res.status_code, [200, 204])

    def test_recommendation_api(self):
        data = {
            "allergys": [self.allergy.id],
            "cuisines": [self.cuisine.id]
        }
        res = self.client.post(reverse("recommend restaurants"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("restaurants", res.json())

    def test_share_wishlist(self):
        data = {"shared_with": [self.friend.id]}
        res = self.client.put(reverse("share_wishlist", args=[self.wishlist.id]), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)

    def test_review_as_dict(self):
        data = self.review.as_dict()
        self.assertEqual(data["restaurant"], self.restaurant.name)
        self.assertEqual(data["user"]["first_name"], self.user.first_name)

    def test_reservation_api_crud(self):
        self.client.login(username="user1", password="testpass")
        self.client.force_login(self.user)

        data = {
            "user_id": self.user.id,
            "restaurant_id": self.restaurant.id,
            "reservation_time": timezone.now().isoformat(),
            "number_of_people": 2,
            "status": 0,
            "special_requests": "Quiet table"
        }
        res = self.client.post(reverse("reservations api"), json.dumps(data), content_type="application/json")
        print("API Response:", res.content)
        self.assertEqual(res.status_code, 200)

        reservation_id = res.json().get("id")

        # Update
        update = {"number_of_people": 4}
        res = self.client.put(reverse("reservation api", args=[reservation_id]), json.dumps(update), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # Delete
        res = self.client.delete(reverse("reservation api", args=[reservation_id]))
        self.assertEqual(res.status_code, 204)

    def test_review_api_crud(self):
        # Create
        data = {
            "restaurant_id": self.restaurant.id,
            "user_id": self.user.id,
            "name": "Decent",
            "rating": 4,
            "food_rating": 4,
            "service_rating": 4,
            "ambience_rating": 3,
            "description": "Good overall"
        }
        res = self.client.post(reverse("reviews api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        review_id = res.json().get("id")

        # Update
        update = {"rating": 5}
        res = self.client.put(reverse("review api", args=[review_id]), json.dumps(update), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # Delete
        res = self.client.delete(reverse("review api", args=[review_id]))
        self.assertEqual(res.status_code, 204)

   
    def test_owner_can_only_delete_their_wishlist(self):
        # Try deleting as someone else
        self.client.force_login(self.friend)
        res = self.client.delete(reverse("wishlist api", args=[self.wishlist.id]))
        self.assertIn(res.status_code, [403, 401])

    

    def test_prevent_duplicate_friendships(self):
        logging.info('Testing prevent duplicate friendships')
        Friendship.objects.create(user=self.user, friend=self.friend)
        try:
            Friendship.objects.create(user=self.user, friend=self.friend)
        except Exception as e:
            logging.error('Error occurred while creating duplicate friendship: %s', e)
            self.fail('Duplicate friendship was not prevented')

    def test_users_api_missing_fields(self):
        data = {"email": "incomplete@example.com"}
        res = self.client.post(reverse("users api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing fields", res.json().get("error", ""))

########
    def test_restaurant_as_dict_and_str(self):
        data = self.restaurant.as_dict()
        self.assertEqual(data["name"], "Taverna")
        self.assertEqual(str(self.restaurant), "Taverna")

    def test_user_as_dict(self):
        data = self.user.as_dict()
        self.assertEqual(data["username"], "user1")
        self.assertIn("email", data)

    def test_chosen_as_dict(self):
        chosen = Chosen.objects.create(user=self.user, restaurant=self.restaurant)
        self.assertEqual(chosen.as_dict()["restaurant"], self.restaurant.id)

    def test_reservation_as_dict(self):
        reservation = Reservation.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            reservation_time=timezone.now(),
            number_of_people=3,
            status=0,
            special_requests="Corner table"
        )
        self.assertEqual(reservation.as_dict()["number_of_people"], 3)

    def test_protected_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("reservations api"))
        self.assertIn(response.status_code, [302, 403, 401])

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("user logout"))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("user login"), res.url)


   
    def test_chosen_allergy_api(self):
        data = {
            "user_id": self.user.id,
            "allergy_id": self.allergy.id
        }
        res = self.client.post(reverse("chosenAllergys api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        chosen_id = res.json()["id"]
        delete = self.client.delete(reverse("chosenAllergy api", args=[chosen_id]))
        self.assertEqual(delete.status_code, 204)

    def test_share_wishlist_post(self):
        data = {"shared_with": [self.friend.id]}
        res = self.client.put(reverse("share_wishlist", args=[self.wishlist.id]), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.json())

    def test_wishlist_share_str_and_uniqueness(self):
        WishlistShare.objects.create(wishlist=self.wishlist, user=self.friend, can_edit=False)
        share = WishlistShare.objects.get(wishlist=self.wishlist, user=self.friend)
        expected_str = f"{self.friend.username} access to {self.wishlist.name}"
        self.assertEqual(str(share), expected_str)

    def test_wishlist_str_and_as_dict(self):
        wishlist = Wishlist.objects.create(name="My List", owner=self.user)
        data = wishlist.as_dict()
        self.assertEqual(str(wishlist), "My List")
        self.assertIn("shared_with", data)

    def test_wishlist_item_as_dict(self):
        item = WishlistItem.objects.create(wishlist=self.wishlist, restaurant=self.restaurant, owner=self.user)
        data = item.as_dict()
        self.assertEqual(data["restaurant"], self.restaurant.name)
 
    def test_chosen_cuisine_crud(self):
        data = {
            "user_id": self.user.id,
            "cuisine_id": self.cuisine.id
        }
        res = self.client.post(reverse("chosenCuisines api"), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        chosen_id = res.json()["id"]
        delete = self.client.delete(reverse("chosenCuisine api", args=[chosen_id]))
        self.assertEqual(delete.status_code, 204)

    def test_update_invalid_reservation(self):
        data = {"status": 1}
        res = self.client.put(reverse("reservation api", args=[999]), json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 404)

    def test_login_view_success(self):
        response = self.client.post(reverse("user login"), {
            "username": "user1",
            "password": "pass"
        })
        self.assertEqual(response.status_code, 302)

   