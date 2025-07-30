    
import asyncio
from bizkaibus.bizkaibusAPI import BizkaibusAPI


bizka = BizkaibusAPI('0252')
ok = asyncio.run(bizka.TestConnection())

if ok:
    result = asyncio.run(bizka.GetTimetable())
    print(result)
    result = asyncio.run(bizka.GetLinesOnStop())
    for line in result:
        print(line)
else:
    print("Connection failed")