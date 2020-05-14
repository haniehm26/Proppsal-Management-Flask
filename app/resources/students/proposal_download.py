import io

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from flask import abort, send_from_directory

from database.file_handler import fs, fsb
from database.db import mongo
from resources.students.student_proposal import curr_user_is_student


class ProposalDownload(Resource):
    @jwt_required
    def get(self):
        current_user_email = get_jwt_identity()
        if curr_user_is_student(current_user_email):
            students = mongo.db.students
            student = students.find_one({'email': current_user_email})
            if student:
                if fs.exists(filename=student['info_student_id']):
                    proposal_file = fs.find_one({'filename': student['info_student_id']})
                    grid_out = fsb.open_download_stream_by_name(proposal_file.filename)
                    contents = grid_out.read().decode()
                    return download_file(contents, proposal_file.filename)
            else:
                return "Student not found"
        else:
            return "It's prof"


PATH = r"D:/Uni/Term 6/Software/Project/Project-Flask/app/static/download_files/txt/"


def download_file(contents, file_name):
    file_name = file_name + '.txt'
    with io.open(PATH + file_name, "w", encoding="utf-8") as f:
        for lines in contents:
            f.write(lines)
    f.close()
    try:
        return send_from_directory(PATH, filename=file_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)