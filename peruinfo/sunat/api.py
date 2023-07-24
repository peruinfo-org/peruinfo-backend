from typing import List
from ninja import Router, Query
from ninja.pagination import paginate

from .models import Padron
from .schemas import PadronOutSchema, PadronFilterSchema

router = Router()


@router.get("/padron", response=List[PadronOutSchema], by_alias=True)
@paginate()
def get_padron_list(request, filters: PadronFilterSchema = Query(...)):
    qs = filters.filter(Padron.objects.all())
    return qs


@router.get("/padron/{ruc}", response=PadronOutSchema, by_alias=True)
def get_padron(request, ruc: str):
    return Padron.objects.get(ruc=ruc)
