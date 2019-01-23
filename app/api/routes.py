from flask import jsonify, request, session, send_file, abort, flash, redirect, url_for
import dask.dataframe as dd
import json
import io
import os
import zipfile
import logging
from app.api import bp
from subprocess import call
from app.web.forms import db_none_chosen
from app.core.objects.FastQDataframe import FastQDataframe
from app.core.utils.to_json import seq_length_to_json, perc_count_to_json, \
    get_paired_percentage_to_json, nucleotide_percentages_to_json
from app.core.bowtie2.Bowtie2_controller import bowtie2_builder, bowtie2_aligner
from app.core.bowtie2.Bowtie2_result_parser import bowtie2_output_parser
from datetime import datetime
from config import Config


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


@bp.route('/diamond', methods=['POST'])
def run_diamond():
    """
        Endpoint for running DIAMOND.
        """
    parameters = {
        "--algo": request.form.get("algorithm"),
        "--compress": request.form.get("compress"),
        "--evalue": request.form.get("evalue"),
        "--frameshift": request.form.get("frameshift"),
        "--gapextend": request.form.get("gapExtend"),
        "--gapopen": request.form.get("gapOpen"),
        "--id": request.form.get("id"),
        "--matrix": request.form.get("matrix"),
        "--max-hsps": request.form.get("maxHSPS"),
        "--max-target-seqs": request.form.get("maxTargetSeqs"),
        "--min-score": request.form.get("minScore"),
        "--outfmt": request.form.get("outfmt"),
        "--query-cover": request.form.get("queryCover"),
        "--sensitive": request.form.get("sensitive"),
        "--more-sensitive": request.form.get("moreSensitive"),
        "--subject-cover": request.form.get("subjectCover")
    }
    try:
        session_id = session['id']
        session_db = session['db_choice']
        if os.path.exists('data/' + session_id + '/diamond/query/query.fasta'):
            query = 'data/' + session_id + '/diamond/query/query.fasta'
        elif os.path.exists('data/' + session_id + '/diamond/query/query.fastq'):
            query = 'data/' + session_id + '/diamond/query/query.fastq'
        else:
            flash("No query file was found, please ensure that one was uploaded.")
            return redirect(url_for('web.confinr'))

        if os.path.exists('data/' + session_id + '/diamond/database/db.dmnd'):
            db = 'data/' + session_id + '/diamond/query/query.fasta'
        elif session['db_choice'] != '':
            db = Config.DB_PATH+session_db
        else:
            flash("No database file was found, please ensure that one was uploaded or selected.")
            return redirect(url_for('web.confinr'))

        if not os.path.exists('data/' + session_id + '/diamond/output'):
            os.makedirs('data/' + session_id + '/diamond/output')
        out = 'data/' + session_id + '/diamond/output/diamond.m8'

        command = 'diamond blastx -d ' + db + ' -q ' + query + ' -o ' + out

        command_params = ""
        for key, value in parameters.items():
            if key == "--sensitive" or key == "--more-sensitive":
                if value.lower() != "false":
                    command_params += " " + key
            else:
                if value != "":
                    command_params += " " + key + " " + value
        if command_params != "":
            command += command_params

        call(command, shell=True)
        # FIXME: Create response
        return "diamond completed"
    except KeyError:
        abort(400)
    except Exception:
        abort(500)


