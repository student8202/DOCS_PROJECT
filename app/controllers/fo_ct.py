# app/controllers/fo_ct.py
from fastapi import HTTPException
from services.fo_sv import FOService

class FOController:
    @staticmethod
    def get_inhouse_list():
        try:
            data = FOService.get_inhouse_list_logic()
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
