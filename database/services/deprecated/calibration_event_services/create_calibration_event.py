from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, EntryDoesNotExistException, CalibrationEventRequiredFieldsEmptyException
from database.models import Instrument, CalibrationEvent
from database.services.deprecated.calibration_event_services.select_calibration_events import SelectCalibrationEvents
from database.services.deprecated.calibration_event_services.utils import handle_calib_event_validation_error
from database.services.deprecated.in_app_service import InAppService
from database.services.deprecated.instrument_services.select_instruments import SelectInstruments
from database.services.deprecated.model_services import SelectModels
from database.services.service import Service


class CreateCalibrationEvent(InAppService):

    def __init__(
            self,
            user_id,
            password,
            instrument_id,
            date,
            comment=None
    ):
        self.instrument_id = instrument_id
        self.date = date
        self.comment = comment
        super().__init__(user_id=user_id, password=password, admin_only=False)

    def execute(self):
        if self.instrument_id is None:
            raise CalibrationEventRequiredFieldsEmptyException(date=self.date)
        try:
            instrument = SelectInstruments(user_id=self.user.id, password=self.user.password, instrument_id=self.instrument_id)\
                .execute()\
                .get(id=self.instrument_id)
            try:
                calibration_event = CalibrationEvent(instrument=instrument, user=self.user, date=self.date,
                                                       comment=self.comment)
                calibration_event.full_clean()
                calibration_event.save()
                return calibration_event
            except ValidationError as e:
                handle_calib_event_validation_error(e,
                                                    vendor=instrument.model.vendor,
                                                    model_number=instrument.model.model_number,
                                                    serial_number=instrument.serial_number,
                                                    date=self.date)
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("instrument", self.instrument_id)