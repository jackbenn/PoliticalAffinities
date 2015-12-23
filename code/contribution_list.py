#!python
from __future__ import division
import pandas as pd
import scipy.spatial.distance as ssd
from scipy.cluster import hierarchy
import math
import string
from name import Name

import matplotlib.pyplot as plt

import itertools
import numpy as np


class ContributionList(object):
    '''
    This is a mapping of contributors to campaigns
    '''

    def __init__(self):
        self.contribs = None
        self.dis = None

    def _rebuild_lists(self):
        self.campaigns = self.contribs.campaign.unique()
        self.donors = self.contribs.donor.unique()

    def load_seattle_data(self, filename):
        '''
        Load data from City of Seattle
        for now, just do the contributions (rather than alltransactions) files
        '''
        df = pd.read_csv(filename)
        self.contribs = df[['intElectionCycle', 'strContest', 'strTransactorName', 'strCampaignName', 'moneyAmount', 'strTransactionDate']]
        self.contribs.columns = ['year', 'contest', 'donor', 'campaign', 'amount', 'date']
        # TODO  datify the date and maybe year
        # we're leaving out (for now) address, employer, and other stuff
        self._rebuild_lists()

    @staticmethod
    def load_file_or_files(filenames):
        if type(filenames) == str:
            filenames = [filenames]
        df = pd.read_csv(filenames[0], skipinitialspace=True)
        for i in range(1, len(filenames)):
            df = df.append(pd.read_csv(filenames[i], skipinitialspace=True))
        return df

    @staticmethod
    def pair_name_lists(list1, list2):
        width1 = max([len(x) for x in list1])
        formatstr = "{0:" + str(width1) + "} {1}"
        sorted1 = sorted(list1)
        sorted2 = sorted(list2)
        i1 = i2 = 0
        while i1 < len(sorted1) and i2 < len(sorted2):
            if sorted1[i1] == sorted2[i2]:
                print formatstr.format(sorted1[i1], sorted2[i2])
                i1 += 1
                i2 += 1
            elif sorted1[i1] < sorted2[i2]:
                print formatstr.format(sorted1[i1], "")
                i1 += 1
            else:
                print formatstr.format("", sorted2[i2])
                i2 += 1

    @staticmethod
    def build_contest_name(candidate):
        '''
        INPUT: DataFrame (with Office, District, and Position columns)
        used to build contest names from WA state data in a cononical way
        '''
        contest = "Legaslative District " + str(candidate.District) + " - " + \
            candidate.Office.lower()
        if str(candidate.Position) != "nan":
            # if not a senator, append position info (but change 01->1, 02->2)
            contest += " Pos. " + string.lstrip(candidate.Position, '0')

    def load_wa_data(self, donorfiles, candidatefiles, year):
        '''
        INPUT: str or list, str or list, int
        '''
        #import pdb; pdb.set_trace()

        dfdonors = self.load_file_or_files(donorfiles)

        dfcandidates = self.load_file_or_files(candidatefiles)

        # some candidates might be there twice. We'll try to merge them
        #multiplicity = df.groupby('Name').count()
        #dups = multiplicity[multiplicity.Office > 2].index
        # not done here

        dfmerged = dfdonors.merge(dfcandidates, how='inner', on='Name')
        dfmerged['year'] = year
        dfmerged['contest'] = dfmerged.apply(ContributionList.build_contest_name, axis=1)

        self.contribs = dfmerged[['year', 'contest', 'Contributor', 'Name', 'Amount', 'Date']]
        self.contribs.columns = ['year', 'contest', 'donor', 'campaign', 'amount', 'date']
        self._rebuild_lists()

    def merge_election_data(self, electionfiles, racefilter):
        dfelections = self.load_file_or_files(electionfiles)

        # since many different races can be in the same resutls file, we have a filter
        # to just look at elections where the races match that word
        # but maybe we should use the JurisdictionName (e.g., =='Legislative') column
        dfelections = dfelections[dfelections.Race.str.match(racefilter)]

        # merge results
        # first, create canonicalized name column on elections df
        dfelections['canonname'] = dfelections.Candidate.apply(lambda x: str(Name(x, 'election')))
        # ...and for the contribs df
        self.contribs['canonname'] = self.contribs.campaign.apply(lambda x: str(Name(x, 'contribution')))

        # maybe we should do left join, but we're assuming those without election results dropped out
        self.contribs = self.contribs.merge(dfelections, how='inner', on='canonname')


    def remove_single_target_contributors(self):
        # number of campaigns each donor gives to
        dcnt = self.contribs[['donor', 'campaign']].drop_duplicates().groupby('donor').count()
        self.contribs = self.contribs[self.contribs.donor.isin(dcnt[dcnt.campaign > 1].index)]
        self._rebuild_lists()

    def build_donor_matrix(self):
        self.donor_matrix = np.zeros([len(self.campaigns), len(self.donors)])

        # group df by campaings donors and iterate over groups
        for contrib_group in self.contribs[['campaign', 'donor']].drop_duplicates().groupby(['donor']):
                # cs is a Series of the campains associated with that donor
                donor = contrib_group[0]
                #print donor
                cs = contrib_group[1].loc[:, 'campaign']
                for campaign in cs:
                    self.donor_matrix[list(self.campaigns).index(campaign), list(self.donors).index(donor)] += 1

    def build_dissimilarity_matrix(self):
        shares = np.ones([len(self.campaigns), len(self.campaigns)])
        # group by contributors and iterate over groups
        for contrib_group in self.contribs[['campaign', 'donor']].drop_duplicates().groupby(['donor']):
                # cs is a Series of the campains associated with that donor
                cs = contrib_group[1].loc[:, 'campaign']
                # get all pairs of campaigns that the donor has funded
                pairs = itertools.combinations(cs, 2)
                for pair in pairs:
                    i0 = list(self.campaigns).index(pair[0])
                    i1 = list(self.campaigns).index(pair[1])
                    shares[i0, i1] += 1
                    shares[i1, i0] += 1
        shares = 1.0/shares
        # dendrogram gets upset if the diagonals are zero
        for i in range(shares.shape[0]):
            shares[i, i] = 0
        # convert to triangular form used by other software
        self.dis = ssd.squareform(shares)



    def plot_dendrogram(self):
        if self.dis is None:
            self.build_dissimilarity_matrix()
        h = hierarchy.linkage(self.dis, method='average')
        plt.figure(figsize=(10, 15))
        hierarchy.dendrogram(h, labels=self.campaigns, leaf_rotation=0, orientation='left')

        plt.show()

