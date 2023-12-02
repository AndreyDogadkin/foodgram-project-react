import csv
import sys

from django.core.management.base import BaseCommand

from foodgram_backend.settings import BASE_DIR
from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    MODEL_PATH = ((Ingredient, 'data/ingredients.csv'), (Tag, 'data/tags.csv'))

    def handle(self, *args, **options):
        if self.__check_model_object():
            for model, path in self.MODEL_PATH:
                with open(BASE_DIR / path) as csv_file:
                    dict_reader = csv.DictReader(csv_file)
                    for row in dict_reader:
                        row: dict = row
                        model.objects.create(**row)
                    csv_file.close()
            return f'Данные успешно загружены.'
        else:
            sys.exit()

    def __check_model_object(self):
        models_with_data = []
        for model, _ in self.MODEL_PATH:
            if model.objects.exists():
                models_with_data.append(model.__name__)
        if models_with_data:
            answer = input(
                f'В {models_with_data} уже есть данные.\n'
                'Продолжение операции может привести к конфликтам.\n'
                'Продолжить? y/n: '
            )
            if answer.lower() != 'y':
                return False
        return True
