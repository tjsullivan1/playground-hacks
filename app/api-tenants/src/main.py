import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

from pathlib import Path
from typing import Optional

from pydantic import BaseModel

import fastapi
import uuid
import uvicorn
import json
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

api = fastapi.FastAPI()

def configure_routing():
#    api.mount('/static', StaticFiles(directory='static'), name='static')
#    api.include_router(home.router)
#    api.include_router(rental_api.router)
    pass


def configure_cosmosdb():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    return client.get_database_client(DATABASE_ID)
    
def configure():
    configure_routing()

# Define a list of tenants
tenants = []

class TenantSubmittal(BaseModel):
    company_name: str
    person_name: str
    email: str
    building: str
    rent: float
    due_day: int
    pays_utilities: bool
    portion_electric: float
    portion_gas: float

class Tenant(TenantSubmittal):
    id: str


# Need to figure out a better way to do this:
COSMOS_DB = configure_cosmosdb()

def create_items(container, tenant: Tenant):
    print("Creating items in the container")

    container.create_item(body=tenant.dict())


@api.get("/")
async def root():
    return {"message": "Hello World"}

# GET all tenants
@api.get("/tenants")
async def get_tenants():
    container = COSMOS_DB.get_container_client(CONTAINER_ID)

    tenants = []
    # Get all tenants from CosmosDB
    # TODO: Add pagination
    tenants_raw = container.read_all_items(max_item_count=10)

    for tenant in tenants_raw:
        tenants.append(tenant)

    return tenants

# GET a single tenant by ID
@api.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    container = COSMOS_DB.get_container_client(CONTAINER_ID)

    # Get the tenant from CosmosDB
    tenant = container.read_item(item=tenant_id, partition_key=tenant_id)
    return tenant
    # return {"error": "Tenant not found"}


# DELETE a single tenant by ID
@api.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str):
    container = COSMOS_DB.get_container_client(CONTAINER_ID)

    # Get the tenant from CosmosDB
    tenant = container.delete_item(item=tenant_id, partition_key=tenant_id)
    return tenant
    # return {"error": "Tenant not found"}


# POST a new tenant
@api.post("/tenants")
async def create_tenant(tenant: TenantSubmittal):
    # Generate a new ID for the tenant
    new_id = str(uuid.uuid4())
    print(new_id)

    # Create a new Tenant object
    new_tenant = Tenant(id=new_id, **tenant.dict())
    print(new_tenant)

    # Add the tenant to CosmosDB
    container = COSMOS_DB.get_container_client(CONTAINER_ID)
    create_items(container, new_tenant)

    # Return the new tenant
    return new_tenant

if __name__ == '__main__':
    configure()
    uvicorn.run(api, port=8000, host='127.0.0.1')
else:
    configure()