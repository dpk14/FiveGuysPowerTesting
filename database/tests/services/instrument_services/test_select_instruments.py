from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from database.models import Model, Instrument
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels
from database.tests.services.service_test_utils import create_non_admin_user


class SelectModelsTestCase(TestCase):

    def test_select_all_instruments(self):
        user = create_non_admin_user()
        self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password).execute()
        if instruments.count() != 3:
            self.fail("selected wrong instruments")

    def test_select_model_by_instrument_id(self):
        user = create_non_admin_user()
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password, instrument_id=instrument.id).execute()
        if instruments.count() != 1 or instruments.get(id=instrument.id) != instrument:
            self.fail("selected wrong instrument")

    def test_select_model_by_serial_number(self):
        user = create_non_admin_user()
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password, serial_number=instrument2.serial_number).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument2.id) != instrument2 or \
                instruments.get(id=instrument3.id) != instrument3:
            self.fail("selected wrong instrument")

    def test_select_model_by_model_id(self):
        user = create_non_admin_user()
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password, model_id=instrument.model_id).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")

    def test_select_model_by_model_number(self):
        user = create_non_admin_user()
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password, model_number=model.model_number).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")

    def test_select_model_by_vendor(self):
        user = create_non_admin_user()
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password, vendor=model.vendor).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")

    def test_select_model_by_description(self):
        user = create_non_admin_user()
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(user_id=user.id, password=user.password, description=model.description).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")


    def create_3_instruments(self):
        user = create_non_admin_user()
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                             comment="comment", calibration_frequency=1)
        instrument = Instrument.objects.create(model=model, serial_number="serial_number")
        instrument2 = Instrument.objects.create(model=model, serial_number="serial_number2")
        model2 = Model.objects.create(vendor="vendor2", model_number="model_number2", description="description2",
                             comment="comment2", calibration_frequency=2)
        instrument3 = Instrument.objects.create(model=model2, serial_number="serial_number2")
        return instrument, instrument2, instrument3, model, model2
