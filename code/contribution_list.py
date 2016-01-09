#!python
from __future__ import division
import pandas as pd
import scipy.spatial.distance as ssd
from scipy.cluster import hierarchy
from sklearn.decomposition import NMF
import math
import string
import re
import glob
from name import Name

import matplotlib.pyplot as plt

import itertools
import numpy as np

class ContributionList(object):
    '''
    This is a mapping of contributors to campaigns

    fields:
    self.contribs: all contributions, loaded from files donation files
    self.campaigns: --numpy 1d array of all campaigns, based on unique names in contrib
    self.donors: --numpy 1d array of all donors, based on unique names in contrib
    self.candidates: dataframe of candidates, loaded from candidate files
    self.dis: dissimilarity matrix, in triangular form, (len(campaigns)^2)
    self.w: w matrix created by nmf
    self.h: h matrix created by nmf
    self.donor_matrix:

    self.disindex: Series

    What do I need?
    I need a way to
    '''

    def __init__(self):
        self.contribs = None
        self.dis = None
        self.candidates = None

    def _rebuild_lists(self):
        self.donors = pd.DataFrame(self.contribs.donor.unique())
        self.donors.columns = ['name']

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
        # if passed a single string, expand glob wildcards
        if type(filenames) == str:
            filenames = glob.glob(filenames)
        df = pd.read_csv(filenames[0], skipinitialspace=True)
        for i in range(1, len(filenames)):
            df = df.append(pd.read_csv(filenames[i], skipinitialspace=True))
        return df

    @staticmethod
    def pair_name_lists(list1, list2):
        '''
        :param list1: list
        :param list2: list
        :return: None
        Prints out two (similar, sorted) lists side-by-side, lining up matching elements together
        as an aid for finding gaps and mismatches between them.
        '''
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
        used to build contest names from WA state data in a cannonical way
        '''
        #import pdb; pdb.set_trace()
        contest = "Legislative District " + str(candidate.District) + " - " + \
            candidate.Office.title()
        if str(candidate.Position).lower() != "nan":
            # if not a senator, append position info (but change 01->1, 02->2)
            contest += " Pos. " + string.lstrip(candidate.Position, '0')
        return contest

    def load_wa_data(self, donorfiles, candidatefiles, year):
        '''
        INPUT: str or list, str or list, int
        '''

        dfdonors = self.load_file_or_files(donorfiles)

        dfcandidates = self.load_file_or_files(candidatefiles)
        dfcandidates['contest'] = dfcandidates.apply(ContributionList.build_contest_name, axis=1)

        # some candidates might be there twice. We'll try to merge them
        #multiplicity = df.groupby('Name').count()
        #dups = multiplicity[multiplicity.Office > 2].index
        # not done here

        dfmerged = dfdonors.merge(dfcandidates, how='inner', on='Name')
        dfmerged['year'] = year

        dfmerged = dfmerged[['year', 'contest', 'Contributor', 'Name', 'Amount', 'Date', 'Party']]
        dfmerged.columns = ['year', 'contest', 'donor', 'campaign', 'amount', 'date', 'party']
        if self.contribs is None:
            self.contribs = dfmerged
        else:
            self.contribs = self.contribs.append(dfmerged)
        self._rebuild_lists()

        # for looking up candidate information
        self.candidates = dfcandidates[['Name', 'contest', 'Party']].drop_duplicates()
        self.candidates.columns = ['name', 'contest', 'party']

        #self.candidates.index = self.candidates.name


    @staticmethod
    def convert_party_to_label(preference):
        '''
        :param preference: str: from election data
        :return: str: party label
        '''
        if str(preference) == 'nan':
            return "O"
        elif re.match("Democrat", preference):
            return "D"
        elif re.match("Republican", preference):
            return "R"
        elif re.match('G\.O\.P\.', preference):
            return "R"
        elif re.match('Gop', preference):
            return "R"
        else:
            return "O"

    def merge_election_data(self, electionfiles, racefilter, year):
        '''
        :param electionfiles:
        :param racefilter: str: only
        :return:
        Merge data from election results into the contribs DataFrame
        N.B. Can only merge only year at a time.
        '''

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
        # ...and also for the list of candidates
        self.candidates['canonname'] = self.candidates.name.apply(lambda x: str(Name(x, 'contribution')))

        # add year column, so we can merge only those contests
        dfelections['year'] = year

        # maybe we should do left join, but we're assuming those without election results dropped out
        self.contribs = self.contribs.merge(dfelections, how='left', on='canonname')

        self.candidates = self.candidates.merge(self.candidates, how='left', on='canonname')
        self.candidates = self.candidates.merge(dfelections, how='left', on='canonname')

        #self.campaigns['party_label'] = self.campaigns.Party.apply(lambda x: self.convert_party_to_label(x))

    def remove_single_target_contributors(self):
        # this is no longer used
        # number of campaigns each donor gives to
        # should fix how this changes the numbering (_rebuild lists doesn't change campaigns any more)
        dcnt = self.contribs[['donor', 'campaign']].drop_duplicates().groupby('donor').count()
        self.contribs = self.contribs[self.contribs.donor.isin(dcnt[dcnt.campaign > 1].index)]
        self._rebuild_lists()

    def build_donor_matrix(self):
        # TODO NEED TO FIX
        self.donor_matrix = np.zeros([len(self.candidates), len(self.donors)])

        # group df by campaings donors and iterate over groups
        for contrib_group in self.contribs[['campaign', 'donor']].drop_duplicates().groupby(['donor']):
                donor = contrib_group[0]
                # cs is a Series of the campaigns associated with that donor
                cs = contrib_group[1].loc[:, 'campaign']
                for campaign in cs:
                    self.donor_matrix[list(self.candidates.name).index(campaign), list(self.donors.name).index(donor)] += 1

    def generate_features(self, n_features):
        '''
        :return:
         Run NFM to find features
        '''

        if not hasattr(self, "donor_matrix"):
            self.build_donor_matrix()

        nmf = NMF(n_features, max_iter=1000)
        self.w = nmf.fit_transform(self.donor_matrix)
        self.h = nmf.components_
        # TODO display features

