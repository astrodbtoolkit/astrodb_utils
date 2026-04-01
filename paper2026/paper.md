---
title: 'AstroDB Toolkit: A Python toolkit for making and maintaining collaborative astronomical databases'
tags:
  - Python
  - astronomy
  - databases
  - data management
authors:
  - name: Kelle L. Cruz
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: "1, 2, 3" # (Multiple affiliations must be quoted)
  - name: David Rodriguez
    orcid: 0000-0000-0000-0000
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 4
affiliations:
 - name: Hunter College, City University of New York, United States
   index: 1
 - name: Graduate Center, City University of New York, United States
   index: 2
 - name: Astrophysics, American Museum of Natural History, United States
   index: 3
 - name: STScI, USA
   index: 4
date: 1 April 2026
bibliography: paper.bib

---
## Summary

*A description of the high-level functionality and purpose of the software for a diverse, non-specialist audience.*

We introduce the AstroDB Toolkit to fill a gap in the data management/sharing ecosystem for astronomers by providing a robust toolkit to empower astronomers to build databases of astronomical sources. Currently, astronomers reinvent the wheel, spending time making technology choices, database design decisions, and web applications as opposed to being able to focus on the analysis and physical interpretation of the actual data. The AstroDB Toolkit is an open-source, openly developed tool that greatly lowers the technology burden on the astronomers and empowers them to make databases of astronomical sources using a common, interoperable framework. The Toolkit uses GitHub’s features and its collaborative workflow. Spectra, images, and other non-tabular data are stored as pointers to cloud-hosted files.

## Statement of need

*A section that clearly illustrates the research purpose of the software and places it in the context of related work. This should clearly state what problems the software is designed to solve, who the target audience is, and its relation to other work.*

The purpose of the AstroDB Toolkit is to fill a gap in the data management/sharing ecosystem for astronomers by providing a robust toolkit to empower astronomers to build databases of astronomical sources.
In the “big data” era of large, long-standing missions such as TESS, Kepler, and JWST, astronomers find themselves managing increasingly large and unwieldy collections of target parameters, both observed and modeled.
Currently, astronomers reinvent the wheel, spending time making technology choices, database design decisions, and web applications as opposed to being able to focus on the analysis and physical interpretation of the actual data.
A plethora of different Astronomer-made “databases” exists, all with different tech stacks and underlying schemas.
The AstroDB Toolkit is an open-source tool that greatly lowers the technology burden on the astronomers and empowers them to make databases of astronomical sources using a common, interoperable framework.

The AstroDB Toolkit aims to serve the needs of individual astronomers and small-to-medium sized collaborations who need a data management system for hundreds to thousands of sources. The Toolkit will bridge the divide where a shared Google sheet is insufficient, but the dataset is either still living (e.g., follow-up observations are underway, new parameters being derived) or otherwise not appropriate for an institutional archive.

## State of the field

*A description of how this software compares to other commonly-used packages in the research area. If related tools exist, provide a clear “build vs. contribute” justification explaining your unique scholarly contribution and why existing alternatives are insufficient.*

The astronomical community has produced numerous data compilations, but they fall into two broad categories: large institutional archives and small grassroots efforts — and neither category offers a reusable framework for building new compilations.

**Institutional archives** such as the NASA Exoplanet Archive [@akeson:2013], HITRAN [@gordon:2022], and WISeREP [@yaron:2012] provide excellent data access and, in the case of the Exoplanet Archive, gold-standard interoperability via the IVOA Table Access Protocol (TAP) and ADQL. However, their backends are undisclosed, they are operated by dedicated engineering teams, and they cannot be deployed by individual researchers or small collaborations. Contributing data requires submission through web forms or bulk upload APIs. These platforms are powerful for data consumers but offer no path for an astronomer to build their own analogous database.

