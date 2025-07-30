"""Support for Bizkaibus, Biscay (Basque Country, Spain) Bus service."""

import xml.etree.ElementTree as ET
import json
import aiohttp

from bizkaibus.Model.BizkaibusArrival import BizkaibusArrival
from bizkaibus.Model.BizkaibusArrivalTime import BizkaibusArrivalTime
from bizkaibus.Model.BizkaibusLine import BizkaibusLine
from bizkaibus.Model.BizkaibusTimetable import BizkaibusTimetable
from bizkaibus.ServiceParams.BizkaibusServiceParam import BizkaibusServiceParam
from bizkaibus.ServiceParams.LineItineraryServiceParam import LineItineraryServiceParam
from bizkaibus.ServiceParams.LinesInTownServiceParam import LinesInTownServiceParam
from bizkaibus.ServiceParams.TimetableServiceParam import TimetableServiceParam
from bizkaibus.ServiceParams.StopInfoServiceParam import StopInfoServiceParam
from typing import Any, Optional

class BizkaibusAPI:
    """The class for handling the data retrieval."""

    def __init__(self, stop: str):
        """Initialize the data object."""
        self.stop = stop
        
    async def TestConnection(self) -> bool: 
        """Test the API."""
        timetableParam = TimetableServiceParam(self.stop)
        result = await self.__getRequest(timetableParam)
        return result is not None
    
    async def GetLinesOnStop(self) -> list[BizkaibusLine]:
        """Retrieve the information of a bus on stop."""

        stopInfoParam = StopInfoServiceParam()
        result = await self.__getRequest(stopInfoParam)

        if result is None:
            return []

        root = result['Consulta']

        provincia = ''
        municipio = ''
        stop_Id = ''

        for parada in root['Paradas']:

            stop_Id = parada['CODIGOREDUCIDOPARADA']

            if stop_Id == self.stop:
                provincia = parada['PROVINCIA']
                municipio = parada['MUNICIPIO']
                break

        if stop_Id != self.stop:
            return []

        timetableParam = LinesInTownServiceParam(provincia, municipio)
        result = await self.__getRequest(timetableParam)
        if result is None:
            return []

        root = result['Consulta']
 
        lines = {}

        for line in root['Lineas']:
            route = line['NumeroRuta']
            line_Id = line['CodigoLinea']
            direction = line['Sentido']

            if line_Id in lines:
                continue

            itinerary = LineItineraryServiceParam(line_Id, route, direction)

            result2 = await self.__getRequest(itinerary)
            if result2 is None:
                continue
            root2 = result2['Consulta']

            for stops in root2['Paradas']:
                if stops['PR_CODRED'] == self.stop:
                    lines[line_Id] = BizkaibusLine(line_Id, root2['Descripcion'])
                    break

        return list(lines.values())

    async def GetTimetable(self) -> Optional[BizkaibusTimetable]:
        """Retrieve the information of a stop arrivals."""
        return await self.__getTimetable()

    async def GetNextArrivals(self, line: str) -> Optional[BizkaibusArrival]:
        """Retrieve the information of a bus on stop."""
        timetable = await self.__getTimetable()

        if timetable is None or not timetable.arrivals or line not in timetable.arrivals:
            return None
        else:
            return timetable.arrivals[line]
        
    async def __getTimetable(self) -> Optional[BizkaibusTimetable]:
        timetableParam = TimetableServiceParam(self.stop)
        result = await self.__getRequest(timetableParam)
        if result is None:
            return None

        root = ET.fromstring(result['Resultado'])

        stopName = root.find('DenominacionParada')
        stopNameStr = stopName.text if stopName is not None else None
        timetable = BizkaibusTimetable(self.stop, stopNameStr)

        for childBus in root.findall("PasoParada"):
            linea_elem = childBus.find('linea')
            ruta_elem = childBus.find('ruta')
            e1_elem = childBus.find('e1')
            e2_elem = childBus.find('e2')

            route = linea_elem.text if linea_elem is not None else None
            routeName = ruta_elem.text if ruta_elem is not None else None
            minutos1 = e1_elem.find('minutos') if e1_elem is not None else None
            time1 = minutos1.text if minutos1 is not None else None
            minutos2 = e2_elem.find('minutos') if e2_elem is not None else None
            time2 = minutos2.text if minutos2 is not None else None

            if (routeName is not None and time1 is not None and route is not None):
                if time2 is None:
                     stopArrival = BizkaibusArrival(BizkaibusLine(route, routeName), 
                    BizkaibusArrivalTime(int(time1)))
                else:
                    stopArrival = BizkaibusArrival(BizkaibusLine(route, routeName), 
                    BizkaibusArrivalTime(int(time1)), BizkaibusArrivalTime(int(time2)))

                timetable.arrivals[stopArrival.line.id] = stopArrival

        return timetable
            
    async def __getRequest(self, service_param: BizkaibusServiceParam) -> Optional[dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            params = service_param.BuildParams()
            url = service_param.GetURL()
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None

                strJSON = await response.text()
                strJSON = strJSON[1:-2].replace('\'', '"')
                result = json.loads(strJSON)

                if str(result['STATUS']) != 'OK':
                    return None
                
                return result
