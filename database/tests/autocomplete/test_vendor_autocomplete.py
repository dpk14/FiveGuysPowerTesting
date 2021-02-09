from database.models import EquipmentModel
from database.tests.test_utils import EndpointTestCase
from database.views import VendorAutoCompleteViewSet, EquipmentModelViewSet
from user_portal.models import PowerUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate


class VendorAutoCompleteTestCase(EndpointTestCase):
    def test_vendor_auto_complete_happy_case(self):
        EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        EquipmentModel.objects.create(vendor="vendor2", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        EquipmentModel.objects.create(vendor="vendor3", model_number="model_number", description="description",
                                      comment="comment", calibration_frequency=1)
        request = self.factory.get("http://127.0.0.1:8000/vendors?vendor=vend")
        force_authenticate(request, self.admin)
        view = VendorAutoCompleteViewSet.as_view()
        response = view(request)
        self.assertEquals(response.data, ['vendor', 'vendor2', 'vendor3'])