**Grassroots compilations** span a wide range of technology choices with little interoperability between them. The Open Astronomy Catalogs (AstroCats; @guillochon:2017) represent the most mature open-source effort: each transient source is stored as a richly annotated JSON file in a Git repository, with a documented schema that mandates source attribution for every data point. The framework was explicitly designed to be reusable, and four separate catalogs (supernovae, tidal disruption events, novae, black holes) were built on it. However, AstroCats supports only JSON — there is no relational query layer — and the codebase targets Python 2/3.4–3.6, limiting its continued maintainability. The MOCA database of open clusters [@malo:2021] uses a hosted MySQL backend with a companion Python package (`mocapy`) for querying, but the database schema is not designed to be forked and repopulated for a new science case. The Community Atlas of Tidal Streams [@price-whelan:2021] encapsulates its science logic in Jupyter notebooks with no persistent database backend, making it difficult to query programmatically or extend to new data types. At the lightest end of the spectrum, compilations such as the Ultracool Sheet [@ucsheet] and the Hypatia Catalog [@hinkel:2014] rely on Google Sheets or web-only interfaces — convenient for human browsing but lacking version control, contribution workflows, or machine-readable schemas.

Across this landscape, several gaps are consistent. No community-built grassroots project exposes a TAP or Virtual Observatory interface. Schema documentation is rare. Contribution workflows are ad hoc (CSV uploads, pull requests against JSON files, or web forms), with no shared tooling. Most critically, none of these projects offer a general-purpose, deployable framework: an astronomer who wants to build their own compilation of, say, low-mass stars or high-redshift galaxies cannot fork any of these projects and adapt the infrastructure to their science case without essentially starting from scratch.

The AstroDB Toolkit fills this gap. It provides a schema-first, SQLite-backed, Git-native framework that any researcher can clone from a template repository and immediately begin populating with their own sources. Unlike AstroCats — the closest precedent — the Toolkit supports structured SQL queries via SQLAlchemy, integrates with standard Python astronomy libraries (`astropy`, `specutils`), and is actively maintained against modern Python versions. The common schema and shared Python tooling mean that databases built with the Toolkit are interoperable with one another by construction, lowering the barrier both for data consumers and for researchers launching new compilations.

## Software design

*An explanation of the trade-offs you weighed, the design/architecture you chose, and why it matters for your research application. This should demonstrate meaningful design thinking beyond a superficial code structure description.*

The technical choices that were made in the development of the AstroDB Toolkit followed several design requirements:

- Ability to represent complex data models in a simple, intuitive fashion,
- Support for datasets up to tens of thousands of astrophysical sources,
- Collaborative editing that enables community members to modify and maintain data holdings,
- Be usable privately for managing not-yet-public data,
- Interactively explore and visualize holdings via a website,
- Queryable locally via scripting without the need for an internet connection.

As described in the Technical Description, the AstroDB Toolkit meets all of these requirements. We have designed a tool that uses GitHub’s features and its collaborative workflow. The Toolkit fuels open science by providing a common framework for databases, managed openly on GitHub. This shared framework makes databases easier for Astronomers to build and maximizes their interoperability, thus empowering open science and facilitating data sharing.

The AstroDB Toolkit consists of:

- a template schema,
- Python packages (AstrodbKit, astrodb_utils),
- documentation and suggested workflows, and
- a web application.

The AstroDB Toolkit facilitates the creation of intermediate-scale databases focused on typical astronomy use-cases. AstroDB relies on an object-model that naturally translates to astronomical sources, that is to say, the core table in the database can represent objects such as brown dwarfs or galaxies, while supporting tables represent properties of that object. Because the AstroDB Toolkit’s core Python package, AstrodbKit, is a wrapper around the database package SQLAlchemy, it supports a large range of database architectures, including SQLite, PostgreSQL, MySQL, etc, while using language that is familiar to astronomers. AstrodbKit also supports cone searches and can output results as astropy.table objects.

Uses Felis.

### Collaborative Workflow and Testing with GitHub

