import io
import json
import logging

import dask.dataframe as dd
from flask import jsonify, request, session, send_file, abort

from app.api import bp
from app.core.objects.FastQDataframe import FastQDataframe
from app.core.utils.to_json import seq_length_to_json, perc_count_to_json, \
    get_paired_percentage_to_json, nucleotide_percentages_to_json


# METAGEN-55 | METAGEN-70
@bp.route('/sequence', methods=['POST'])
def sequence_length():
    """
    Endpoint for getting filtered sequence length data from the FastQDataframe
    :return: json object containing forward and reverse sequence length data
    """
    try:
        session_id = session['id']
        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")
        min_seq_len = int(request.form.get('min_seq_len'))
        max_seq_len = int(request.form.get('max_seq_len'))
        fastq_df['fw_seq_len_flag'] = fastq_df['fw_seq_length'].apply(
            lambda row: False if min_seq_len <= row <= max_seq_len else True, meta=(bool))
        fastq_df['rv_seq_len_flag'] = fastq_df['rv_seq_length'].apply(
            lambda row: False if min_seq_len <= row <= max_seq_len else True, meta=(bool))
        fastq_df['flagged'] = fastq_df[['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag',
                                        'fw_c_perc_flag', 'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag',
                                        'rv_c_perc_flag', 'fw_seq_len_flag', 'rv_seq_len_flag', 'identity_flag']].any(
            axis=1)

        fastq_df.to_parquet('data/' + session_id + '/parquet/', engine="pyarrow", write_index=True)

        subset = fastq_df[fastq_df['flagged'] == False]
        response = seq_length_to_json(subset[['fw_seq_length', 'rv_seq_length']].compute())
        return response
    except KeyError as e:
        logging.exception(e)
        abort(400)
    except Exception as e:
        logging.exception(e)
        abort(500)


# METAGEN-56 | METAGEN-71 | METAGEN-158
@bp.route('/nucleotide', methods=['POST'])
def nucleotide():
    """
    Endpoint for getting filtered data about nucleotide ratio's
    Added: Now possible to filter on a specific nucleotide
    :return: json object
    """
    try:
        session_id = session['id']
        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")
        min_A_perc = int(request.form.get('minAValue'))
        min_T_perc = int(request.form.get('minTValue'))
        min_G_perc = int(request.form.get('minGValue'))
        min_C_perc = int(request.form.get('minCValue'))
        max_A_perc = int(request.form.get('maxAValue'))
        max_T_perc = int(request.form.get('maxTValue'))
        max_G_perc = int(request.form.get('maxGValue'))
        max_C_perc = int(request.form.get('maxCValue'))
        bin_size = int(request.form.get('BinSize'))
        print(fastq_df.columns)
        fastq_df['fw_A_flag'] = fastq_df['fw_A_perc'].apply(
            lambda row: False if min_A_perc <= row <= max_A_perc else True, meta=(bool))
        fastq_df['fw_T_flag'] = fastq_df['fw_T_perc'].apply(
            lambda row: False if min_T_perc <= row <= max_T_perc else True, meta=(bool))
        fastq_df['fw_G_flag'] = fastq_df['fw_G_perc'].apply(
            lambda row: False if min_G_perc <= row <= max_G_perc else True, meta=(bool))
        fastq_df['fw_C_flag'] = fastq_df['fw_C_perc'].apply(
            lambda row: False if min_C_perc <= row <= max_C_perc else True, meta=(bool))
        fastq_df['rv_A_flag'] = fastq_df['rv_A_perc'].apply(
            lambda row: False if min_A_perc <= row <= max_A_perc else True, meta=(bool))
        fastq_df['rv_T_flag'] = fastq_df['rv_T_perc'].apply(
            lambda row: False if min_T_perc <= row <= max_T_perc else True, meta=(bool))
        fastq_df['rv_G_flag'] = fastq_df['rv_G_perc'].apply(
            lambda row: False if min_G_perc <= row <= max_G_perc else True, meta=(bool))
        fastq_df['rv_C_flag'] = fastq_df['rv_C_perc'].apply(
            lambda row: False if min_C_perc <= row <= max_C_perc else True, meta=(bool))

        fastq_df['flagged'] = fastq_df[['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag',
                                        'fw_c_perc_flag', 'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag',
                                        'rv_c_perc_flag', 'fw_seq_len_flag', 'rv_seq_len_flag', 'identity_flag']].any(
            axis=1)
        fastq_df.to_parquet('data/' + session_id + '/parquet/', engine="pyarrow", write_index=True)
        subset = fastq_df[fastq_df['flagged'] == False]
        fw_json = nucleotide_percentages_to_json(subset[['fw_A_perc', 'fw_T_perc', 'fw_C_perc', 'fw_G_perc']].compute(),
                                                 bin_size, "fw_")
        rv_json = nucleotide_percentages_to_json(subset[['rv_A_perc', 'rv_T_perc', 'rv_C_perc', 'rv_G_perc']].compute(),
                                                 bin_size, "rv_")
        response = json.dumps({"fw_json": fw_json, "rvc_json": rv_json})
        return response
    except KeyError as e:
        logging.exception(e)
        abort(400)
    except Exception as e:
        logging.exception(e)
        abort(500)


