from typing import NamedTuple

import asyncio
import aiomysql


## NOTE: There is a functional requirement that I have left out for now regarding
## the database. This is the synchronization/unification between the fake service
## authentication store method (e.g. database, file, etc.) and our database.

## NOTE: Don't worry about this for now (as this shouldn't affect the methods defined
## in the interface below)


class _database:
    def __init__(self, *args, **kwargs) -> None:
        """Here we setup the aiomysql database cursor object"""
        ...

    async def createBaitTrap(self, credentials: NamedTuple) -> None:
        """This uses the provided credentials to create a bait trap in the database"""
        ...

    async def hasBaitCredentials(self, credentials: NamedTuple) -> bool:
        """This checks whether the bait credentials exist in the database"""
        ...

    async def logBaitRequest(self, credentials: NamedTuple, request: NamedTuple) -> None:
        """This logs a bait request into the database. The request will likely have
        a few common fields (e.g. ip-address, port, protocol), but then will likely
        have protocol specific fields."""
        ## NOTE: Implement this method last
        ...
    
    async def close(self) -> None:
        """This closes any open connections to the database"""
        ...


def main() -> None:
    ...

if __name__ == "__main__":
    main()
