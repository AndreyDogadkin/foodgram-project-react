import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from recipes.models import Tag, Ingredient
from users.models import Follow

User = get_user_model()


class TestsTags(APITestCase):

    FIRST_TAG_NAME = 'Завтрак'
    FIRST_TAG_ID = '1'
    FIRST_TAG_SLUG = 'breakfast'
    FIRST_TAG_COLOR = '#411d96'

    SECOND_TAG_NAME = 'Oбед'
    SECOND_TAG_ID = '2'
    SECOND_TAG_SLUG = 'lunch'
    SECOND_TAG_COLOR = '#411d97'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:tag-list')
        cls.url_detail = reverse('api:tag-detail',
                                 kwargs={'pk': cls.FIRST_TAG_ID})
        cls.tag_first = Tag.objects.create(id=cls.FIRST_TAG_ID,
                                           name=cls.FIRST_TAG_NAME,
                                           slug=cls.FIRST_TAG_SLUG,
                                           color=cls.FIRST_TAG_COLOR)
        cls.tag_second = Tag.objects.create(id=cls.SECOND_TAG_ID,
                                            name=cls.SECOND_TAG_NAME,
                                            slug=cls.SECOND_TAG_SLUG,
                                            color=cls.SECOND_TAG_COLOR)
        cls.tag_detail_response_data = {'id': 1, 'name': 'Завтрак',
                                        'color': '#411d96',
                                        'slug': 'breakfast'}
        cls.tag_list_response_data = [{'id': 1, 'name': 'Завтрак',
                                       'color': '#411d96',
                                       'slug': 'breakfast'},
                                      {'id': 2, 'name': 'Oбед',
                                       'color': '#411d97',
                                       'slug': 'lunch'}]

    def test_get_tags(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content),
                         self.tag_list_response_data)

    def test_get_tag_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.tag_detail_response_data)


class TestsIngredients(APITestCase):

    FIRST_INGREDIENT_NAME = 'Картошка'
    FIRST_INGREDIENT_ID = '1'
    FIRST_INGREDIENT_UNIT = 'кг'

    SECOND_INGREDIENT_NAME = 'Сахар'
    SECOND_INGREDIENT_ID = '2'
    SECOND_INGREDIENT_UNIT = 'г'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:ingredient-list')
        cls.url_detail = reverse(
            'api:ingredient-detail',
            kwargs={'pk': cls.FIRST_INGREDIENT_ID}
        )
        cls.tag_first = Ingredient.objects.create(
            id=cls.FIRST_INGREDIENT_ID,
            name=cls.FIRST_INGREDIENT_NAME,
            measurement_unit=cls.FIRST_INGREDIENT_UNIT
        )
        cls.tag_second = Ingredient.objects.create(
            id=cls.SECOND_INGREDIENT_ID,
            name=cls.SECOND_INGREDIENT_NAME,
            measurement_unit=cls.SECOND_INGREDIENT_UNIT
        )
        cls.tag_detail_response_data = {'id': 1, 'name': 'Картошка',
                                        'measurement_unit': 'кг'}
        cls.tag_list_response_data = [{'id': 1, 'name': 'Картошка',
                                       'measurement_unit': 'кг'},
                                      {'id': 2, 'name': 'Сахар',
                                       'measurement_unit': 'г'}]

    def test_get_ingredients(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content),
            self.tag_list_response_data
        )

    def test_get_ingredient_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.tag_detail_response_data)


class TestsFollowing(APITestCase):

    FIRST_USER_ID = 1
    FIRST_USER_EMAIL = 'user1@ya.ru'
    FIRST_USER_USERNAME = 'follower'
    FIRST_USER_FIRST_NAME = 'user1'
    FIRST_USER_LAST_NAME = 'user_first'

    SECOND_USER_ID = 2
    SECOND_USER_EMAIL = 'user2@ya.ru'
    SECOND_USER_USERNAME = 'following'
    SECOND_USER_FIRST_NAME = 'user2'
    SECOND_USER_LAST_NAME = 'user_second'

    @classmethod
    def setUpTestData(cls):
        cls.url_first = reverse(
            'api:foodgramuser-subscribe',
            kwargs={'pk': cls.FIRST_USER_ID}
        )
        cls.url_second = reverse(
            'api:foodgramuser-subscribe',
            kwargs={'pk': cls.SECOND_USER_ID}
        )
        cls.user = User.objects.create(
            id=cls.FIRST_USER_ID,
            username=cls.FIRST_USER_USERNAME,
            email=cls.FIRST_USER_EMAIL,
            first_name=cls.FIRST_USER_FIRST_NAME,
            last_name=cls.FIRST_USER_LAST_NAME
        )
        cls.following = User.objects.create(
            id=cls.SECOND_USER_ID,
            username=cls.SECOND_USER_USERNAME,
            email=cls.SECOND_USER_EMAIL,
            first_name=cls.SECOND_USER_FIRST_NAME,
            last_name=cls.SECOND_USER_LAST_NAME
        )
        cls.follow_obj = Follow.objects.create(
            user_id=cls.SECOND_USER_ID,
            following_id=cls.FIRST_USER_ID
        )
        cls.token_first = Token.objects.create(user_id=cls.FIRST_USER_ID)
        cls.token_second = Token.objects.create(user_id=cls.SECOND_USER_ID)

        cls.post_response_data = {'email': 'user2@ya.ru',
                                  'id': 2,
                                  'username': 'following',
                                  'first_name': 'user2',
                                  'last_name': 'user_second',
                                  'is_subscribed': True,
                                  'recipes': [],
                                  'recipes_count': 0}

    def test_post_del_follow(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_first.key
        )
        response = self.client.post(self.url_second)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            json.loads(response.content),
            self.post_response_data
        )

    def test_del_follow(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_second.key
        )
        response = self.client.delete(self.url_first)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
