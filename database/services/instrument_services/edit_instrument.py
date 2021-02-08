from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, EntryDoesNotExistException
from database.models import Instrument
from database.services.in_app_service import InAppService
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.instrument_services.utils import handle_instrument_validation_error
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class EditInstrument(InAppService):

    def __init__(
            self,
            user_id,
            password,
            instrument_id,
            model_id,
            serial_number,
            comment=None
    ):
        self.instrument_id = instrument_id
        self.model_id = model_id
        self.serial_number = serial_number
        self.comment = comment
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        if self.model_id is None:
            raise RequiredFieldsEmptyException(object_type="instrument",
                                               required_fields_list=["model", "serial_number"])
        try:
            instrument = SelectInstruments(user_id=self.user.id, password=self.user.password,
                                           instrument_id=self.instrument_id) \
                .execute() \
                .get(id=self.instrument_id)
            try:
                model = SelectModels(user_id=self.user.id, password=self.user.password, model_id=self.model_id)\
                    .execute()\
                    .get(id=self.model_id)
                try:
                    if SelectInstruments(user_id=self.user.id, password=self.user.password, model_id=self.model_id,
                                         serial_number=self.serial_number)\
                            .execute()\
                            .exclude(id=self.instrument_id)\
                            .count() > 0:
                        raise FieldCombinationNotUniqueException(object_type="instrument", fields_list=["model", "serial_number"])
                    instrument.model = model
                    instrument.serial_number = self.serial_number
                    instrument.comment = self.comment
                    instrument.full_clean()
                    instrument.save()
                    return instrument
                except ValidationError as e:
                    handle_instrument_validation_error(e)
            except ObjectDoesNotExist:
                raise EntryDoesNotExistException("model", self.model_id)
        except ObjectDoesNotExist:
           raise EntryDoesNotExistException("instrument", self.instrument_id)