One of the key design requirements for an AstroDB Toolkit-powered database is support for collaborative editing of the holdings using a GitHub workflow. As a result, the Toolkit creates databases that are fundamentally a set of plain text JSON files that describe each object. When users make changes to the properties of an object, such as adding a new spectrum or updating a value for a radial velocity, these changes are human-readable as a simple diff between two JSON files and can be reviewed via pull requests. This JSON document store architecture allows for a community to maintain a database, review changes as they come in, and use automated tools to validate the database. The Astrodbkit package has tools to readily transform data between the document store and relational database to facilitate managing local, private data as well as external applications, such as a hosted website.

By exporting a database to a JSON document store, we can use git and GitHub to handle version control for our database as well as curate commits via pull requests.

An individual user may contain their own copy of any database. They may make changes in their local branch and push to their copy on GitHub. By issuing a pull request, they request their changes be adopted into the main branch of the database. Because the database is stored as individual JSON documents, reviewers can see exactly which objects have been updated and can comment on the changes if needed.

As part of the pull request process, automatic tests implemented via GitHub Actions can be run to verify the integrity of the database. This ensures no changes took place that break the functionality of the database and also include verification for the data that has been added.
Finally, when the pull request is accepted, additional automated tasks can be performed to regenerate the database and push it to external users of the database, such as a graphical user interface.

### Spectra and non-tabular data

Spectra, images, and other non-tabular data are stored as pointers to cloud-hosted files. The files are hosted in a variety of places, including institutional repositories. However, we have found the best host to be Amazon Simple Storage Service (Amazon S3). In order to enable the database to fully function without an internet connection and/or to point to files not hosted in the cloud, we allow pointers to local files using an environment variable to indicate a local path.
AstrodbKit contains logic to understand which columns contain pointers to spectra and translates them into specutils.Spectrum1D objects. We propose here to provide support for lightcurves which would be translated into lightkurve.lightcurve objects.  (Lightkurve is a NASA-package maintained by the TESS team at GSFC.)

## Research impact statement

*Evidence of realized impact (publications, external use, integrations) or credible near-term significance (benchmarks, reproducible materials, community-readiness signals). The evidence should be compelling and specific, not aspirational.*

The current poster-child of the AstroDB Toolkit is SIMPLE, the Substellar and IMaged PLanet Explorer Archive of Complex Objects [https://simple-bd-archive.org/](https://simple-bd-archive.org/). The SIMPLE database contains nearly 3,500 brown dwarfs with photometry, radial velocity, spectral types, and more. Holdings include data from NASA missions such as HST, JWST, and Spitzer in addition to ground-based data and modeled parameters.
Over the past few years, our team has built this database by ingesting new sources, adding spectra, refining the underlying schema, and updating our website to best meet our needs. The current AstroDB Toolkit was built based on lessons learned with this implementation. The Toolkit is still growing as we aim for a more generalized infrastructure. Our goal for this proposal is to work on these details, focusing on improvements to allow other users to straightforwardly develop their own databases.

## Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for 

For a quick reference, the following citation commands can be used:
<!-- 
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)" -->

## Figures

*Figures go here*

<!-- Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% } -->

## AI usage disclosure

Generative AI tools were used at several stages of this work.

**GitHub Copilot** was used to assist in writing small portions of code and inline documentation throughout the development of the AstroDB Toolkit. Its assistance was limited to code completion and documentation suggestions.

**Claude Sonnet 4.6** (Anthropic, accessed via Claude Code CLI) was used to assist in drafting the "State of the field" section of this manuscript, including researching and summarizing the technology stacks and schemas of related astronomical data compilations, and constructing initial BibTeX bibliography entries for cited works.

All AI-generated text and code was thoroughly reviewed, revised, and validated by the human authors. The authors made all primary architectural and design decisions for the AstroDB Toolkit. The authors take full responsibility for the accuracy of all content in this manuscript, including citations and bibliographic details.

## Acknowledgements

We acknowledge contributions from Arjun, HS students, etc.

## References

Some References
