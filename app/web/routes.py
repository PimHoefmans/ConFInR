import datetime
import os
import re
import uuid
from shutil import rmtree
from flask import render_template, redirect, url_for, session, request, flash
from app.web import bp
from app.web.forms import FastQForm, TSVForm, DiamondDBForm, RunDiamondForm, DiamondForm
from werkzeug.utils import secure_filename
from app.core.utils.preprocess_utils import allowed_file
from app.core.preprocessing.parser import preprocess_fastq_files
from app.core.preprocessing.parser_mp import preprocess_fastq_files_mp


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
    #if tsv_form.validate_on_submit():
        # tsv_file = secure_filename(tsv_form.tsv_file.data.filename)
        # if allowed_file(tsv_file):
        # save file in right folder
        # redirect(url_for('web.confinr'))
    form = DiamondForm
    return render_template('confinr_template.html')


bp.route


@bp.route('/about')
def about():
    return render_template('about.html')
