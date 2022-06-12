import asyncio
from email.message import EmailMessage

import aiosmtplib

class _email:
    _httpEmailTemplate = ""
    _textEmailTemplate = ""

    def __init__(self, *args, **kwargs) -> None:
        """Here we load the any startup secrets/configurations"""
        ...


    async def sendEmail(self) -> None:
        """This will send an email about the suspicous exit relay"""
        ...
    


def main() -> None:
    ...

if __name__ == "__main__":
    main()
