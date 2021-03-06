from enum import Enum


class ExportFileNames(Enum):
    INSTRUMENTS = "instruments.csv"
    MODELS = "models.csv"


class ModelTableColumnNames(Enum):
    VENDOR = "Vendor"
    MODEL_NUMBER = "Model-Number"
    DESCRIPTION = "Short-Description"
    COMMENT = "Comment"
    MODEL_CATEGORIES = "Model-Categories"
    LOAD_BANK_SUPPORT = "Load-Bank-Support"
    CALIBRATION_FREQUENCY = "Calibration-Frequency"


class InstrumentTableColumnNames(Enum):
    VENDOR = ModelTableColumnNames.VENDOR.value
    MODEL_NUMBER = ModelTableColumnNames.MODEL_NUMBER.value
    SERIAL_NUMBER = "Serial-Number"
    ASSET_TAG_NUMBER = "Asset-Tag-Number"
    COMMENT = "Comment"
    CALIBRATION_DATE = "Calibration-Date"
    CALIBRATION_COMMENT = "Calibration-Comment"
    INSTRUMENT_CATEGORIES = "Instrument-Categories"
