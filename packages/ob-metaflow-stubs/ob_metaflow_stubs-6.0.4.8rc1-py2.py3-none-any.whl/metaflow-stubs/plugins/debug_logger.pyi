######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.16.5.1+obcheckpoint(0.2.4);ob(v1)                                                    #
# Generated on 2025-07-28T18:04:46.435123                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.event_logger


class DebugEventLogger(metaflow.event_logger.NullEventLogger, metaclass=type):
    @classmethod
    def get_worker(cls):
        ...
    ...

class DebugEventLoggerSidecar(object, metaclass=type):
    def __init__(self):
        ...
    def process_message(self, msg):
        ...
    ...