# METAGEN-56 | METAGEN-71 | METAGEN-158
@bp.route('/nucleotide', methods=['POST'])
def nucleotide():
    """
    Endpoint for getting filtered data about nucleotide ratios
    :return: json object
    """
    try:
        session_id = session['id']
        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")

        # Obtain data from ajax post request
        min_A_perc = int(request.form.get('minAValue'))
        min_T_perc = int(request.form.get('minTValue'))
        min_G_perc = int(request.form.get('minGValue'))
        min_C_perc = int(request.form.get('minCValue'))
        max_A_perc = int(request.form.get('maxAValue'))
        max_T_perc = int(request.form.get('maxTValue'))
        max_G_perc = int(request.form.get('maxGValue'))
        max_C_perc = int(request.form.get('maxCValue'))
        bin_size = int(request.form.get('BinSize'))

        # Flag the dataframe for the individual nucleotide percentages
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

        # Aggregate the individual flags as a result for the column flagged
        fastq_df['flagged'] = fastq_df[['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag',
                                        'fw_c_perc_flag', 'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag',
                                        'rv_c_perc_flag', 'fw_seq_len_flag', 'rv_seq_len_flag', 'identity_flag']].any(
                                        axis=1)

        # Save dask dataframe
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
        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")

        fastq_df['identity_flag'] = fastq_df['overlap_identity_perc'].apply(
            lambda row: False if iden_perc <= row else True, meta=(bool))

        fastq_df['flagged'] = fastq_df[['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag',
                                        'fw_c_perc_flag', 'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag',
                                        'rv_c_perc_flag', 'fw_seq_len_flag', 'rv_seq_len_flag', 'identity_flag']].any(
                                        axis=1)

        filtered_df = fastq_df[fastq_df['flagged'] == False]
        subset = filtered_df.round().groupby(['overlap_identity_perc']).overlap_identity_perc.count()

        fastq_df.to_parquet('data/' + session_id + '/parquet/', engine="pyarrow", write_index=True)
        response = perc_count_to_json(subset)
        return jsonify(response)
    except KeyError as e:
        logging.exception(e)
        abort(400)
    except Exception as e:
        logging.exception(e)
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
        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")

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
        if not os.path.exists("data/"+session_id+"/tsv"):
            os.makedirs("data/"+session_id+"/tsv")

        fastq_df.drop(['paired_flag', 'fw_a_perc_flag', 'fw_t_perc_flag', 'fw_g_perc_flag', 'fw_c_perc_flag',
                       'rv_a_perc_flag', 'rv_t_perc_flag', 'rv_g_perc_flag', 'rv_c_perc_flag', 'fw_seq_len_flag',
                       'rv_seq_len_flag', 'identity_flag'], axis=1).to_csv('data/' + session_id + "/tsv/export-*.tsv", sep="\t")

        mem = io.BytesIO()
        zipf = zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED)
        # Creating a metadata file for the user to know which filters were used
        zipf.writestr(
            zinfo_or_arcname="FILTERDATA.txt", data=
            "The following columns are filtered on these numbers\n"
            "min_seq_len:" + str(min_seq_len) + " | max_seq_len:" + str(max_seq_len) + " | filter_paired:" + str(
                filter_paired) +
            " | min_A_perc:" + str(minA) + " | max_A_perc:" + str(maxA) + " | min_T_perc:" + str(
                minT) + " | max_T_perc:" + str(maxT) +
            " | min_G_perc:" + str(minG) + " | max_G_perc:" + str(maxG) + " | min_C_perc:" + str(
                minC) + " | max_C_perc:"
            + str(maxC) + " | paired_read_percentages:" + str(paired_read_percentage)
            + "\nIn the column flagged, True means it's filtered out, False means it's a good sequence\n")
        # add the csv files to the zip
        zip_files('data/'+session_id+'/tsv/', zipf)
        zipf.close()
        # Make sure that the file pointer is positioned at the start of data to send before calling send_file().
        mem.seek(0)
        return send_file(mem,
                         attachment_filename='ConFInR_export_data-'+datetime.now().strftime("%Y%m%d-%H%M")+'.zip',
                         as_attachment=True)
    except KeyError as e:
        logging.exception(e)
        abort(400)
    except Exception as e:
        logging.exception(e)
        abort(500)


def zip_files(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), arcname=file)


@bp.route("/calc_identity", methods=["POST"])
def call_identity():
    try:
        calculate = "True"
        session_id = session['id']
        fastq_df = dd.read_parquet('data/' + session_id + '/parquet/', engine="pyarrow")
        for root, dirs, files in os.walk("data/"+ session_id):
            if "fw_file.fastq" in files:
                fw_fastq_file = os.path.join(root, "fw_file.fastq")
            if "rv_file.fastq" in files:
                rv_fastq_file = os.path.join(root, "rv_file.fastq")
        if "overlap_identity_perc" in fastq_df.columns:
            calculate = "False"
        else:
            bowtie2_builder(fw_fastq_file)
            bowtie2_aligner(fw_fastq_file, rv_fastq_file)
            fastq_df = bowtie2_output_parser(fastq_df)
            fastq_df.to_parquet('data/' + session_id + '/parquet/', engine="pyarrow", write_index=True)
        return calculate
    except KeyError as e:
        logging.exception(e)
        abort(400)
    except Exception as e :
        logging.exception(e)
        abort(500)
