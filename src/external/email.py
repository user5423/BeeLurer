import asyncio
from datetime import datetime, timedelta
from collections import namedtuple
# from email.message import EmailMessage
# import aiosmtplib


from dataclasses import dataclass, field

@dataclass
class incidentReport:
    senderIP: str
    baitIP: str
    baitService: str
    baitPort: str
    exitRelayIP: str
    exitRelayMD: str
    baitSetupTS: str
    baitCatchTS: str
    rawRequest: str
    additionalInfo: str = field(default="None")


class _email:
    _htmlEmailPath = "src/external/email.html"
    _textEmailPath = "src/external/email.txt"

    def __init__(self, *args, **kwargs) -> None:
        """Here we load the any startup secrets/configurations, and templates"""
        self._htmlEmailTemplate = self._loadString(_email._htmlEmailPath)
        self._textEmailTemplate = self._loadString(_email._textEmailPath)

    def _loadString(self, pathName: str) -> str:
        with open(pathName, "r") as infile:
            return infile.read()

    async def _templateReplace(self, templateString: str, incidentDescriptor: str) -> str:
        return templateString.format(
            senderIP = incidentDescriptor.senderIP,
            baitIP = incidentDescriptor.baitIP,
            baitService = incidentDescriptor.baitService,
            baitPort = incidentDescriptor.baitPort,
            exitRelayIP = incidentDescriptor.exitRelayIP,
            exitRelayMD = incidentDescriptor.exitRelayMD,
            baitSetupTS = incidentDescriptor.baitSetupTS,
            baitCatchTS = incidentDescriptor.baitCatchTS,
            rawRequest = incidentDescriptor.rawRequest,
            additionalInfo = incidentDescriptor.additionalInfo
        )


    async def sendEmail(self, incidentDescriptor: namedtuple) -> bool:
        """This will send an email about the suspicous exit relay"""
        textEmail = self._templateReplace(self._textEmailTemplate, incidentDescriptor)
        htmlEmail = self._templateReplace(self._htmlEmailTemplate, incidentDescriptor)
        return await self._sendEmail(textEmail, htmlEmail) 


    async def _sendEmail(self, textEmail: str, htmlEmail: str) -> bool:
        ...


async def main() -> None:
    em = _email()

    incident = incidentReport(senderIP="10.11.189.14", baitIP="10.11.189.98", baitService="ftp",
                                baitPort=21, exitRelayIP="10.11.182.22", exitRelayMD="...",
                                baitSetupTS=datetime.now(), baitCatchTS=datetime.now() + timedelta(seconds=4),
                                rawRequest="xxxx....xxxx")

    out = await em._templateReplace(em._htmlEmailTemplate, incident)
    print(out)

if __name__ == "__main__":
    asyncio.run(main())
