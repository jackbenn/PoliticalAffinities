# PoliticalAffinities

This project is an exploration of political affinities among candidates for office, PACs, and contributors based on
common sources and targets of contributions. The Seattle and Washington State based on
shared campaign contributors.

In addition, it will classify donors based on those who give to close races, those who give to easy winner, and those
who give to easy losers, and those who give early versus those who give late.

## Data Sources

The Washington State contribution data (going back to 2000) was downloaded from http://www.pdc.wa.gov/MvcQuerySystem/AdvancedSearch/contributions

Seattle contribution information (going back to 2003) was downloaded from http://web6.seattle.gov/ethics/elections/lists.aspx. I’ve downloaded this data and it is reasonably clean, though older data is in a different format. This is my primary data source.


## Class Structure
* Contributions
    * References
        * contributors
        * campaigns
    * Fields
        * amount
        * date
* Contributors
    * References
    * Fields
        * name
* Elections
    * References
        * campaigns
    * Fields
        * P/G
        * votes
        * percent
* Campaigns
    * References
        * candidates
    * Fields
        * year
        * office
* Candidates
    * References
    * Fields
        * name
        * canonname
