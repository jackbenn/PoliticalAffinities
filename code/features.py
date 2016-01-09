#!python
from __future__ import division
from sklearn.decomposition import NMF
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Features(object):
    '''
    Class to manage NMF features
    '''

    def find_sharing_candidates(self, contribs):
        '''
        :param contribs: DataFrame with columns for donor and campaign
        :return: None
        '''
        # find campaigns that shared donors with other campaigns
        # how many campaigns does each donor contribute to?

        donor_count = contribs[['donor', 'campaign']].drop_duplicates().groupby('donor').count()
        # find donors that gave to multiple campaigns
        self.donors = pd.Series(donor_count[donor_count.campaign > 1].index)
        # find campaign that got contributions from those donors
        self.candidates = contribs[contribs.donor.isin(self.donors)].campaign.drop_duplicates()

        print "shape candidates =", self.candidates.shape
        print "shape donors =    ", self.donors.shape


    def build_donor_matrix(self, contribs):
        # TODO NEED TO FIX
        self.donor_matrix = np.zeros([len(self.candidates), len(self.donors)])

        # group df by campaings donors and iterate over groups
        i = 0
        for contrib_group in contribs[['campaign', 'donor']].drop_duplicates().groupby(['donor']):
                donor = contrib_group[0]
                if donor not in list(self.donors):
                    i = i + 1
                    print "missing ", i, donor, i, len(list(self.donors))
                    continue
                # cs is a Series of the campaigns associated with that donor
                cs = contrib_group[1].loc[:, 'campaign']
                for campaign in cs:
                    self.donor_matrix[list(self.candidates).index(campaign), list(self.donors).index(donor)] += 1

    def generate_features(self, n_features):
        '''
        :return:
         Run NFM to find features
        '''

        if not hasattr(self, "donor_matrix"):
            self.build_donor_matrix()

        self.nmf = NMF(n_features, max_iter=500)

        self.w = self.nmf.fit_transform(self.donor_matrix)
        self.h = self.nmf.components_
        # TODO display features
