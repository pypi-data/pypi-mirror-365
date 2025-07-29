import pyonir
from backend import router

# Instantiate pyonir application
demo_app = pyonir.init(__file__)

# Install plugins
# demo_app.install_plugins(['ADD_PLUGIN_MODULE'])

# Generate static website
# demo_app.generate_static_website()

# Run server
demo_app.run(routes=router)
