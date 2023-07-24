from ninja import ModelSchema, FilterSchema, Field
from typing import Optional

from peruinfo.utils import to_camel
from .models import Padron


class PadronOutSchema(ModelSchema):
    
    class Config:
        model = Padron
        model_fields = "__all__"
        alias_generator = to_camel
        allow_population_by_field_name = True


class PadronFilterSchema(FilterSchema):
    search: Optional[str] = Field(q='razon_social__search')
 
    