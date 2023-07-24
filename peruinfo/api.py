from ninja import NinjaAPI
from .sunat.api import router as sunat_router

api = NinjaAPI()

api.add_router("/sunat", sunat_router)