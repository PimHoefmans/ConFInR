import datetime
import os
import re
import uuid
from shutil import rmtree
from flask import render_template, redirect, url_for, session, request, flash
from app.web import bp
from app.web.forms import FastQForm, TSVForm, DatabaseForm
from werkzeug.utils import secure_filename
from app.core.utils.preprocess_utils import allowed_file
from app.core.preprocessing.parser_mp import preprocess_fastq_files_mp
from app.core.diamond.parsers import load_input, convert_to_fasta


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
                renamed_fw_file = 'fw_file.fastq'
                renamed_rc_file = 'rv_file.fastq'
                if not os.path.exists('data/'+session_id):
                    try:
                        os.makedirs('data/'+session_id)
                        form.forward_file.data.save('data/' + session_id + '/' + renamed_fw_file)
                        form.reverse_file.data.save('data/' + session_id + '/' + renamed_rc_file)
                        preprocess_fastq_files_mp('data/' + session_id + '/' + renamed_fw_file, 'data/' + session_id + '/' + renamed_rc_file, session_id)
                        return redirect(url_for('web.preprocessing'))
                    except Exception:
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
    tsv_form = TSVForm()
    db_form = DatabaseForm()

    if tsv_form.validate_on_submit():
        tsv_file = secure_filename(tsv_form.tsv_file.data.filename)
        if allowed_file(tsv_file):
            try:
                session_id = session['id']
            except KeyError:
                session_id = str(uuid.uuid1())
                session['id'] = session_id
            finally:
                input_file = 'input.tsv'
                output_folder = 'data/'+session_id+'/diamond/input'
                input_file_path = '/'.join([output_folder, input_file])
                if not os.path.exists(output_folder):
                    try:
                        os.makedirs(output_folder)
                        tsv_form.tsv_file.data.save(input_file_path)
                        convert_to_fasta(load_input(input_file_path), session_id)
                        flash("File was successfully converted to FASTA and can be used for DIAMOND.")
                        return redirect(url_for('web.confinr'))
                    except Exception:
                        if os.path.exists(output_folder):
                            rmtree(output_folder)
                        flash('An error occurred while parsing the input file, please make sure the '
                              'file conforms to the tsv standard')
                        return redirect(url_for('web.confinr'))
                else:
                    flash("Files are already uploaded")
                    return redirect(url_for('web.confinr'))

    if db_form.validate_on_submit():
        db_file = secure_filename(db_form.db_file.data.filename)
        if allowed_file(db_file):
            try:
                session_id = session['id']
            except KeyError:
                session_id = str(uuid.uuid1())
                session['id'] = session_id
            finally:
                input_file = db_form.name.data+'.fasta'
                output_folder = 'data/'+session_id+'/diamond/database'
                input_file_path = '/'.join([output_folder, input_file])
                if not os.path.exists(output_folder):
                    try:
                        #os.makedirs(output_folder)
                        #db_form.db_file.data.save(input_file_path)
                        #tsv_form.tsv_file.data.save(input_file_pa#h)
                        #convert_to_fasta(load_input(input_file_path), session_id)
                        flash("Database was successfully added and can be used for DIAMOND.")
                        return redirect(url_for('web.confinr'))
                    except Exception:
                        if os.path.exists(output_folder):
                            rmtree(output_folder)
                        flash('An error occurred while parsing the input file, please make sure the '
                              'file conforms to the tsv standard')
                        return redirect(url_for('web.confinr'))
                else:
                    flash("Files are already uploaded")
                    return redirect(url_for('web.confinr'))

    # if db_form.validate_on_submit():
    #     db_file = secure_filename(db_form.db_file.data.filename)
    #     if allowed_file(db_file):
    #         print('SAVE FILE')
    #         # save file in folder
    #         # redirect


    return render_template('confinr.html', tsv_form=tsv_form, db_form=db_form)


@bp.route('/about')
def about():
    return render_template('about.html')
