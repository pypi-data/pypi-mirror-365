# Frame Surfer
<!--
Developer Note - Remove Me!

The README will have certain links/images broken until the PR is merged into `develop`. Update the GitHub links with whichever branch you're using (main etc.) if different.

The logo of the project is a placeholder (docs/images/icon-frame-surfer.png) - please replace it with your app icon, making sure it's at least 200x200px and has a transparent background!

To avoid extra work and temporary links, make sure that publishing docs (or merging a PR) is done at the same time as setting up the docs site on RTD, then test everything.
-->

<p align="center">
  <img src="https://raw.githubusercontent.com/angelopoggi/nautobot-app-frame-surfer/develop/docs/images/icon-frame-surfer.png" class="logo" height="200px">
  <br>
  <a href="https://github.com/angelopoggi/nautobot-app-frame-surfer/actions"><img src="https://github.com/angelopoggi/nautobot-app-frame-surfer/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/"><img src="https://readthedocs.org/projects/nautobot-app-frame-surfer/badge/"></a>
  <a href="https://pypi.org/project/frame-surfer/"><img src="https://img.shields.io/pypi/v/frame-surfer"></a>
  <a href="https://pypi.org/project/frame-surfer/"><img src="https://img.shields.io/pypi/dm/frame-surfer"></a>
  <br>
  An <a href="https://networktocode.com/nautobot-apps/">App</a> for <a href="https://nautobot.com/">Nautobot</a>.
</p>

## Overview

A simple app that allows users to add their Frame TVs IP address into Nautobot, along with their Unsplash credentials using Nautobots secrets provider to fetch and display images on the Frame TV.
The Apps Main job randomly selects a photo and uploads it and sets it as the primary picture. This was a simple excersice in learning how to build a Nautobot App.

### Screenshots

#### Frame TVs
![Frame TVs](https://raw.githubusercontent.com/angelopoggi/nautobot-app-frame-surfer/main/docs/images/frame_tv_model.png)
#### Unsplash
![Unsplash](https://raw.githubusercontent.com/angelopoggi/nautobot-app-frame-surfer/main/docs/images/unsplash_model.png)
#### Photos
![Photos](https://raw.githubusercontent.com/angelopoggi/nautobot-app-frame-surfer/main/docs/images/photos_model.png)
#### Jobs
![Random Job](https://raw.githubusercontent.com/angelopoggi/nautobot-app-frame-surfer/main/docs/images/fetch_random_job.png)

More screenshots can be found in the [Using the App](https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/user/app_use_cases/) page in the documentation. Here's a quick overview of some of the app's added functionality:

![](https://raw.githubusercontent.com/Network to Code, LLC/nautobot-app-frame-surfer/develop/docs/images/placeholder.png)

## Documentation

Full documentation for this App can be found over on the [Nautobot Docs](https://docs.nbframesurfer.com) website:

- [User Guide](https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/user/app_overview/) - Overview, Using the App, Getting Started.
- [Administrator Guide](https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/admin/install/) - How to Install, Configure, Upgrade, or Uninstall the App.
- [Developer Guide](https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/dev/contributing/) - Extending the App, Code Reference, Contribution Guide.
- [Release Notes / Changelog](https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/admin/release_notes/).
- [Frequently Asked Questions](https://docs.nbframesurfer.com/projects/frame-surfer/en/latest/user/faq/).

