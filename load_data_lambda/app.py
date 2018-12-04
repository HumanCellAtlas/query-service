from query.lambdas.load_data.load_data import LoadData
from query.lib.common.logging import get_logger

logger = get_logger(__name__)


def load_data(event, context):
    LoadData().query_service_data_load(event, context)
