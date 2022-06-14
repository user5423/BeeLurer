import json
import asyncio
from datetime import datetime, timedelta
from collections import namedtuple

from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dataclasses import dataclass, field

import aiosmtplib


## TODO: Add exception handling
## TODO: Move incidentReport to other directory
## TODO: Setup gmail account
## TODO: Setup secure credential loading system
## TODO: Write tests

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
	_htmlEmailPath = "src/external/emailTemplate.html"
	_textEmailPath = "src/external/emailTemplate.txt"
	## NOTE: Temp solution
	_authPath = "secrets/emailAuth.json"

	def __init__(self, hostname: str = "smtp.gmail.com", port: int = 465, tls: bool = True) -> None:
		"""Here we load the any startup secrets/configurations, and templates"""
		self._htmlEmailTemplate = self._loadString(_email._htmlEmailPath)
		self._textEmailTemplate = self._loadString(_email._textEmailPath)
		
		## We'll be sending messages with gmail and using their smtp relay
		self.smtp_hostname = hostname
		self.smtp_port = port
		self.use_tls = tls
		
		## We load our email credentials
		self.username, self.password = self.loadCredentials()
		
		## Create an smtp client object for later use
		self.smtp_client = aiosmtplib.SMTP(self.smtp_hostname, self.smtp_port, self.use_tls)


	def loadCredentials(self) -> tuple[str, str]:
		with open(_email._authPath, "r") as infile:
			out = json.load(infile)
		return out["username"], out["password"]


	def _loadString(self, pathName: str) -> str:
		with open(pathName, "r") as infile:
			return infile.read()


	def _templateReplace(self, templateString: str, incidentDescriptor: str) -> str:
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
		emailMessage = self._prepareEmailMessage(textEmail, htmlEmail)
		return await self._sendEmail(emailMessage) 


	def _prepareEmailMessage(self, textEmail: str, htmlEmail: str) -> bool:
		## https://realpython.com/python-send-email/#sending-fancy-emails
		message = MIMEMultipart("alternative")

		message["From"] = "beelurer@example.com"
		message["To"] = "test-2bcad6@test.mailgenius.com"
		message["Subject"] = "Potentially malicious exit relay detected"

		textPart = MIMEText(textEmail, "plain")
		htmlPart = MIMEText(htmlEmail, "html")

		message.attach(textPart)
		message.attach(htmlPart)

		return message


	async def _sendEmail(self, emailMessage: EmailMessage) -> bool:
		async with self.smtp_client:
			## await self.smtp_client.starttls()
			return await aiosmtplib.send_message(emailMessage, 
												port = self.smtp_port,
												hostname = self.smtp_hostname)
		
		## TODO: Check whether it is neccessary to manually exec `starttls()` or is 
		## this handled by the context manager


async def main() -> None:
	em = _email()

	incident = incidentReport(senderIP="10.11.189.14", baitIP="10.11.189.98", baitService="ftp",
								baitPort=21, exitRelayIP="10.11.182.22", exitRelayMD="...",
								baitSetupTS=datetime.now(), baitCatchTS=datetime.now() + timedelta(seconds=4),
								rawRequest="xxxx....xxxx")

	out = await(em.sendEmail(incident))

if __name__ == "__main__":
	asyncio.run(main())
