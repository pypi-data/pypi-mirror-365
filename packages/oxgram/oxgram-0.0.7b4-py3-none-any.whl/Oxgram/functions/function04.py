from ..exceptions import InvalidKey
from ..exceptions import Negativemode
from ..exceptions import InvalidReply
from ..exceptions import Accessblocked
from ..exceptions import CancelledTask
from ..exceptions import LimitedMessage
from ..exceptions import ExpiredPremium
#=====================================================================

class BMessage:

    async def get01(message, errors=None):
        if message:
            raise CancelledTask(errors)

    async def get02(message, errors=None):
        if not message:
            raise CancelledTask(errors)

    async def get03(blocked, errors=None):
        if blocked:
            raise Accessblocked(errors)

    async def get04(blocked, errors=None):
        if not blocked:
            raise Accessblocked(errors)

    async def get05(taskuid, storage, errors=None):
        if taskuid in storage:
            raise CancelledTask(errors)

    async def get06(taskuid, storage, errors=None):
        if taskuid not in storage:
            raise CancelledTask(errors)

    async def get07(taskuid, storage, errors=None):
        if taskuid in storage:
            raise CancelledTask(errors)
        storage.append(taskuid)

    async def get08(taskuid, storage, errors=None):
        if taskuid not in storage:
            raise CancelledTask(errors)
        storage.append(taskuid)

    async def get09(message, incoming, errors=None):
        if message.startswith(incoming):
            raise CancelledTask(errors)

    async def get10(message, incoming, errors=None):
        if message.endswith(incoming):
            raise CancelledTask(errors)

    async def get11(message, incoming, errors=None):
        if not message.startswith(incoming):
            raise CancelledTask(errors)

    async def get12(message, incoming, errors=None):
        if not message.endswith(incoming):
            raise CancelledTask(errors)

    async def get21(message, status=False, errors=None):
        if message is status:
            raise InvalidReply(errors)

    async def get22(message, status=False, errors=None):
        if message == status:
            raise InvalidReply(errors)

    async def get23(message, status=False, errors=None):
        if message is status:
            raise Negativemode(errors)

    async def get24(message, status=False, errors=None):
        if message == status:
            raise Negativemode(errors)

    async def get30(minimum, maximum=1024, errors=None):
        if minimum < maximum:
            raise ExpiredPremium(errors)

    async def get31(minimum, maximum=1024, errors=None):
        if minimum > maximum:
            raise LimitedMessage(errors)

    async def get32(minimum, maximum=1024, errors=None):
        if len(minimum) > maximum:
            raise LimitedMessage(errors)

    async def get33(message, skiplist, errors=None):
        for command in message.split():
            if command in skiplist:
                raise InvalidKey(command)

#=====================================================================
