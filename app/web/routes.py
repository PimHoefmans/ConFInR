import datetime
import os
import re
import uuid
import logging
from shutil import rmtree
from flask import render_template, redirect, url_for, session, request, flash
from app.web import bp
from app.web.forms import FastQForm, DiamondInputForm, db_none_chosen
from werkzeug.utils import secure_filename
from app.core.utils.preprocess_utils import allowed_file
from app.core.preprocessing.parser_mp import preprocess_fastq_files_mp
from app.core.diamond.parsers import load_input, merge_input, convert_to_fasta
from app.core.diamond.runner import make_diamond_db


last_purge = None


@bp.before_request
def before_request():
    global last_purge
    now = datetime.datetime.now()

    try:
        if last_purge:
            delta = now - last_purge
            if delta.seconds > 3600:
                for dir in os.listdir(os.path.abspath("data/")):
                    if re.search("([a-zA-Z0-9_]+-)+([a-zA-Z0-9_]+)", dir):
                        for file in os.listdir(os.path.abspath("data/"+dir)):
                            print(os.path.join(os.path.abspath("data/"+dir), file), "automatically removed")
                            os.remove(os.path.join(os.path.abspath("data/"+dir), file))

                last_purge = now
        else:
            last_purge = now
    except:
        pass


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/preprocessing', methods=['GET', 'POST'])
def preprocessing():
    form = FastQForm()

    if form.validate_on_submit():
        fw_file = secure_filename(form.forward_file.data.filename)
        rv_file = secure_filename(form.reverse_file.data.filename)
        if allowed_file(fw_file) and allowed_file(rv_file):
            try:
                session_id = session['id']
            except KeyError:
                session_id = str(uuid.uuid1())
                session['id'] = session_id
            finally:
                renamed_fw_file = 'fw_file.'+fw_file.rsplit('.', 1)[1].lower()
                renamed_rc_file = 'rv_file.'+rv_file.rsplit('.', 1)[1].lower()
                if not os.path.exists('data/'+session_id):
                    try:
                        os.makedirs('data/'+session_id)
                        form.forward_file.data.save('data/' + session_id + '/' + renamed_fw_file)
                        form.reverse_file.data.save('data/' + session_id + '/' + renamed_rc_file)
                        preprocess_fastq_files_mp('data/' + session_id + '/' + renamed_fw_file, 'data/' + session_id + '/' + renamed_rc_file, session_id)
                        flash('Files were successfully uploaded!')
                        return redirect(url_for('web.preprocessing'))
                    except Exception as e:
                        logging.exception(e)
                        if os.path.exists('data/'+session_id):
                            rmtree('data/'+session_id)
                        session.clear()
                        flash('An error occurred while parsing the input files, please make sure the '
                              'files conform the fastq standard')
                        return redirect(url_for('web.preprocessing'))
                else:
                    flash("Files are already uploaded")
                    return redirect(url_for('web.preprocessing'))
        else:
            flash('Unsupported file types')
            return redirect(url_for('web.preprocessing'))

    return render_template('preprocessing.html', form=form)


@bp.route('/confinr', methods=['GET', 'POST'])
def confinr():
    diamond_input_form = DiamondInputForm()
    query_uploaded = False
    db_uploaded = False
    if diamond_input_form.validate_on_submit():
        query_file = secure_filename(diamond_input_form.query_file.data.filename)
        db_choice = diamond_input_form.db_choice.data
        try:
            db_file = secure_filename(diamond_input_form.db_file.data.filename)
        except AttributeError:
            db_file = None

        if allowed_file(query_file):
            try:
                session_id = session['id']
            except KeyError:
                session_id = str(uuid.uuid1())
                session['id'] = session_id
            finally:
                for extension in ['.fasta', '.fastq', '.gz', '.tsv', '.zip']:
                    if extension in query_file:
                        query_storage_file = 'query'+extension
                        query_storage_folder = 'data/' + session_id + '/diamond/query'
                        query_storage_file_path = '/'.join([query_storage_folder, query_storage_file])
                        if not os.path.exists(query_storage_folder):
                            try:
                                os.makedirs(query_storage_folder)
                                diamond_input_form.query_file.data.save(query_storage_file_path)
                                if any(ext in query_storage_file for ext in ['.tsv']):
                                    convert_to_fasta(load_input(query_storage_file_path), session_id)
                                elif any(ext in query_storage_file for ext in ['.zip']):
                                    import sys
                                    print('ZIP detetected', file=sys.stderr)
                                    convert_to_fasta(merge_input(query_storage_file_path), session_id)
                                query_uploaded = True
                            except Exception:
                                if os.path.exists(query_storage_folder):
                                    rmtree(query_storage_folder)
                                flash('An error occurred while parsing the query file. Please make sure the file'
                                      'conforms to the required data formats.')
                                return redirect(url_for('web.confinr'))
                        else:
                            flash("File is already uploaded")
                            return redirect(url_for('web.confinr'))

                if db_file is not None and allowed_file(db_file):
                    if db_choice == db_none_chosen:
                        for extension in ['.dmnd', '.fasta', '.gz']:
                            if extension in db_file:
                                db_storage_file = 'db'+extension
                                db_storage_folder = 'data/' + session_id + '/diamond/database'
                                db_storage_file_path = '/'.join([db_storage_folder, db_storage_file])
                                if not os.path.exists(db_storage_folder):
                                    try:
                                        os.makedirs(db_storage_folder)
                                        diamond_input_form.db_file.data.save(db_storage_file_path)
                                        if any(ext in db_storage_file_path for ext in ['.fasta', '.gz']):
                                            make_diamond_db(session_id)
                                        db_uploaded = True
                                        session['db_choice'] = db_none_chosen
                                    except Exception:
                                        if os.path.exists(db_storage_folder):
                                            rmtree(db_storage_folder)
                                        flash('An error occurred while parsing the query file. Please make sure the'
                                              'file conforms to the required data formats.')
                                        return redirect(url_for('web.confinr'))
                                else:
                                    flash("File is already uploaded")
                                    return redirect(url_for('web.confinr'))
                    else:
                        flash('Both a database file and an existing database are selected, please select only one.')
                        return redirect(url_for('web.confinr'))

                if db_file is None and db_choice == db_none_chosen:
                    flash('Neither a database file or an existing database are selected, please select one.')
                    return redirect(url_for('web.confinr'))

                if db_file is None and db_choice != db_none_chosen:
                    session['db_choice'] = db_choice

                if query_uploaded and db_uploaded:
                    flash('Both files have successfully been uploaded and processed.')
                if query_uploaded and not db_uploaded and db_choice != db_none_chosen:
                    flash('The query file has successfully been uploaded and processed.'
                          '\nAn existing database has been selected.')
                if query_uploaded and not db_uploaded and db_choice == db_none_chosen:
                    flash('The query file has successfully been uploaded and processed.'
                          '\nAn error occurred with the database file.')
                if not query_uploaded and db_uploaded and db_choice == db_none_chosen:
                    flash('The database file has successfully been uploaded and processed.'
                          '\nAn error occurred with the query file.')
                return redirect(url_for('web.confinr'))
    return render_template('confinr.html', db_input_form=diamond_input_form)


@bp.route('/about')
def about():
return render_template('about.html')
