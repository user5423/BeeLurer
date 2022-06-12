## Fake Service Design

### Introduction

**AIM**: We need to design a fake service design

**Previously**: We already have somewhat fleshed out the high-level system architecture design, which included a `client` and `proxy` component. These will most likely run concurrently within the same process (on different threads) or asynchronously)

**Currently**: We need to design the container architecture and submission process of containers/fake-services

### High-level container architecture

We have two containers which run:
1. The first container runs the `BeeLurer.py` (incl. `client` and `proxy` components)
2. The second container runs the fake service and services the requests that have been passed from the `proxy` to it. It should NOT have direct public access

**NOTE** It's excruciatingly important that the fake service container is hardened, in order to be increase difficulty of successful attacks.


### Container Networking Requirements

Here are the minimum requirements required for communications

1. `BeeLurer` container
    - `client` component 
        - Needs to be able to make high-level protocol requests
        - Make requests to external BeeLurer Database
    - `proxy` component
        - Receives/Responds to public requests
        - Passes/Relayes requests to `FakeService` **local** container
        - Make requests to external BeeLurer Database
2. `FakeService` container
    -  Receives/Responds to `BeeLurer` proxified requests

In this case, we need to configure the container networking:
1. `BeeLurer` and `FakeService` need to be able to communicate
2. `BeeLurer` has public access but `FakeService` does not

Research: https://docs.docker.com/network/

It seems that docker provides user-defined bridge networks where the containers inside the network have access to all of each others ports, but no access to the outside. We then publish the set of ports on the `BeeLurer` container that the fake service would have used, in order to pass through any traffic.

**TODO** Decide on exact configuration, and discuss high-level implementation details.


### `FakeService` container and program usage

- We can copy the likes of ExitMap in terms of reporting. I believe exitMap runners communicate with trusted community members who then investigate exit relays
- An important decision is deciding how configurable the `Fake Service` should be

#### Proposal 1: Submissions

A submission portal is provided where community members can submit fake services, which are then stored privately. Through some decided scheduling, we retire fake services, and replace them with new fake services from a submission backlog

Potential Issues/Resolutions

- **Security Issues**
    - **Upload Portal** - Allowing people to upload source code or binary files, can be a problem. We can offset this to a 3rd party managed storage service, but they will most likley have filetype restrictions.
    - Allowing people to submit container images and data could result in a pwned system before we even start scanning. Even if there's a manual review system in place, an adversary could submit something that looks harmless, but has a backdoor by using vulnerable software versions. Additionally, allowing control of the fakeservice image, could lead to breakout of the network isolation provided by the user-defined bridge. (There are so many issues with this)
    - Container images - These are likely to be significantly easier to detect security problems with as they are considerably shorter, easier to understand, and have excellent tools such as Snyk to scan for outdated packages - (does this handle poor system configurations)
    - Data - This is likely to be more difficult to detect problems with. Even if the code isn't malicious itself, it's possible that an adversary could submit code with vulnerable dependencies, that they can later exploit.
- **Increased Implementation Complexity** - 

**Proposal 1a: Restricted**

We consider restricting what is allowed to be uploaded via the submission portal. However, this only mitigates a prevalent surface attack area, which still exists. 

TODO: Consider if it is possible to come to a secure restricted submission system.



**Proposal 2: No Submission system**

The user instead inserts their own docker containers and source code. We provide a set of scanning scripts to try to detect incorrect / vulnerable setup of the `fakeService`.

- This is significantly easier for us to implement (for an MVP), and is pretty easy for us to pivot to an alternative system


Potential Issues/Resolutions
- Increased level of knowledge of containers. This can be mitigated by:
    - Reference dockerfiles and docker-compose files that are commented and dedicated for different stacks (e.g. one for WP, FTP, Drupal, etc.)
    - Interactive scripts that automate generation of the dockerfiles/dockercompose files. This requires in-depth knowledge of dockerfiles and compose in order to implement this successfully
- The runners of the system need to be trusted
    - but this was true for any reporting system.
    - In this case, we avoid the problem of volunteers running code that
    the adversary poisoned in the now removed submission process
    


### TODOs
- We need to reevaluate this document, and fill in any missing content, discussions, proposals and/or designs


