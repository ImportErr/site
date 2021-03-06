from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase

from profiles.models import RestrictProcessing


class AnonymousUserProfilesTests(TestCase):
    """
    Scenario:
        - Single user in the database
        - Anonymous User visits the site
        - accesses profile detail view for known user
        - accesses profile detail view for unknown user
        - accesses profile deletion view for known user
        - accesses profile deletion view for unknown user
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='testpassword')
        cls.social_account = SocialAccount.objects.create(
            uid=190,
            user=cls.user,
            extra_data={'guild': None}
        )

    def test_detail_known_user_status_200(self):
        resp = self.client.get(reverse("profiles:detail", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 200)

    def test_detail_unknown_user_status_404(self):
        resp = self.client.get(reverse("profiles:detail", kwargs={"pk": 214}))
        self.assertEqual(resp.status_code, 404)

    def test_update_known_user_status_403(self):
        resp = self.client.get(reverse("profiles:update", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 403)

        resp = self.client.post(reverse("profiles:update", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 403)

    def test_update_unknown_user_status_404(self):
        resp = self.client.get(reverse("profiles:update", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(reverse("profiles:update", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)

    def test_delete_known_user_status_403(self):
        resp = self.client.get(reverse("profiles:delete", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 403)

        resp = self.client.post(reverse("profiles:delete", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 403)

    def test_delete_unknown_user_status_404(self):
        resp = self.client.get(reverse("profiles:delete", kwargs={"pk": 214}))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(reverse("profiles:delete", kwargs={"pk": 214}))
        self.assertEqual(resp.status_code, 404)


class GuestUserProfilesTests(TestCase):
    """
    Scenario:
        - Guest User visits the site
        - Another user in the database
        - accesses profile detail view for known user
        - accesses profile detail view for unknown user
        - accesses profile deletion view for known user
        - accesses profile deletion view for unknown user
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='testpassword')
        cls.social_account = SocialAccount.objects.create(
            uid=1231,
            user=cls.user,
            extra_data={'guild': None}
        )
        cls.original_user = User.objects.create_user('testdatabaseuser', password='testpassword')
        cls.original_user_socialacc = SocialAccount.objects.create(
            uid=120391,
            user=cls.original_user,
            extra_data={'guild': None}
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_detail_unknown_user_status_404(self):
        resp = self.client.get(reverse("profiles:detail", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)

    def test_get_update_own_profile_status_200(self):
        resp = self.client.get(reverse("profiles:update", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 200)

    def test_update_unowned_profile_status_403(self):
        kwargs = {"pk": self.original_user_socialacc.uid}

        resp = self.client.get(reverse("profiles:update", kwargs=kwargs))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse("profiles:update", kwargs=kwargs))
        self.assertEqual(resp.status_code, 403)

    def test_update_unknown_user_status_404(self):
        resp = self.client.get(reverse("profiles:update", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(reverse("profiles:update", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)

    def test_get_delete_view_for_self_status_200(self):
        resp = self.client.get(reverse("profiles:delete", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 200)

    def test_delete_unknown_user_status_404(self):
        resp = self.client.get(reverse("profiles:delete", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(reverse("profiles:delete", kwargs={"pk": 42}))
        self.assertEqual(resp.status_code, 404)


class RestrictProcessingTests(TestCase):
    """
    Scenario:
        - anonymous user accesses the site
        - visits the profile of a user with `restrict_processing` set
        - visits the restrict processing update view of the user
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='testpassword')
        restrict_processing_obj = RestrictProcessing.objects.get(user=cls.user)
        restrict_processing_obj.restrict_processing = True
        restrict_processing_obj.save()
        cls.social_account = SocialAccount.objects.create(
            uid=42,
            user=cls.user,
            extra_data={'guild': None}
        )

    def test_detail_returns_403(self):
        resp = self.client.get(reverse("profiles:detail", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 403)


class UserProfileDeletionTest(TestCase):
    """
    Scenario:
        - user visits the site
        - deletes their own profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='testpassword')
        cls.social_account = SocialAccount.objects.create(
            uid=109231,
            user=cls.user,
            extra_data={'guild': None}
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_user_can_delete_own_profile(self):
        resp = self.client.get(reverse("profiles:delete", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse("profiles:delete", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('home:index'))

        self.assertIsNone(User.objects.filter(id=self.user.id).first())


class UserProfileUpdateTest(TestCase):
    """
    Scenario:
        - user visits the site
        - updates their own profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='testpassword')
        cls.social_account = SocialAccount.objects.create(
            uid=12931,
            user=cls.user,
            extra_data={'guild': None}
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_user_can_update_own_profile(self):
        resp = self.client.get(reverse("profiles:update", kwargs={"pk": self.social_account.uid}))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(
            reverse("profiles:update", kwargs={"pk": self.social_account.uid}),
            data={'restrict_processing': True}
        )
        self.assertEqual(resp.status_code, 302)
        restrict_processing_object = RestrictProcessing.objects.get(user=self.user)
        self.assertTrue(restrict_processing_object.restrict_processing)


class MemberProfileRestrictProcessingTest(TestCase):
    """
    Scenario:
        - user with restrict processing enabled visits the site
        - visits their own profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('testuser', password='testpassword')
        cls.social_account = SocialAccount.objects.create(
            uid=123091,
            user=cls.user,
            extra_data={'guild': None}
        )
        restrict_processing_obj = RestrictProcessing.objects.get(user=cls.user)
        restrict_processing_obj.restrict_processing = True
        restrict_processing_obj.save()

    def setUp(self):
        self.client.force_login(self.user)

    def test_can_visit_own_profile(self):
        resp = self.client.get(reverse('profiles:detail', kwargs={'pk': self.social_account.uid}))
        self.assertEqual(resp.status_code, 200)
