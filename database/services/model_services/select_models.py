from database.models import Model
from database.services.in_app_service import InAppService
from database.services.service import Service


class SelectModels(InAppService):

    def __init__(
            self,
            user_id,
            password,
            model_id=None,
            vendor=None,
            model_number=None,
            description=None,
            calibration_frequency=None,
            num_per_page=None,
            page_num=None
    ):
        self.id = model_id
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.calibration_frequency = calibration_frequency
        super().__init__(user_id=user_id, password=password, admin_only=False)

    def execute(self):
        models = Model.objects.all()
        models = models if self.id is None else models.filter(id=self.id)
        models = models if self.vendor is None else models.filter(vendor=self.vendor)
        models = models if self.model_number is None else models.filter(model_number=self.model_number)
        models = models if self.description is None else models.filter(description=self.description)
        models = models if self.calibration_frequency is None else models.filter(calibration_frequency=self.calibration_frequency)
        return models



