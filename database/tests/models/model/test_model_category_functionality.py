from datetime import timedelta

from django.test import TestCase

from database.models.model import Model
from database.models.model_category import ModelCategory


class CreateModelCategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        c1 = ModelCategory.objects.create(name="Voltmeter")
        c2 = ModelCategory.objects.create(name="Multimeter")
        c3 = ModelCategory.objects.create(name='Oscilloscope')
        m1 = Model.objects.create(vendor="Fluke",
                                  model_number="86V",
                                  description="High Impedance Voltmeter",
                                  calibration_frequency=timedelta(days=90))
        m2 = Model.objects.create(vendor="Fluke",
                                  model_number="87M",
                                  description="Multimeter with temperature probes",
                                  calibration_frequency=timedelta(days=60))
        m3 = Model.objects.create(vendor="Fluke",
                                  model_number="901C",
                                  description="Portable oscilloscope",
                                  calibration_frequency=timedelta(days=30))
        m1.model_categories.set([c1])
        m2.model_categories.set([c1, c2])
        m3.model_categories.set([c3])
        m1.save()
        m2.save()
        m3.save()

    def test_single_model_for_category(self):
        queryset = ModelCategory.objects.get(name="Multimeter").model_list.all()
        expected_queryset = Model.objects.filter(vendor="Fluke", model_number="87M")
        self.assertEqual(f'{queryset}', f'{expected_queryset}')

    def test_multiple_models_for_category(self):
        queryset = ModelCategory.objects.get(name="Voltmeter").model_list.all()
        expected_queryset = Model.objects.filter(model_categories__name="Voltmeter")  # want this to be string
        self.assertEqual(f'{queryset}', f'{expected_queryset}')

    def test_create_model_with_existing_category(self):
        Model.objects.create(vendor="Agilent",
                             model_number="900C",
                             description="4 Input Oscilloscope",
                             calibration_frequency=timedelta(days=120),
                             model_categories=['Oscilloscope'],
                             calibration_mode='DEFAULT')
        created_model = Model.objects.get(vendor='Agilent')
        queryset = created_model.model_categories.all()
        expected_queryset = ModelCategory.objects.filter(name="Oscilloscope")
        self.assertEqual(f'{queryset}', f'{expected_queryset}')

    def test_create_model_with_multiple_existing_categories(self):
        Model.objects.create(vendor="Agilent",
                             model_number="99M",
                             description="Heavy Duty Multimeter",
                             calibration_frequency=timedelta(days=40),
                             model_categories=['Multimeter', 'Voltmeter'],
                             calibration_mode='DEFAULT')
        created_model = Model.objects.get(vendor='Agilent')
        queryset = created_model.model_categories.all()
        expected_queryset = ModelCategory.objects.filter(name__endswith="meter")
        self.assertEqual(f'{queryset}', f'{expected_queryset}')

    def test_create_model_with_new_category(self):
        Model.objects.create(vendor="Agilent",
                             model_number="57P",
                             description="DC Power Supply",
                             calibration_frequency=timedelta(days=365),
                             model_categories=['power_supply'],
                             calibration_mode='DEFAULT')
        created_model = Model.objects.get(vendor='Agilent')
        queryset = created_model.model_categories.all()
        expected_queryset = ModelCategory.objects.filter(name="power_supply")
        self.assertEqual(f'{queryset}', f'{expected_queryset}')

    def test_create_model_with_new_and_existing_categories(self):
        Model.objects.create(vendor="Agilent",
                             model_number="99M",
                             description="Heavy Duty Multimeter",
                             calibration_frequency=timedelta(days=40),
                             model_categories=['Multimeter', 'Voltmeter', 'Ammeter'],
                             calibration_mode='DEFAULT')
        created_model = Model.objects.get(vendor='Agilent')
        queryset = created_model.model_categories.all()
        expected_queryset = ModelCategory.objects.filter(name__endswith="meter")
        self.assertEqual(f'{queryset}', f'{expected_queryset}')
