from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaPoll(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0xf94e5f1``

    Parameters:
        poll: :obj:`Poll <pyeitaa.raw.base.Poll>`
        correct_answers (optional): List of ``bytes``
        solution (optional): ``str``
        solution_entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
    """

    __slots__: List[str] = ["poll", "correct_answers", "solution", "solution_entities"]

    ID = 0xf94e5f1
    QUALNAME = "types.InputMediaPoll"

    def __init__(self, *, poll: "raw.base.Poll", correct_answers: Optional[List[bytes]] = None, solution: Optional[str] = None, solution_entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.poll = poll  # Poll
        self.correct_answers = correct_answers  # flags.0?Vector<bytes>
        self.solution = solution  # flags.1?string
        self.solution_entities = solution_entities  # flags.1?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        poll = TLObject.read(data)
        
        correct_answers = TLObject.read(data, Bytes) if flags & (1 << 0) else []
        
        solution = String.read(data) if flags & (1 << 1) else None
        solution_entities = TLObject.read(data) if flags & (1 << 1) else []
        
        return InputMediaPoll(poll=poll, correct_answers=correct_answers, solution=solution, solution_entities=solution_entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.correct_answers is not None else 0
        flags |= (1 << 1) if self.solution is not None else 0
        flags |= (1 << 1) if self.solution_entities is not None else 0
        data.write(Int(flags))
        
        data.write(self.poll.write())
        
        if self.correct_answers is not None:
            data.write(Vector(self.correct_answers, Bytes))
        
        if self.solution is not None:
            data.write(String(self.solution))
        
        if self.solution_entities is not None:
            data.write(Vector(self.solution_entities))
        
        return data.getvalue()
