---
title: 'AstroDB Toolkit: A toolkit for creating and maintaining small, collaborative astronomical databases'
tags:
  - Python
  - astronomy
  - databases
  - data management
authors:
  - name: Kelle L. Cruz
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: "1, 2, 3" 
  - name: David Rodriguez
    orcid: 0000-0000-0000-0000
    equal-contrib: true 
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

We introduce the AstroDB Toolkit to fill a gap in the data management/sharing ecosystem for astronomers by providing a robust toolkit to empower astronomers to build databases of astronomical sources. The AstroDB Toolkit is an open-source, openly developed tool that greatly lowers the technology burden on the astronomers and empowers them to make databases of astronomical sources using a common, interoperable framework. The Toolkit uses GitHub’s features and its collaborative workflow.

## Statement of need

The purpose of the AstroDB Toolkit is to fill a gap in the data management/sharing ecosystem for astronomers by providing a robust toolkit to empower astronomers to build databases of astronomical sources.
In the “big data” era of large, long-standing missions such as TESS, Kepler, and JWST, astronomers find themselves managing increasingly large and unwieldy collections of target parameters, both observed and modeled.
Currently, astronomers reinvent the wheel, spending time making technology choices, database design decisions, and web applications as opposed to being able to focus on the analysis and physical interpretation of the actual data.
The AstroDB Toolkit greatly lowers the technology burden on the astronomers and empowers them to make databases of astronomical sources using a common, interoperable framework.

The AstroDB Toolkit aims to serve the needs of individual astronomers and small-to-medium sized collaborations who need a data management system for hundreds to thousands of sources. The Toolkit bridges the divide where a shared Google sheet is insufficient, but the dataset is either still living (e.g., follow-up observations are underway, new parameters being derived) or otherwise not appropriate for an institutional archive.

## State of the field

The astronomical community has produced numerous data compilations, but they fall into two broad categories: large institutional archives and small grassroots efforts — and neither category offers a reusable framework for building new compilations.

**Institutional archives** such as the NASA Exoplanet Archive [@akeson:2013], HITRAN [@gordon:2022], and WISeREP [@yaron:2012] provide excellent data access and, in the case of the Exoplanet Archive, gold-standard interoperability via the IVOA Table Access Protocol (TAP) and ADQL. However, their backends are undisclosed, they are operated by dedicated engineering teams, and they cannot be deployed by individual researchers or small collaborations. Contributing data requires submission through web forms or bulk upload APIs. These platforms are powerful for data consumers but offer no path for an astronomer to build their own analogous database.

**Grassroots compilations** span a wide range of technology choices with little interoperability between them. The Open Astronomy Catalogs (AstroCats; @guillochon:2017) represent the most mature open-source effort: each transient source is stored as a richly annotated JSON file in a Git repository, with a documented schema that mandates source attribution for every data point. The framework was explicitly designed to be reusable, and four separate catalogs (supernovae, tidal disruption events, novae, black holes) were built on it. However, AstroCats supports only JSON — there is no relational query layer — and the codebase targets Python 2/3.4–3.6, limiting its continued maintainability. The MOCA database of open clusters [@malo:2021] uses a hosted MySQL backend with a companion Python package (`mocapy`) for querying, but the database schema is not designed to be forked and repopulated for a new science case. The Community Atlas of Tidal Streams [@price-whelan:2021] encapsulates its science logic in Jupyter notebooks with no persistent database backend, making it difficult to query programmatically or extend to new data types. At the lightest end of the spectrum, compilations such as the Ultracool Sheet [@ucsheet] and the Hypatia Catalog [@hinkel:2014] rely on Google Sheets or web-only interfaces — convenient for human browsing but lacking version control, contribution workflows, or machine-readable schemas.

Across this landscape, several gaps are consistent. Schema documentation is rare. Contribution workflows are ad hoc (CSV uploads, pull requests against JSON files, or web forms), with no shared tooling. Most critically, none of these projects offer a general-purpose, deployable framework: an astronomer who wants to build their own compilation of, say, low-mass stars or high-redshift galaxies cannot fork any of these projects and adapt the infrastructure to their science case without essentially starting from scratch.

## Software design

The technical choices that were made in the development of the AstroDB Toolkit followed several design requirements:

- Ability to represent complex data models in a simple, intuitive fashion,
- Support for datasets up to tens of thousands of astrophysical sources,
- Collaborative editing that enables community members to modify and maintain data holdings,
- Be usable privately for managing not-yet-public data,
- Interactively explore and visualize holdings via a website,
- Queryable locally via scripting without the need for an internet connection.

