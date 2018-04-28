from django.test import TestCase

from meta_magic.models import Author


class MyTestCase(TestCase):
    def test_models(self):
        model = Author()
        model.name = 'Some name'
        model.save()
        ModelsInfo = model.app_meta.ModelsInfo
        print(ModelsInfo)
