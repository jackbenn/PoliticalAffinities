# Final Proposal: Capstone Project

## Summary

My project is to map Seattle’s groupings based on shared contributors.

## Motivation

The city of Seattle holds non-partisan election. There are no party primaries, and candidates for mayor and city council aren’t identified by party on the ballot. Nearly all are Democrats, and progressive by national standards, but they aren’t the same. While Seattleites Seattle candidates often have similar beliefs on such issues around social justice, transportation, and the environment, the focuses are often very different.

The goal of this project is to inform voters on the relationships between candidates, and between major contributors. Other information, such as council voting records and precicnt election results might also be used to connect candidates.

## Deliverables

The project will include visualizations showing the clustered and hierarchical grouping of candidates in recent elections. It will show similar groups for major campaign donors.An interacted component will allow users to select candidates and major contributors and see a lis of connections.

## Data Sources 

Contribution information going back to 2003 is available at http://web6.seattle.gov/ethics/elections/lists.aspx. I’ve downloaded this data and it is reasonably clean, though older data is in a different format. This is my primary data source.

Information campaign contributions for state- and county-wide races is available at http://www.pdc.wa.gov/MvcQuerySystem. I might also look at King County races (they are also now non-partisan, though there party affiliation is often clear) and I might use this as an additional source for clustering the donors.

Election-result information is available at http://www.kingcounty.gov/elections/election-info.aspx. I could use the precinct results as a dissimilarity measure of candidates, it won’t be as useful it the latest (district-based) election.

Council voting records are available at http://clerk.seattle.gov/~public/CBOR1.htm, but parsing them there will require significant web scraping. If there isn’t any easier source, this may not be included in the project.

## Process

I have already looked over the contribution data for 2015 and building a hierarchy; the data still needs a bit of cleanup, mostly matching campaign names to politicians. I’ll expand that to include prior years.

Second, I will include county-wide information to see the matching donors.

Next, I’ll spend a day or two investigation council voting records. I’m not sure if I can scrape the information in a reasonable amount of time, but it would provide significant value to the project.

