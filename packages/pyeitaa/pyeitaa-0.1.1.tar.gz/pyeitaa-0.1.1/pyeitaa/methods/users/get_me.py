import pyeitaa
from ...raw.types.user import User
from ...raw.types.input_user_self import InputUserSelf
from ...raw.functions.users.get_full_user import GetFullUser


class GetMe:
    async def get_me(
        self: "pyeitaa.Client",
        check_connection: bool = True
    ) -> User:
        r = await self.invoke(
            GetFullUser(
                id=InputUserSelf()
            ),
            check_connection=check_connection
        )

        return r.user
