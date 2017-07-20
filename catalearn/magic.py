
from .server_connector import ServerConnector
from .local_params import get_local_vars
from .gpu_module_finder import find_required_imports
import dill
import sys

def run_in_cloud(cell, connector, namespace):

    gpu_hash, gpu_ip, ws_port = connector.contact_server()

    if (gpu_hash is None or gpu_ip is None or ws_port is None):
        return

    local_vars = get_local_vars(cell, namespace)
    imports, unused_vars = find_required_imports(cell, local_vars)

    for var in unused_vars:
        del local_vars[var]

    uploads = {}
    uploads['cell'] = cell
    uploads['env'] = local_vars
    uploads['imports'] = imports

    with open('uploads.pkl', 'wb') as file:
        dill.dump(uploads, file)

    connector.upload_params_magic(gpu_ip, gpu_hash)
    outUrl = connector.stream_output(gpu_ip, gpu_hash, ws_port)

    if outUrl is None:
        return 

    result = connector.get_return_object(outUrl)
    return result
    