import csv
import sys

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        if self.__check_model_object():
            with open('../data/ingredients.csv') as csv_file:
                dict_reader = csv.DictReader(csv_file)
                for row in dict_reader:
                    row: dict = row
                    Ingredient.objects.create(**row)
                csv_file.close()
            return f'Данные успешно загружены в {Ingredient.__name__}.'
        else:
            sys.exit()

    @staticmethod
    def __check_model_object():
        if Ingredient.objects.exists():
            answer = input(
                f'В модели {Ingredient.__name__} уже есть данные.\n'
                'Продолжение операции может привести к конфликтам.\n'
                'Продолжить? y/n: '
            )
            if answer.lower() != 'y':
                return False
        return True
