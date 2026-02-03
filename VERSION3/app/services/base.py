from ..db.tables import get_table

class BaseService:
    def __init__(self,table_name:str="playbook_core"):
        self.table=get_table(table_name)

    def _extract_capacity(self,response:dict)->float:
        return response.get("ConsumedCapacity",{}).get("CapacityUnits",0)