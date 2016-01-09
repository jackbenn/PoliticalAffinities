#!python
from __future__ import division
import scipy.spatial.distance as ssd
from scipy.cluster import hierarchy
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Dendrogram(object):
    '''
    Methods and data to build a dendrogram
    '''
    def find_all_candidates(selfself, contrib):
        pass

    def find_sharing_candidates(self, contribs):
        '''
        :param contribs: DataFrame with columns for donor and campaign
        :return: None
        '''
        # find campaigns that shared donors with other campaigns
        # how many campaigns does each donor contribute to?

        donor_count = contribs[['donor', 'campaign']].drop_duplicates().groupby('donor').count()
        # find donors that gave to multiple campaigns
        big_donors = pd.Series(donor_count[donor_count.campaign > 1].index)
        # find campaign that got contributions from those donors
        self.candidates = contribs[contribs.donor.isin(big_donors)].campaign.drop_duplicates()

        print "shape candidates =", self.candidates.shape

    def build_dissimilarity_matrix(self, contribs):
        shares = np.ones([len(self.candidates), len(self.candidates)])

        # group by contributors and iterate over groups
        for contrib_group in contribs.ix[contribs.campaign.isin(self.candidates),
                                              ['campaign', 'donor']].drop_duplicates().groupby(['donor']):
                # cs is a Series of the campains associated with that donor
                cs = contrib_group[1].loc[:, 'campaign']
                #cs = np.intersect1d(cs.values, self.disindex.values, True)
                # get all pairs of campaigns that the donor has funded
                pairs = itertools.combinations(cs, 2)
                for pair in pairs:
                    i0 = list(self.candidates).index(pair[0])
                    i1 = list(self.candidates).index(pair[1])
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
        hierarchy.dendrogram(h, labels=self.candidates.values, leaf_rotation=0, orientation='left')
        #hierarchy.dendrogram(h, leaf_rotation=0, orientation='left')

        plt.show()
