######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.16.7                                                                                 #
# Generated on 2025-07-29T01:50:18.738314                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

class NotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    ...

