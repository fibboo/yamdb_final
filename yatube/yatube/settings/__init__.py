from .base import *

if DEBUG is True:
    from .local import *
else:
    from .prod import *
