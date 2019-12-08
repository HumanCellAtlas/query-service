import enum


class PermissionTypeEnum(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"


class CellLineTypeEnum(enum.Enum):
    PRIMARY = "primary"
    IMMORTALIZED = "immortalized"
    STEM_CELL = "stem cell"
    STEM_CELL_DERIVED = "stem cell-derived"
    INDUCED_PLURIPOTENT = "induced pluripotent"
    SYNTHETIC = "synthetic"


class IsLivingEnum(enum.Enum):
    YES = "yes"
    NO = "no",
    UNKNOWN = "unknown",
    NOT_APPLICABLE = "not applicable"


class SexEnum(enum.Enum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class ExpressionTypeEnum(enum.Enum):
    pass


class FeatureTypeEnum(enum.Enum):
    pass


class ReadIndexEnum(enum.Enum):
    pass


class AccessionTypeEnum(enum.Enum):
    PROCESS = "PROCESS"


class AnnotationTypeEnum(enum.Enum):
    pass


class AnnotationSourceEnum(enum.Enum):
    pass


class AutolysisScoreEnum(enum.Enum):
    pass


class StorageMethodEnum(enum.Enum):
    pass


class PreservationMethodEnum(enum.Enum):
    pass


class NutritionalStateEnum(enum.Enum):
    pass


class BarcodeReadEnum(enum.Enum):
    pass


class RunTypeEnum(enum.Enum):
    pass


class ProcessConnectionTypeEnum(enum.Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    PROTOCOL = "PROTOCOL"


class VectorRemovalEnum(enum.Enum):
    pass


class NucleicAcidSourceEnum(enum.Enum):
    BULK_CELL = "bulk cell"
    SINGLE_CELL = "single cell"
    SINGLE_NUCLEUS = "single nucleus"
    BULK_NUCLEI = "bulk nuclei"
    MITOCHONDRIA = "mitochondria"
