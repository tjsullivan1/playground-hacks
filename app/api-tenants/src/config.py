import os

settings = {
    'host': os.environ.get('COSMOS_DB_URL'),
    'master_key': os.environ.get('COSMOS_DB_KEY'),
    'database_id': os.environ.get('COSMOS_DATABASE', 'invoicer'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'tenants'),
}