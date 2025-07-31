from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class WebAuthorization(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebAuthorization`.

    Details:
        - Layer: ``135``
        - ID: ``-0x59070bae``

    Parameters:
        hash: ``int`` ``64-bit``
        bot_id: ``int`` ``64-bit``
        domain: ``str``
        browser: ``str``
        platform: ``str``
        date_created: ``int`` ``32-bit``
        date_active: ``int`` ``32-bit``
        ip: ``str``
        region: ``str``
    """

    __slots__: List[str] = ["hash", "bot_id", "domain", "browser", "platform", "date_created", "date_active", "ip", "region"]

    ID = -0x59070bae
    QUALNAME = "types.WebAuthorization"

    def __init__(self, *, hash: int, bot_id: int, domain: str, browser: str, platform: str, date_created: int, date_active: int, ip: str, region: str) -> None:
        self.hash = hash  # long
        self.bot_id = bot_id  # long
        self.domain = domain  # string
        self.browser = browser  # string
        self.platform = platform  # string
        self.date_created = date_created  # int
        self.date_active = date_active  # int
        self.ip = ip  # string
        self.region = region  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        bot_id = Long.read(data)
        
        domain = String.read(data)
        
        browser = String.read(data)
        
        platform = String.read(data)
        
        date_created = Int.read(data)
        
        date_active = Int.read(data)
        
        ip = String.read(data)
        
        region = String.read(data)
        
        return WebAuthorization(hash=hash, bot_id=bot_id, domain=domain, browser=browser, platform=platform, date_created=date_created, date_active=date_active, ip=ip, region=region)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Long(self.bot_id))
        
        data.write(String(self.domain))
        
        data.write(String(self.browser))
        
        data.write(String(self.platform))
        
        data.write(Int(self.date_created))
        
        data.write(Int(self.date_active))
        
        data.write(String(self.ip))
        
        data.write(String(self.region))
        
        return data.getvalue()
