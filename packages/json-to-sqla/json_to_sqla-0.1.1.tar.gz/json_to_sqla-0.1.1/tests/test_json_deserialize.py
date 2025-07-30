from __future__ import annotations

from json_deserialize import JsonSerializer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import Optional
from base_sqlalchemy import Base
from external_models import MChildChild

def test_deserialize_int():
    j = """
    {
        "id": 123
    }
    """
    
    class MInt(Base):
        __tablename__ = "mint"
        id: Mapped[int] = mapped_column(String, primary_key=True)

        def __eq__(self, other: MInt): # type: ignore
            return self.id == other.id

    assert JsonSerializer[MInt]().deserialize_string(j) == MInt(id=123)

    
def test_deserialize_str():
    j = """
    {        "id": "123"
    }
    """
    
    class MStr(Base):
        __tablename__ = "mstr"
        id: Mapped[str] = mapped_column(String, primary_key=True)

        def __eq__(self, other: MStr): # type: ignore
            return self.id == other.id

    assert JsonSerializer[MStr]().deserialize_string(j) == MStr(id="123")

def test_deserialize_bool():
    j = """
    {
        "id": true
    }
    """
    
    class MBool(Base):
        __tablename__ = "mbool"
        id: Mapped[bool] = mapped_column(String, primary_key=True)

        def __eq__(self, other: MBool): # type: ignore
            return self.id == other.id

    assert JsonSerializer[MBool]().deserialize_string(j) == MBool(id=True)

def test_deserialize_to_snake_case():
    j = """
    {
        "id": "1",
        "givenName": "S1",
        "givenNameName": "S2"
    }
    """
    
    class MSnake(Base):
        __tablename__ = "msnake"
        id: Mapped[bool] = mapped_column(String, primary_key=True)
        given_name: Mapped[str]
        given_name_name: Mapped[str]

        def __eq__(self, other: MSnake): # type: ignore
            return self.id == other.id and self.given_name == other.given_name

    expected = MSnake(id="1", given_name="S1", given_name_name="S2")
    result = JsonSerializer[MSnake](camelCase_to_snake_case=True).deserialize_string(j)
    assert result == expected

class MChild(Base):
    __tablename__ = "mchild"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    mchildchild_id: Mapped[str] = mapped_column(ForeignKey("mchildchild.id"))
    mchildchild: Mapped[MChildChild] = relationship()
    def __eq__(self, other: MChild): # type: ignore
        return self.id == other.id and self.mchildchild_id == other.mchildchild_id and self.mchildchild == other.mchildchild

class MParent(Base):
    __tablename__ = "mparent"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    mchild_id: Mapped[str] = mapped_column(ForeignKey("mchild.id"))
    mchild: Mapped[MChild] = relationship()
    def __eq__(self, other: MParent): # type: ignore
        return self.id == other.id and self.mchild_id == other.mchild_id and self.mchild == other.mchild
    
def test_deserialize_nested():
    j = """
    {
        "id": "1",
        "mchild": {
            "id": "2",
            "mchildchild": {
                "id": "3"
            }
        }
    }
    """
            
    res = JsonSerializer[MParent]().deserialize_string(j)
    print(f"{res.mchild.mchildchild.id=}")
    # assert 1 == 0
    assert res == MParent(id="1", mchild_id="2", mchild=MChild(id="2", mchildchild_id="3", mchildchild=MChildChild(id="3")))

def test_deserialize_optional_missing():
    j = """
    {
        "id": 123
    }
    """
    
    class MOptionalMissing(Base):
        __tablename__ = "moptionalmissing"
        id: Mapped[int] = mapped_column(String, primary_key=True)
        optional: Mapped[Optional[str]]

        def __eq__(self, other: MOptionalMissing): # type: ignore
            return self.id == other.id

    assert JsonSerializer[MOptionalMissing]().deserialize_string(j) == MOptionalMissing(id=123)

def test_deserialize_optional_present():
    j = """
    {
        "id": 123,
        "optional": "456"
    }
    """
    
    class MOptionalPresent(Base):
        __tablename__ = "moptionalpresent"
        id: Mapped[int] = mapped_column(String, primary_key=True)
        optional: Mapped[Optional[str]]

        def __eq__(self, other: MOptionalPresent): # type: ignore
            return self.id == other.id

    expected = MOptionalPresent(id=123, optional="456")
    result = JsonSerializer[MOptionalPresent]().deserialize_string(j)
    assert result == expected

def test_deserialize_list():
    j = """
    [
        {
            "id": "1"
        },
        {
            "id": "2"
        }
    ]
    """

    class MElementInList(Base):
        __tablename__ = "melementinlist"
        id: Mapped[str] = mapped_column(String, primary_key=True)

        def __eq__(self, other: MElementInList): # type: ignore
            return self.id == other.id
        
    expected = [MElementInList(id="1"), MElementInList(id="2")]
    result = JsonSerializer[MElementInList]().deserialize_string_to_many(j)

    assert len(result) == len(expected)
    for i, _ in enumerate(result):
        assert result[i] == expected[i] 