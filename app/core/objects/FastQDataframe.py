import pandas as pd
import uuid
import pickle
from os.path import abspath
from app.core.objects.FastQData import FastQData


class FastQDataframe:

    __df = pd.DataFrame
    __uuid = ""

    def __init__(self, fw_data: FastQData=None, rvc_data: FastQData=None, fw_items: list=None, fw_indices: list=None,
                 rvc_items: list=None, rvc_indices: list=None, df_id: str=None, fw_dict=None, rv_dict=None):
        """
        A FastQDataframe can be constructed multiple ways. The most straight forward way is to use FastQData objects,
        But it is also possible to use list items
        :param fw_data: FastQData
        :param rvc_data: FastQData
        :param fw_items: list with forward sequence and quality score items
        :param fw_indices: list with identifiers of the forward items (fastQ headers)
        :param rvc_items: list with reverse complement sequence and quality score items
        :param rvc_indices: list with identifiers of the reverse complement items (fastQ headers)
        :param df_id: unique identifier for a FastQDataframe instance. Is used for writing this object to a pickle
        """
        if df_id:
            self.__uuid = df_id
        else:
            self.__uuid = str(uuid.uuid1())
        if fw_items and fw_indices and rvc_items and rvc_indices:
            self.__from_lists(fw_items, fw_indices, rvc_items, rvc_indices)
        elif fw_data and rvc_data:
            self.__from_fastqdata(fw_data, rvc_data)
        elif fw_dict and rv_dict:
            self.__from_dict(fw_dict, rv_dict)
        else:
            raise Exception("No input data given, please use either FastQData objects or list objects")

    def __from_lists(self, items_fw: list, indices_fw: list, items_rvc: list, indices_rvc: list):
        """
        Creates a pandas dataframe from list items
        :param items_fw:
        :param indices_fw:
        :param items_rvc:
        :param indices_rvc:
        :return:
        """
        fw_columns = ['fw_seq', 'fw_seq_score']
        fw_df = pd.DataFrame(data=items_fw, columns=fw_columns, index=indices_fw)

        rvc_columns = ['rvc_seq', 'rvc_seq_score']
        rvc_df = pd.DataFrame(data=items_rvc, columns=rvc_columns, index=indices_rvc)

        self.__df = fw_df.join(rvc_df)

    def __from_fastqdata(self, fw_data: FastQData, rvc_data: FastQData):
        """
        Create a pandas dataframe from FastQData objects
        :param fw_data:
        :param rvc_data:
        :return:
        """
        fw_columns = ['fw_seq', 'fw_seq_score', 'fw_seq_length', 'fw_A_perc', 'fw_T_perc', 'fw_G_perc', 'fw_C_perc', 'fw_Q-score']
        fw_df = pd.DataFrame(columns=fw_columns, index=fw_data.get_index_list())

        fw_df['fw_seq'] = fw_data.get_sequence_list()
        fw_df['fw_seq_score'] = fw_data.get_q_score_list()

        rvc_columns = ['rv_seq','rvc_seq', 'rv_seq_score', 'rv_seq_length', 'rv_A_perc', 'rv_T_perc', 'rv_G_perc', 'rv_C_perc', 'rv_Q-score']
        rvc_df = pd.DataFrame(columns=rvc_columns, index=rvc_data.get_index_list())

        rvc_df['rv_seq'] = rvc_data.get_sequence_list()
        rvc_df['rvc_seq'] = rvc_data.get_complement_list()
        rvc_df['rv_seq_score'] = rvc_data.get_q_score_list()
        joined_df = fw_df.join(rvc_df)
        joined_df['flagged'] = False
        joined_df['paired_flag'] = False
        joined_df['fw_a_perc_flag'] = False
        joined_df['fw_t_perc_flag'] = False
        joined_df['fw_g_perc_flag'] = False
        joined_df['fw_c_perc_flag'] = False
        joined_df['rv_a_perc_flag'] = False
        joined_df['rv_t_perc_flag'] = False
        joined_df['rv_g_perc_flag'] = False
        joined_df['rv_c_perc_flag'] = False
        joined_df['fw_seq_len_flag'] = False
        joined_df['rv_seq_len_flag'] = False
        joined_df['identity_flag'] = False
        self.__df = joined_df

    def __from_dict(self, fw_data, rv_data):
        """
        Create a pandas dataframe from FastQData objects
        :param fw_data:
        :param rvc_data:
        :return:
        """
        fw_columns = ['fw_seq', 'fw_seq_score', 'fw_seq_length', 'fw_A_perc', 'fw_T_perc', 'fw_G_perc', 'fw_C_perc',
                      'fw_Q-score']
        fw_df = pd.DataFrame(columns=fw_columns, index=fw_data['index'])

        fw_df['fw_seq'] = fw_data['seq']
        fw_df['fw_seq_score'] = fw_data['qual']

        rv_columns = ['rv_seq', 'rvc_seq', 'rv_seq_score', 'rv_seq_length', 'rv_A_perc', 'rv_T_perc', 'rv_G_perc',
                       'rv_C_perc', 'rv_Q-score']
        rv_df = pd.DataFrame(columns=rv_columns, index=rv_data['index'])
        rv_df['rv_seq'] = rv_data['seq']
        rv_df['rvc_seq'] = rv_data['comp']
        rv_df['rv_seq_score'] = rv_data['qual']

        del fw_data
        del rv_data

        joined_df = fw_df.join(rv_df)

        del fw_df
        del rv_df

        joined_df['flagged'] = False
        joined_df['paired_flag'] = False
        joined_df['fw_a_perc_flag'] = False
        joined_df['fw_t_perc_flag'] = False
        joined_df['fw_g_perc_flag'] = False
        joined_df['fw_c_perc_flag'] = False
        joined_df['rv_a_perc_flag'] = False
        joined_df['rv_t_perc_flag'] = False
        joined_df['rv_g_perc_flag'] = False
        joined_df['rv_c_perc_flag'] = False
        joined_df['fw_seq_len_flag'] = False
        joined_df['rv_seq_len_flag'] = False
        joined_df['identity_flag'] = False
        self.__df = joined_df

    def set_df(self, df: pd.DataFrame):
        self.__df = df

    def update_by_list(self, data: list, columns: list):
        # items of data must be the same length as the number of indexes in the dataframe
        for i, column in enumerate(columns):
            self.__df[column] = [data][i]

    def update_by_series(self, data: pd.Series):
        self.__df.update(data)

    def update_by_dataframe(self, data: pd.DataFrame):
        self.__df.update(data)

    def get_dataframe(self):
        return self.__df

    def get_list_columns(self):
        return self.__df.columns

    def get_column(self, column_name: str):
        return self.__df[column_name]

    def get_columns(self, column_names: list):
        return self.__df[column_names]

    def get_uuid(self):
        return self.__uuid

    def filter_between(self, value1, value2, columns: list):
        filtered_df = self.__df.copy()
        for column in columns:
            filtered_df = filtered_df[filtered_df[column].between(value1, value2, inclusive=True)]
        return filtered_df

    def filter_greater_than(self, value, columns: list):
        filtered_df = self.__df.copy()
        for column in columns:
            filtered_df = filtered_df[filtered_df[column] > value]
        return filtered_df

    def filter_smaller_than(self, value, columns: list):
        filtered_df = self.__df.copy()
        for column in columns:
            filtered_df = filtered_df[filtered_df[column] < value]
        return filtered_df

    def filter_equals(self, value, columns: list):
        filtered_df = self.__df.copy()
        for column in columns:
            filtered_df = filtered_df[filtered_df[column] == value]
        return filtered_df

    @staticmethod
    def is_filtered(row):
        try:
            if row['flagged'] == False:
                return True
        except KeyError:
            return False

    def flag_any(self, columns: list=['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag','fw_g_perc_flag', 'fw_c_perc_flag',
                       'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag', 'rv_c_perc_flag', 'fw_seq_len_flag',
                                      'rv_seq_len_flag', 'identity_flag'], axis=1, flag_column='flagged'):
        self.__df[flag_column] = self.__df[columns].any(axis)

    def flag_between(self, filter_on, value1, value2, column='flagged'):
        self.__df[column] = self.__df[filter_on].apply(lambda row: False if value1 <= row <= value2 else True)

    @staticmethod
    def __do_between(row, column, value1, value2):
        if value1 <= row[column] <= value2:
            return False
        else:
            return True

    def flag_smaller_than(self, filter_on, value, column='flagged'):
        self.__df[column] = self.__df[filter_on].apply(lambda row: False if row <= value else True)

    @staticmethod
    def __do_smaller(row, column, value):
        if row[column] <= value:
            return False
        else:
            return True

    def flag_greater_than(self, filter_on, value, column='flagged'):
        self.__df[column] = self.__df[filter_on].apply(lambda row: False if row >= value else True)

    @staticmethod
    def __do_greater(row, column, value):
        if row[column] >= value:
            return False
        else:
            return True

    def flag_equals(self, filter_on, value, column='flagged'):
        self.__df[column] = self.__df[filter_on].apply(lambda row: False if row == value else True)

    @staticmethod
    def __do_equals(row, column, value):
        if row[column] == value:
            return False
        else:
            return True

    def to_json(self):
        return self.__df.to_json()

    def to_csv(self, path):
        return self.__df.to_csv(path)

    def to_pickle(self, path='data/', filename=None):
        if filename:
            with open(abspath(path+filename+".pkl"), "wb") as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        else:
            with open(abspath(path+self.__uuid+".pkl"), "wb") as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_pickle(file):
        with open(abspath(file), 'rb') as f:
            df = pickle.load(f)
            if type(df) is FastQDataframe:
                return df
            else:
                raise TypeError('Pickle is not a FastQDataframe')
