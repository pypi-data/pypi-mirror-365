######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.16.5.1+obcheckpoint(0.2.4);ob(v1)                                                    #
# Generated on 2025-07-28T18:04:46.470107                                                            #
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

