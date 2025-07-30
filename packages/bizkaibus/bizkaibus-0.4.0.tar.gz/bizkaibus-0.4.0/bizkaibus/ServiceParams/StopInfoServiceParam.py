from bizkaibus.ServiceParams.BizkaibusServiceParam import BizkaibusServiceParam
from bizkaibus.const import _RESOURCE, STOP_INFO_SERVICE

class StopInfoServiceParam(BizkaibusServiceParam):

    def __init__(self):
        """Retrieve the parameters for the service."""

    def GetURL(self) -> str:
        return _RESOURCE + STOP_INFO_SERVICE