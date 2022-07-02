import json
import os
import subprocess
from typing import Optional
# import argparse

## NOTE: Docker has a limitation where you are unable to publish container ports during runtime
## NOTE: Therefore, we have to modify the dockerfile before we run it

## NOTE: This setup.py might have additional verification functionality later, but for now no

from ruamel.yaml import YAML

yaml = YAML()

## TODO: Add argument parsing to provide multiple functionality
##       --> Add ability to do execute several tasks including: 
#              `startup`
#              `validate definition`
#              `validate deployment`
##       --> Add ability to manipulate the paths for the compose and service definition files
## TODO: Add output in real-time from `docker-compose ... up`
##       ==> currently subprocess only outputs after the process has finished executing
##       --> We want output (with content thresholding (e.g. debug, info, medium))
## TODO: Provide validation of filesand define stricter requirments for:
##       --> docker-compose.base.yml
##       --> docker-compose.bait.yml
##       --> service-definitions.json
## TODO: Provide testing for the live deployment to see if running "correctly"
##       ==> This idea needs to be fleshed out a bit later on


class DockerSetup:
    baitServiceDir = os.path.join("baitServices", "default-httpservice")
    baseServiceDir = os.path.join("./")

    baitServiceComposePath = os.path.join(baitServiceDir, "docker-compose.bait.yml")
    baitServiceDefinitionPath = os.path.join(baitServiceDir, "service-definitions.json")
    baseServiceComposePath = os.path.join(baseServiceDir, "docker-compose.base.yml")

    runtimeBaitServicePath = os.path.join(baitServiceDir, "docker-compose.runtime-bait.yml")
    runtimeBaseServicePath = os.path.join(baseServiceDir, "docker-compose.runtime-base.yml")

    baitNetwork = "baitservice-network"


    def __init__(self) -> None:
        self.baseService: Optional[dict] = None
        self.baitService: Optional[dict] = None
        self._loadComposeFiles()


    def _loadComposeFiles(self) -> None:
        print("Loading docker-compose files")
        with open(DockerSetup.baseServiceComposePath, "r") as infile:
            self.baseService = yaml.load(infile)
        
        with open(DockerSetup.baitServiceComposePath, "r") as infile:
            self.baitService = yaml.load(infile)


    def run(self):
        ## Using the service-definitions, we override the base compose file
        self._overrideBaseComposeFile()
        ## Using our standard networks, we override the bait compose file
        self._overrideBaitComposeFile()

        ## Validate the merged file to see whether it is valid and fits the network restrictions that we want to impose
        self._validateBaseComposeFile()
        self._validateOverrideComposeFile()

        ## Run the runtime compose files
        self._run()


    def _validateBaseComposeFile(self):
        ## TODO: Here we need to perform validation on the base compose file
        return True


    def _validateOverrideComposeFile(self):
        ## TODO: Here we need to perform validation on the bait compose files
        return True


    def _overrideBaseComposeFile(self) -> None:
        with open(DockerSetup.baitServiceDefinitionPath) as infile:
            serviceDefinitions = json.load(infile)

        proxyports = [f"{service['port']}:{service['port']}" for service in serviceDefinitions]
        self.baseService["services"]["beelurer-proxy"]["ports"] = proxyports


    def _overrideBaitComposeFile(self) -> None:
        ## We want to remove port publishing in the bait service
        print("Overriding/Correcting docker-compose.bait.yml file...")
        for service in self.baitService["services"].keys():
            ## Removing published ports (TODO: Consider moving this into validation)
            if len(self.baitService["services"][service].get("ports", [])) > 0:
                del self.baitService["services"][service]["ports"]

            ## Adding the neccessary network (TODO: Consider making checks in validation)
            if not (self.baitService["services"][service].get("networks") and \
                DockerSetup.baitNetwork in self.baitService["services"][service]["networks"]):
                self.baitService["services"][service]["networks"].append(DockerSetup.baitNetwork)


    def _run(self):
        print("Creating runtime docker-compose files...")
        with open(DockerSetup.runtimeBaseServicePath, "w+") as outfile:
            yaml.dump(self.baseService, outfile)

        with open(DockerSetup.runtimeBaitServicePath, "w+") as outfile:
            yaml.dump(self.baitService, outfile)

        print("Running docker-compose.yml files...")
        process = subprocess.Popen(["docker-compose", 
                                "-f", DockerSetup.runtimeBaseServicePath, 
                                "-f", DockerSetup.runtimeBaitServicePath,
                                "up", "-d"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        
        print("Finished running docker-compose setup")


def main() -> None:
    DockerSetup().run()

if __name__ == "__main__":
    main()