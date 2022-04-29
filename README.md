# Re-Search — An Academic Search Engine


## Introduction

Re-Search is an academic search engine that can be used to search open-source datasets and academic research papers similar to Google Scholar. This was built as part of a coursework for Edinburgh University's [Text Technologies for Data Science](http://www.drps.ed.ac.uk/21-22/dpt/cxinfr11145.htm) course.

🏆 This project also received the Best Project Award among 250 students / 50+ groups for the same course. 


## Features

Re-Search allows you to search for publicly available datasets and research papers using three different ranking algorithms - TF-IDF, BM25, and ScaNN. It also supports Author Search (wherever the datapoint allows it), Phrase Search, and Proximity Search along with its default search type. 

Re-Search uses React for the frontend with the backend supported by Flask and stores data in a MongoDB database. It has a separate microservice for the ScaNN algorithm as it only runs on Linux servers. We use Redis for the distributed cache but we also provide an LRU Cache implementation that works without distributed caching. We provided load balancing and horizontal scalability with Google Cloud Platform's App Engine.

- [Proposed System Design](public/system_design.jpg)
- [Home Page Screenshot](public/homepage_screenshot.jpg)


## Install

- Install  [Python 3.5+](https://www.python.org/downloads/), [Node](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm), and [MongoDB](https://www.mongodb.com/docs/manual/installation/).
- Clone the GitHub Repo & move into it.
- Install React and Python dependenices with ``npm install`` and ``pip install -r requirements.txt``
- Run them with ``npm start`` and ``flask run`` respectively.
- Run the MongoDB database (not in repo) with ``sudo service mongod start``.

You can run the backend files in production with ``waitress`` using the ``prod_*.py`` files, however, currently, the app isn't configured to provide scalability or transfer data securely. 

We'll soon publish this project on [SMASH Research Group's](https://smash.inf.ed.ac.uk/) servers in the summer. Until then you can request database access by contacting Leo/Yuto.


## Team

- [Yuto Shibata](https://github.com/YutoShibata07) (Core)
- [Sarah Kaysar](https://github.com/sarahkayser05) (Frontend)
- [Stylianos Charalampous](https://github.com/stylianosc07) (Core)
- [Suhas Narreddy](https://github.com/sulaimansuhas) (Frontend & backend)
- [Ziqian 'Leo' Ni](https://github.com/nizqleo) (Core & backend)
- [Gagan Devagiri](https://github.com/GaganSD) (Team Lead & Project Manager)



## License

[Mozilla Public License 2.0](https://github.com/GaganSD/ttds-cw3-research-team/blob/main/LICENSE) ©️ The Re-Search Team
