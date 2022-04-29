# Re-Search — An Academic Search Engine


## Introduction

Re-Search is an academic search engine that can be used to search open-source datasets and academic research papers similar to Google Scholar. This was built as part of a coursework for Edinburgh University's [Text Technologies for Data Science](http://www.drps.ed.ac.uk/21-22/dpt/cxinfr11145.htm) course.

🏆 This project also received the Best Project Award among 250 students / 50+ groups for the same course. 


## Features

Re-Search allows you to search for publicly available datasets and research papers using three different ranking algorithms - TF-IDF, BM25, and ScaNN. It also supports Author Search (wherever the datapoint allows it), Phrase Search, and Proximity Search along with its default search type. 

Re-Search uses React for the frontend with the backend supported by Flask. It has a separate microservice for the ScaNN algorithm as it only runs on Linux servers. We use Redis for the distributed cache but we also provide an LRU Cache implementation that works without distributed caching. We provided load balancing and horizontal scalability with Google Cloud Platform's App Engine.

- [Proposed System Design](public/system_design.jpg)
- [Home Page Screenshot](public/homepage_screenshot.jpg)


## Install

- Install [node & npm 14.0+](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) and [Python 3.5+](https://www.python.org/downloads/)
- Clone the GitHub Repo.
- Move into the directory.
- Install React and Python dependenices with ``npm install`` and ``pip install -r requirements.txt``
- Run them with ``npm start`` and ``flask run`` respectively.

You can run the backend files in production with ``waitress`` using the ``prod_*.py`` files, however, currently, the app isn't configured to provide scalability or transfer data securely. You can request database access by contacting Leo/Yuto.

We'll soon publish this project on [SMASH Research Group's](https://smash.inf.ed.ac.uk/) servers in the summer.



## Team

- Yuto Shibata (Core)
- Sarah Kaysar (Frontend)
- Stylianos Charalampous (Core)
- Suhas Narreddy (Frontend & backend)
- Ziqian 'Leo' Ni (Core & backend)
- Gagan Devagiri (Team Lead)



## License

[Mozilla Public License 2.0](https://github.com/GaganSD/ttds-cw3-research-team/blob/main/LICENSE) ©️ The Re-Search Team
