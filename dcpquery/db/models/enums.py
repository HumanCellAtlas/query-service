import enum


class AnnotationTypeEnum(enum.Enum):
    pass


class AnnotationSourceEnum(enum.Enum):
    pass


class NormothermicRegionalPerfusionEnum(enum.Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class IsLivingEnum(enum.Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not applicable"


class VectorRemovalEnum(enum.Enum):  # refactor into more general enum, can also use for protocol.channel.multiplexed
    YES = "yes"
    NO = "no"
    UNKONWN = "unknown"


class IschemicTemperatureEnum(enum.Enum):
    WARM = "warm"
    COLD = "cold"


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


class OrganDonationDeathTypeEnum(enum.Enum):
    DCD = "Donation after circulatory death (DCD)"
    DBD = "Donation after brainstem death (DBD)"


class SexEnum(enum.Enum):
    FEMALE = "female"
    MALE = "male"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class WellQualityEnum(enum.Enum):
    OK = "OK"
    CONTROL_2C = "control, 2-cell well"
    CONTROL_EMPTY = "control, empty well"
    LOW_QUALITY_CELL = "low quality cell"


class ReadIndexEnum(enum.Enum):
    READ_1 = "read1"
    READ_2 = "read2"
    INDEX_1 = "index1"
    INDEX_2 = "index2"
    SINGLE_ENDED_NON_INDEXED = "single-end, non-indexed"


class ExpressionTypeEnum(enum.Enum):
    TPM = "TPM"
    COUNT = "COUNT"


class AccessionTypeEnum(enum.Enum):
    PROCESS = "PROCESS"
    INSDC_STUDY = "INSDC_STUDY"
    INSDC_PROJECT = "INSDC_PROJECT"
    INSDC_RUN = "INSDC_RUN"
    GEO_SERIES = "GEO_SERIES"


class AutolysisScoreEnum(enum.Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"


class StorageMethodEnum(enum.Enum):
    AMBIENT = "ambient temperature"
    CUT_SLIDE = "cut slide"
    FRESH = "fresh"
    FROZEN_NEG_70C = "frozen at -70C"
    FROZEN_NEG_80C = "frozen at -80C"
    FROZEN_NEG_150C = "frozen at -150C"
    LIQUID_NITROGEN = "frozen in liquid nitrogen"
    FROZEN_VAPOR_PHASE = "frozen in vapor phase"
    PARAFFIN = "paraffin block"
    FNALATER_4C = "RNAlater at 4C"
    RNALATER_25C = "RNAlater at 25C"
    RNALATER_NEG_20C = "RNAlater at -20C"


class PreservationMethodEnum(enum.Enum):
    CRYO_LN_DT = "cryopreservation in liquid nitrogen (dead tissue)"
    CRTO_DI_DT = "cryopreservation in dry ice (dead tissue)"
    CRYO_LN_LC = "cryopreservation of live cells in liquid nitrogen"
    CRYO_OTHER = "cryopreservation, other"
    FORMALIN_UNBUFF = "formalin fixed, unbuffered"
    FORMALON_BUFF = "formalin fixed, buffered"
    FROMALIN_PARAFFIN = "formalin fixed and paraffin embedded"
    HYPOTHERMIC_2_to_8C = "hypothermic preservation media at 2-8C"
    FRESH = "fresh"


class NutritionalStateEnum(enum.Enum):
    NORMAL = "normal"
    FASTING = "fasting"
    FT_REMOVED = "feeding tube removed"


class PrimerEnum(enum.Enum):
    POLY_DT = "poly-dT"
    RANDOM = "random"


class BarcodeReadEnum(enum.Enum):
    READ_1 = "Read 1"
    READ_2 = "Read 2"
    I7_INDEX = "i7 Index"
    I5_INDEX = "i5 Index"


class AnalysisRunTypeEnum(enum.Enum):
    RUN = "run"
    COPY_FORWARD = "copy-forward"


class ProcessConnectionTypeEnum(enum.Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    PROTOCOL = "PROTOCOL"


class NucleicAcidSourceEnum(enum.Enum):
    BULK_CELL = "bulk cell"
    SINGLE_CELL = "single cell"
    SINGLE_NUCLEUS = "single nucleus"
    BULK_NUCLEI = "bulk nuclei"
    MITOCHONDRIA = "mitochondria"


class EndBiasEnum(enum.Enum):
    A3PT = "3 prime tag"
    A3PEB = "3 prime end bias"
    A5PT = "5 prime tag"
    A5PEB = "5 prime end bias"
    FL = "full length"


# **************************************
class LibraryStrandEnum(enum.Enum):
    FIRST = "first"
    SECOND = "second"
    UNSTRANDED = "unstranded"
    NOT_PROVIDED = "not provided"


class MycoplasmaTestingMethodEnum:
    DIRECTED_STAIN = "Direct DNA stain"
    INDIRECT_STAIN = "Indirect DNA stain"
    BROTH_AND_AGAR = "Broth and agar culture"
    PCR = "PCR"
    NESTED_PCR = "Nested PCR"
    ELISA = "ELISA"
    AUTORADIOGRAPHY = "Autoradiography"
    IMMUNOSTAINING = "Immunostaining"
    CELL_BASED_ASSAY = "Cell-based assay"
    MICROBIO_ASSAY = "Microbiological assay"


class TestResultEnum(enum.Enum):  # use for cell viability, mycoplasma testing,
    PASS = "pass"
    FAIL = "fail"


class ISPCMethodEnum(enum.Enum):
    LENTIVIRUS = "lentivirus"
    SENDAI_VIRUS = "sendai virus"
    GUN_PARTICLE = "Gun particle"
    PB_TRANS = "piggyBac transposon"
    MIRNA_VIRAL = "miRNA viral"
    ADENOVIRUS = "adenovirus"
    CRE_LOXP = "cre-loxP"
    PLASMID = "plasmid"
    RETROVIRAL = "retroviral"


class FeederLayerTypeEnum(enum.Enum):
    FEEDER_FREE = "feeder-free"
    FD_JK1C = "feeder-dependent, JK1 feeder cells"
    FD_SNLC = "feeder-dependent, SNL 76/7 feeder cells"
    FD_HMSC = "feeder-dependent, human marrow stromal cells"
    FD_BEFC = "feeder-dependent, bovine embryonic fibroblast cells"
    FD_MEFC = "feeder-dependent, mouse embryonic fibroblast cells"
    FD_MFSC = "feeder-dependent, mouse fibroblast STO cells"
    FD_MBMSC = "feeder-dependent, mouse bone marrow stromal cells"
    FC_MYSDEC = "feeder-dependent, mouse yolk sac-derived endothelial cells"
    FD_HFFC = "feeder-dependent, human foreskin fibroblast cells"
    FD_HNFC = "feeder-dependent, human newborn fibroblast cells"
    FD_HFLFC = "feeder-dependent, human fetal lung fibroblast cells"
    FD_HUEC = "feeder-dependent, human uterine endometrial cells"
    FD_HBPC = "feeder-dependent, human breast parenchymal cells"
    FD_HEFC = "feeder-dependent, human embryonic fibroblast cells"
    FD_HASC = "feeder-dependent, human adipose stromal cells"
    FD_HAEC = "feeder-dependent, human amniotic epithelial cells"
    FD_HPFC = "feeder-dependent, human placental fibroblast cells"
    FD_HUCSC = "feeder-dependent, human umbilical cord stromal cells"
    FD_HFMC = "feeder-dependent, human fetal muscle cells"
    FD_HFSC = "feeder-dependent, human fetal skin cells"
    FD_HFLSC = "feeder-dependent, human fetal liver stromal cells"
    FD_HFTEC = "feeder-dependent, human fallopian tubal epithelial cells"
    FD_HAMC = "feeder-dependent, human amniotic mesenchymal cells"
