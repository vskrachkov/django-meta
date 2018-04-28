from django.test import TestCase

# Create your tests here.
from meta_magic.models import Author, ModelsInfo


class MyTestCase(TestCase):
    def test_models(self):
        model = Author()
        model.name = 'Some name'
        model.save()
        m = ModelsInfo.get_model(model.__class__.__name__)
        print(m)