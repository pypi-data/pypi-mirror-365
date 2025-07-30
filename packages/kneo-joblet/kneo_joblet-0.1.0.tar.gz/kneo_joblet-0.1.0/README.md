# EOCube Functions

EOCube functions is a fork of the [KNeo Joblet Function](https://gitlab.terrasigna.com/kneo/kneo-joblet) project.

EOCube Functions aims to be a simple runtime for invoking serverless KNative functions. 
It handles:
- HTTP Based functions: handling liveness, routing and CloudEvent extraction
- Batch Jobs: integration with the KNative JobSink
- Authentication using OIDC for Broker interaction

The base (kneo-functions) library is inspired by `parliament-functions` and aims to be a dropin replacement.


Developers only need to write a function which takes a `Context` object as a sole parameter.

## 🙏 Acknowledgements

This work is funded by a grant of the  European Space Angency. Project KNeo.

This work is partially supported by a grant of the Ministry of Research, Innovation and Digitization, 
CCCDI - UEFISCDI, project number **PN-IV-P6-6.3-SOL-2024-2-0248**, within PNCDI IV.
