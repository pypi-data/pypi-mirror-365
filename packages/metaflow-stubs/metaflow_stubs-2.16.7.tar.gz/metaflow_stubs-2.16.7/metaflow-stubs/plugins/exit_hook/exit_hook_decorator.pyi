######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.16.7                                                                                 #
# Generated on 2025-07-29T01:50:18.746346                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

