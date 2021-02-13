from datetime import timedelta

from rest_framework import serializers

from database.model_enums import EquipmentModelEnum, InstrumentEnum, CalibrationEventEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent
from user_portal.serializers import UserFieldsForCalibrationEventSerializer


class EquipmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [e.value for e in EquipmentModelEnum]


class InstrumentSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value, InstrumentEnum.SERIAL_NUMBER.value]


class EquipmentModelRetrieveSerializer(serializers.ModelSerializer):
    instruments = InstrumentSerialNumberSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentModel
        fields = [e.value for e in EquipmentModelEnum] + ['instruments']


class EquipmentModelForInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [EquipmentModelEnum.PK.value,
                  EquipmentModelEnum.VENDOR.value,
                  EquipmentModelEnum.MODEL_NUMBER.value,
                  EquipmentModelEnum.DESCRIPTION.value]


class CalibrationHistoryRetrieveSerializer(serializers.ModelSerializer):
    user = UserFieldsForCalibrationEventSerializer(many=False, read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value,
                  CalibrationEventEnum.USER.value,
                  CalibrationEventEnum.COMMENT.value]


class CalibrationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value]


class InstrumentRetrieveSerializer(serializers.ModelSerializer):
    calibration_history = CalibrationHistoryRetrieveSerializer(many=True, read_only=True)
    model = EquipmentModelForInstrumentSerializer(many=False, read_only=True)
    calibration_expiration = serializers.DateField()

    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum] + ['calibration_history', 'calibration_expiration']


class InstrumentListSerializer(serializers.ModelSerializer):
    calibration_history = serializers.SerializerMethodField()
    calibration_expiration = serializers.DateField()
    model = EquipmentModelForInstrumentSerializer(many=False, read_only=True)

    def get_calibration_history(self, obj):
        """Redefine calibration_history field to return only most recent calibration event"""
        try:
            query = CalibrationEvent.objects.filter(instrument=obj.pk).latest('date')
            serializer = CalibrationHistorySerializer(query, many=False, read_only=True)
            return serializer.data
        except CalibrationEvent.DoesNotExist:
            return None

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.MODEL.value,
                  'calibration_history',
                  'calibration_expiration']


class InstrumentSerializer(serializers.ModelSerializer):
    calibration_history = CalibrationHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.MODEL.value] + ['calibration_history']

    def to_representation(self, instance):
        return InstrumentListSerializer(instance).data


class CalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [EquipmentModelEnum.VENDOR.value]