As described below, the AstroDB Toolkit meets all of these requirements.

The AstroDB Toolkit consists of:

- a template schema,
- Python packages (AstrodbKit, astrodb_utils), and
- documentation and suggested workflows

The AstroDB Toolkit facilitates the creation of intermediate-scale databases focused on typical astronomy use-cases. The Toolkit's template schema relies on an object-model that naturally translates to astronomical sources, that is to say, the core table in the database can represent objects such as brown dwarfs or galaxies, while supporting tables represent properties of that object. Because the AstroDB Toolkit’s core Python package, `AstrodbKit`, is a wrapper around the database package `SQLAlchemy`, it supports a large range of database architectures, including SQLite, PostgreSQL, MySQL, etc, while using language that is familiar to astronomers. `AstrodbKit` also supports cone searches and can output results as `astropy.table` objects.

Uses Felis.

### Collaborative Workflow and Testing with GitHub

One of the key design requirements for an AstroDB Toolkit-powered database is support for collaborative editing of the holdings using a GitHub workflow. As a result, the Toolkit creates databases that are fundamentally a set of plain text JSON files that describe each object. When users make changes to the properties of an object, such as adding a new spectrum or updating a value for a radial velocity, these changes are human-readable as a simple diff between two JSON files and can be reviewed via pull requests. This JSON document store architecture allows for a community to maintain a database, review changes as they come in, and use automated tools to validate the database. The Astrodbkit package has tools to readily transform data between the document store and relational database to facilitate managing local, private data as well as external applications, such as a hosted website.

By exporting a database to a JSON document store, we can use git and GitHub to handle version control for our database as well as curate commits via pull requests.

An individual user may contain their own copy of any database. They may make changes in their local branch and push to their copy on GitHub. By issuing a pull request, they request their changes be adopted into the main branch of the database. Because the database is stored as individual JSON documents, reviewers can see exactly which objects have been updated and can comment on the changes if needed.

As part of the pull request process, automatic tests implemented via GitHub Actions can be run to verify the integrity of the database. This ensures no changes took place that break the functionality of the database and also include verification for the data that has been added.

Finally, when the pull request is accepted, additional automated tasks can be performed to regenerate the database and push it to external users of the database, such as a graphical user interface.

<!-- Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% } -->

### Spectra and non-tabular data

Spectra, images, and other non-tabular data are stored as pointers to cloud-hosted files. The files are hosted in a variety of places, including institutional repositories. However, we have found the best host to be Amazon Simple Storage Service (Amazon S3). In order to enable the database to fully function without an internet connection and/or to point to files not hosted in the cloud, we allow pointers to local files using an environment variable to indicate a local path.
AstrodbKit contains logic to understand which columns contain pointers to spectra and translates them into `specutils.Spectrum` objects.

## Research impact statement

*Evidence of realized impact (publications, external use, integrations) or credible near-term significance (benchmarks, reproducible materials, community-readiness signals). The evidence should be compelling and specific, not aspirational.*

The current poster-child of the AstroDB Toolkit is SIMPLE, the Substellar and IMaged PLanet Explorer Archive of Complex Objects [https://simple-bd-archive.org/](https://simple-bd-archive.org/).

The newest useage of the Toolkit is focused on Dwarf Galaxies. There are tens if not hundreds of galaxies in the Local Group, with a diverse range of applicable science problems. Many of these scientific applications depend on having as complete as possible a list of properties for these galaxies such as: total luminosity, half-light radius, and redshift/systemic velocity.

## AI usage disclosure

Generative AI tools were used at several stages of this work.

**GitHub Copilot** was used to assist in writing small portions of code and inline documentation throughout the development of the AstroDB Toolkit. Its assistance was limited to code completion and documentation suggestions.

**Claude Sonnet 4.6** (Anthropic, accessed via Claude Code CLI) was used to assist in drafting the "State of the field" section of this manuscript, including researching and summarizing the technology stacks and schemas of related astronomical data compilations, and constructing initial BibTeX bibliography entries for cited works.

All AI-generated text and code was thoroughly reviewed, revised, and validated by the human authors. The authors made all primary architectural and design decisions for the AstroDB Toolkit. The authors take full responsibility for the accuracy of all content in this manuscript, including citations and bibliographic details.

## Acknowledgements

We acknowledge contributions from Arjun, HS students, etc.

## References
