import importlib

from django.db.models import DateField, ExpressionWrapper, F, OuterRef, Subquery
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from database.filters import InstrumentFilter, ModelFilter
from database.models.instrument import CalibrationEvent
from database.models.instrument_category import InstrumentCategory
from database.serializers.calibration_event import ApprovalDataSerializer, \
    CalibrationEventSerializer, \
    CalibrationRetrieveSerializer, InstrumentForCalibrationEventSerializer, InstrumentsPendingApprovalSerializer
from database.serializers.instrument import InstrumentBulkImportSerializer, InstrumentCalibratorSerializer, \
    InstrumentRetrieveSerializer, InstrumentSerializer
from database.serializers.model import *
from database.services.export_services.export_instruments import ExportInstrumentsService
from database.services.export_services.export_models import ExportModelsService
from database.services.import_instruments import ImportInstruments
from database.services.import_models import ImportModels
from database.services.table_enums import MaxInstrumentTableColumnNames, MaxModelTableColumnNames, \
    MinInstrumentTableColumnNames, \
    ModelTableColumnNames


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CategoryViewSet(viewsets.ModelViewSet):
    filterset_fields = [CategoryEnum.NAME.value]
    search_fields = [CategoryEnum.NAME.value]
    ordering_fields = [CategoryEnum.NAME.value]

    def get_serializer_class(self):
        name = self.__class__.__name__.replace('ViewSet', '')
        model = name.replace('Category', '').lower()
        m = importlib.import_module(f'database.serializers.{model}')
        if self.action == 'retrieve':
            return getattr(m, f'{name}RetrieveSerializer')
        return getattr(m, f'{name}Serializer')


class ModelCategoryViewSet(CategoryViewSet):
    queryset = ModelCategory.objects.all()


class InstrumentCategoryViewSet(CategoryViewSet):
    queryset = InstrumentCategory.objects.all()


class ModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Model.objects.all()
    filterset_class = ModelFilter
    pagination_class = SmallResultsSetPagination
    search_fields = [
        ModelEnum.VENDOR.value,
        ModelEnum.MODEL_NUMBER.value,
        ModelEnum.DESCRIPTION.value,
        'model_categories__name',
    ]
    ordering_fields = [
        ModelEnum.VENDOR.value,
        ModelEnum.MODEL_NUMBER.value,
        ModelEnum.DESCRIPTION.value,
        ModelEnum.CALIBRATION_FREQUENCY.value,
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModelRetrieveSerializer
        return ModelSerializer

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(['get'], detail=False)
    def vendors(self, request):
        model_number = request.query_params.get('model_number')
        return Response(Model.objects.vendors(model_number))

    @action(['get'], detail=False)
    def model_numbers(self, request):
        vendor = request.query_params.get('vendor')
        return Response(Model.objects.model_numbers(vendor=vendor))

    @action(['get'], detail=False)
    def export(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return ExportModelsService().execute(queryset)

    @action(['get'], detail=False)
    def all(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        return Response(serializer(self.get_queryset(), many=True).data)


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instruments to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    filterset_class = InstrumentFilter
    pagination_class = SmallResultsSetPagination
    search_fields = [
        'model__' + ModelEnum.VENDOR.value,
        'model__' + ModelEnum.MODEL_NUMBER.value,
        'model__' + ModelEnum.DESCRIPTION.value,
        'model__model_categories__name',
        InstrumentEnum.SERIAL_NUMBER.value,
        'instrument_categories__name',
        InstrumentEnum.ASSET_TAG_NUMBER.value,
    ]
    ordering_fields = [
        'model__' + ModelEnum.VENDOR.value,
        'model__' + ModelEnum.MODEL_NUMBER.value,
        'model__' + ModelEnum.DESCRIPTION.value,
        InstrumentEnum.SERIAL_NUMBER.value,
        'most_recent_calibration_date',
        'calibration_expiration_date',
        InstrumentEnum.ASSET_TAG_NUMBER.value,
    ]
    ordering = ['model__vendor', 'model__model_number', 'serial_number']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstrumentRetrieveSerializer
        elif self.action == 'calibrators':
            return InstrumentCalibratorSerializer
        elif self.action == 'calibration_certificate':
            return CalibrationRetrieveSerializer, InstrumentForCalibrationEventSerializer
        return InstrumentSerializer

    def get_queryset(self):
        sq = CalibrationEvent.objects.filter(instrument=OuterRef('pk')).filter(approval_data__approved=True).order_by('-date')
        expression = F('most_recent_calibration_date') + F('model__calibration_frequency')
        expiration = ExpressionWrapper(expression, output_field=DateField())
        qs = super().get_queryset().annotate(most_recent_calibration_date=Subquery(sq.values('date')[:1]))
        return qs.annotate(calibration_expiration_date=expiration)

    def recurse_calibration_event(self, calibration_event, calibration_serializer, instrument_serializer):
        if not calibration_event:
            return

        calibration_event_dict = calibration_serializer(calibration_event).data
        calibration_event_dict['calibration_expiration_date'] = \
            (calibration_event.date + calibration_event.instrument.model.calibration_frequency).date()

        index = 0
        for instrument in calibration_event.calibrated_with.all():
            calibration_event_dict['calibrated_with'][index] = \
                self.recurse_instrument(
                    instrument,
                    calibration_event.date,
                    calibration_serializer,
                    instrument_serializer
                )

            index += 1

        return calibration_event_dict

    def recurse_instrument(self, instrument, date, calibration_serializer, instrument_serializer):
        if not instrument:
            return

        instrument_dict = instrument_serializer(instrument).data
        calibration_event = CalibrationEvent.objects.find_calibration_event(instrument.pk, date)
        instrument_dict['calibration_event'] = \
            self.recurse_calibration_event(calibration_event, calibration_serializer, instrument_serializer)

        return instrument_dict

    @action(['get'], detail=False)
    def calibratable_asset_tag_numbers(self, request, *args, **kwargs):
        return Response(Instrument.objects.calibratable_asset_tag_numbers())

    @action(['get'], detail=False)
    def export(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return ExportInstrumentsService().execute(queryset)

    @action(['get'], detail=False)
    def all(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        queryset = self.filter_queryset(self.get_queryset())
        return Response(serializer(queryset, many=True).data)

    @action(['get'], detail=False)
    @permission_classes([IsAuthenticated])
    def asset_tag_numbers(self, request, *args, **kwargs):
        pks = request.query_params.get('pks').split(',')
        return Response(Instrument.objects.asset_tag_numbers(pks))

    @action(['get'], detail=True)
    def calibrators(self, request, pk=None, *args, **kwargs):
        """ Return all possible calibrators for given instrument """
        serializer = self.get_serializer_class()
        return Response(serializer(Instrument.objects.calibrators(Instrument.objects.get(pk=pk)), many=True).data)

    @action(['get'], detail=True)
    def calibration_certificate(self, request, pk=None, *args, **kwargs):
        """ Return calibration certificate for given instrument """
        c_e_s, i_s = self.get_serializer_class()
        calibration_event = CalibrationEvent.objects.find_valid_calibration_event(pk)
        return Response(self.recurse_calibration_event(calibration_event, c_e_s, i_s))


class ApprovalDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows approval data to be viewed or edited.
    """
    queryset = ApprovalData.objects.all()
    serializer_class = ApprovalDataSerializer


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calibration events to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    filter_backends = []

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CalibrationRetrieveSerializer
        elif self.action == 'pending_approval':
            return InstrumentsPendingApprovalSerializer
        return CalibrationEventSerializer

    @action(['get'], detail=False)
    def pending_approval(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        return Response(serializer(CalibrationEvent.objects.pending_approval(), many=True).data)


class ModelUploadView(APIView):
    parser_classes = [MultiPartParser, ]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.data['file']
        return ImportModels(file, ModelListSerializer, ModelTableColumnNames, MaxModelTableColumnNames).bulk_import()


class InstrumentUploadView(APIView):
    parser_classes = [MultiPartParser, ]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.data['file']
        return ImportInstruments(file, InstrumentBulkImportSerializer, MinInstrumentTableColumnNames,
                                 MaxInstrumentTableColumnNames, self.request.user).bulk_import()