# METAGEN-57 | METAGEN-72
@bp.route('/quality', methods=['POST'])
def quality():
    """
    Endpoint for getting a subset of the dataframe filtered on a quality score
    :return: json object
    """
    try:
        session_id = session['id']
        fastq_df = FastQDataframe.load_pickle("data/" + session_id + "/pickle.pkl")
        response = request.form.get('qValue')
        return jsonify(response)
    except KeyError as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)


# METAGEN-59 | METAGEN-74
@bp.route('/paired', methods=['POST'])
def paired():
    """
    Endpoint for getting a subset containing only paired reads
    :return: json object for a image
    """
    try:
        session_id = session['id']
        filter_paired = bool(request.form.get('FilterPaired'))

        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")
        fastq_df['paired_flag'] = fastq_df['paired'].apply(lambda row: False if row == True else True, meta=(bool))
        fastq_df['flagged'] = fastq_df[['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag',
                                        'fw_c_perc_flag', 'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag',
                                        'rv_c_perc_flag', 'fw_seq_len_flag', 'rv_seq_len_flag', 'identity_flag']].any(
            axis=1)
        fastq_df.to_parquet('data/' + session_id + '/parquet/', engine="pyarrow", write_index=True)
        response = get_paired_percentage_to_json(fastq_df)
        return response

    except KeyError as e:
        logging.exception(e)
        abort(400)
    except Exception as e:
        logging.exception(e)
        abort(500)


# METAGEN-58 | METAGEN-73
@bp.route('/identity', methods=['POST'])
def identity():
    """
    Endpoint for filtering the dataframe on identity score and getting json data for an image
    :return: json object
    """

    try:
        iden_perc = int(request.form.get('paired_read_percentage'))
        session_id = session['id']
        fastq_df = FastQDataframe.load_pickle("data/" + session_id + "/pickle.pkl")
        fastq_df.flag_greater_than('identity', iden_perc, 'identity_flag')
        fastq_df.flag_any()
        filtered_df = fastq_df.filter_equals(False, ['flagged'])

        subset = filtered_df.round().groupby(['identity']).identity.count()
        fastq_df.to_pickle(path='data/' + session_id + '/', filename='pickle')

        response = perc_count_to_json(subset)
        return jsonify(response)
    except KeyError:
        abort(400)
    except Exception:
        abort(500)


# METAGEN-173
@bp.route('/export_tsv', methods=['GET'])
def export_tsv():
    """
    Endpoint for returning a TSV file of the dataframe
    :return: tsv file
    """

    try:
        session_id = session['id']
        fastq_df = FastQDataframe.load_pickle("data/" + session_id + "/pickle.pkl").get_dataframe()

        min_seq_len = request.args.get('minSL', 0, int)
        max_seq_len = request.args.get('maxSL', 10000, int)
        filter_paired = request.args.get('filterP', True, bool)
        minA = request.args.get('minA', 0, int)
        minT = request.args.get('minT', 0, int)
        minG = request.args.get('minG', 0, int)
        minC = request.args.get('minC', 0, int)
        maxA = request.args.get('maxA', 100, int)
        maxT = request.args.get('maxT', 100, int)
        maxG = request.args.get('maxG', 100, int)
        maxC = request.args.get('maxC', 100, int)
        paired_read_percentage = request.args.get('pairedRP', 0, int)

        buffer = io.StringIO()
        buffer.write(
            "#min_seq_len:" + str(min_seq_len) + " | max_seq_len:" + str(max_seq_len) + " | filter_paired:" + str(
                filter_paired) +
            " | min_A_perc:" + str(minA) + " | max_A_perc:" + str(maxA) + " | min_T_perc:" + str(
                minT) + " | max_T_perc:" + str(maxT) +
            " | min_G_perc:" + str(minG) + " | max_G_perc:" + str(maxG) + " | min_C_perc:" + str(
                minC) + " | max_C_perc:"
            + str(maxC) + " | paired_read_percentages:" + str(paired_read_percentage)
            + "\n#column flagged; True means it's filtered, False means it's a good sequence\n")
        fastq_df.drop(['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag', 'fw_c_perc_flag',
                       'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag', 'rv_c_perc_flag', 'fw_seq_len_flag',
                       'rv_seq_len_flag', 'identity_flag'], axis=1).to_csv(buffer, sep='\t', index=True, header=True)

        mem = io.BytesIO()
        mem.write(buffer.getvalue().encode('utf-8'))
        mem.seek(0)
        buffer.close()
        return send_file(mem,
                         mimetype='text/tsv',
                         attachment_filename='YEET_export_data.tsv',
                         as_attachment=True)
    except KeyError:
        abort(400)
    except Exception:
        abort(500)
