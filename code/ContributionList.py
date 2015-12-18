#!python
from __future__ import division
import pandas as pd
import scipy.spatial.distance as ssd
from scipy.cluster import hierarchy

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

    def load_wa_data(self, filename):
        df = pd.read_csv(filename)
        self.contribs = df[['', '', 'Contributor', 'Name', 'Amount', 'Date']]
        self.contribs.columns = ['year', 'contest', 'donor', 'campaign', 'amount', 'date']
        self._rebuild_lists()

    def remove_single_target_contributors(self):
        # number of campaigns each donor gives to
        dcnt = self.contribs[['donor','campaign']].drop_duplicates().groupby('donor').count()
        self.contribs = self.contribs[self.contribs.donor.isin(dcnt[dcnt.campaign > 1].index)]
        self._rebuild_lists()


    def build_dissimilarity_matrix(self):
        shares = np.ones([len(self.campaigns),len(self.campaigns)])

        # group by contributors and iterate over groups
        for contrib_group in self.contribs[['campaign', 'donor']].drop_duplicates().groupby(['donor']):
                c = contrib_group[1].iloc[:,0]
                # get all pairs of campaigns that the donor has funded
                pairs = itertools.combinations(c, 2)
                for pair in pairs:
                    i0 = list(self.campaigns).index(pair[0])
                    i1 = list(self.campaigns).index(pair[1])
                    shares[i0, i1] += 1
                    shares[i1, i0] += 1
        shares = 1.0/shares
        # it gets upset if the diagonals are zero
        for i in range(shares.shape[0]):
            shares[i,i] = 0
        # convert to triangular form used by other software
        self.dis = ssd.squareform(shares)

    def plot_dendrogram(self):
        if self.dis is None:
            self.build_dissimilarity_matrix()
        h = hierarchy.linkage(self.dis, method='average')
        plt.figure(figsize=(10,15))
        hierarchy.dendrogram(h, labels=self.campaigns, leaf_rotation=0, orientation='left')

        plt.show()
