Welcome to openpilot running on an headless Rpi 
======

[openpilot](http://github.com/commaai/openpilot) is an open source driving agent. 

This fork is a port to RPi (in progress...)
It runs without the can bus, panda and eon focussing on smaller vehicles.

Table of Contents
=======================

* [Community](#community)
* [Hardware](#hardware)
* [Supported Cars](#supported-cars)
* [Community Maintained Cars](#community-maintained-cars)
* [In Progress Cars](#in-progress-cars)
* [How can I add support for my car?](#how-can-i-add-support-for-my-car)
* [Directory structure](#directory-structure)
* [User Data / chffr Account / Crash Reporting](#user-data--chffr-account--crash-reporting)
* [Testing on PC](#testing-on-pc)
* [Contributing](#contributing)
* [Licensing](#licensing)

---

Community
------

openpilot is developed by [comma.ai](https://comma.ai/) 
 [Discord](https://discord.comma.ai).

Hardware
------

At the moment openpilot supports the [EON Dashcam DevKit](https://comma.ai/shop/products/eon-dashcam-devkit). A [panda](https://shop.comma.ai/products/panda-obd-ii-dongle) and a [giraffe](https://comma.ai/shop/products/giraffe/) are recommended tools to interface the EON with the car. We'd like to support other platforms as well.

Install openpilot on a neo device by entering ``https://openpilot.comma.ai`` during NEOS setup.

Supported Cars

How can I add support for my car?
------

If your car has adaptive cruise control and lane keep assist, you are in luck. Using a [panda](https://comma.ai/shop/products/panda-obd-ii-dongle/) and [cabana](https://community.comma.ai/cabana/), you can understand how to make your car drive by wire.

We've written guides for [Brand](https://medium.com/@comma_ai/how-to-write-a-car-port-for-openpilot-7ce0785eda84) and [Model](https://medium.com/@comma_ai/openpilot-port-guide-for-toyota-models-e5467f4b5fe6) ports. These guides might help you after you have the basics figured out.

- BMW, Audi, Volvo, and Mercedes all use [FlexRay](https://en.wikipedia.org/wiki/FlexRay) and can be supported after [FlexRay support](https://github.com/commaai/openpilot/pull/463) is merged.
- We put time into a Ford port, but the steering has a 10 second cutout limitation that makes it unusable.
- The 2016-2017 Honda Accord uses a custom signaling protocol for steering that's unlikely to ever be upstreamed.

Directory structure
------
    .
    ├── apk                 # The apk files used for the UI
    ├── cereal              # The messaging spec used for all logs on EON
    ├── common              # Library like functionality we've developed here
    ├── installer/updater   # Manages auto-updates of openpilot
    ├── opendbc             # Files showing how to interpret data from cars
    ├── panda               # Code used to communicate on CAN and LIN
    ├── phonelibs           # Libraries used on EON
    ├── pyextra             # Libraries used on EON
    └── selfdrive           # Code needed to drive the car
        ├── assets          # Fonts and images for UI
        ├── boardd          # Daemon to talk to the board
        ├── can             # Helpers for parsing CAN messages
        ├── car             # Car specific code to read states and control actuators
        ├── common          # Shared C/C++ code for the daemons
        ├── controls        # Perception, planning and controls
        ├── debug           # Tools to help you debug and do car ports
        ├── locationd       # Soon to be home of precise location
        ├── logcatd         # Android logcat as a service
        ├── loggerd         # Logger and uploader of car data
        ├── mapd            # Fetches map data and computes next global path
        ├── orbd            # Computes ORB features from frames
        ├── proclogd        # Logs information from proc
        ├── sensord         # IMU / GPS interface code
        ├── test            # Car simulator running code through virtual maneuvers
        ├── ui              # The UI
        └── visiond         # Embedded vision pipeline

To understand how the services interact, see `selfdrive/service_list.yaml`

User Data / chffr Account / Crash Reporting
------

By default, openpilot creates an account and includes a client for chffr, our dashcam app. We use your data to train better models and improve openpilot for everyone.

It's open source software, so you are free to disable it if you wish.

It logs the road facing camera, CAN, GPS, IMU, magnetometer, thermal sensors, crashes, and operating system logs.
The user facing camera is only logged if you explicitly opt-in in settings.
It does not log the microphone.

By using it, you agree to [our privacy policy](https://community.comma.ai/privacy.html). You understand that use of this software or its related services will generate certain types of user data, which may be logged and stored at the sole discretion of comma.ai. By accepting this agreement, you grant an irrevocable, perpetual, worldwide right to comma.ai for the use of this data.

Testing on PC
------

Check out [openpilot-tools](https://github.com/commaai/openpilot-tools): lots of tools you can use to replay driving data, test and develop openpilot from your pc.

Also, within openpilot there is a rudimentary infrastructure to run a basic simulation and generate a report of openpilot's behavior in different longitudinal control scenarios.

```bash
# Requires working docker
./run_docker_tests.sh
```

Contributing
------

We welcome both pull requests and issues on [github](http://github.com/commaai/openpilot). Bug fixes and new car ports encouraged.

We also have a [bounty program](https://comma.ai/bounties.html).

Want to get paid to work on openpilot? [comma.ai is hiring](https://comma.ai/jobs/)

Licensing
------

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

---

<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/1061157-bc7e9bf3b246ece7322e6ffe653f6af8-medium_jpg.jpg?buster=1458363130" width="75"></img> <img src="https://cdn-images-1.medium.com/max/1600/1*C87EjxGeMPrkTuVRVWVg4w.png" width="225"></img>
