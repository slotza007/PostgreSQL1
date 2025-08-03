import flask

import models
import forms

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coedb.sqlite"

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )

    # สร้างออบเจกต์ Note
    note = models.Note()
    # Populate เฉพาะฟิลด์ title และ content ซึ่งมาจาก BaseNoteForm
    note.title = form.title.data
    note.content = form.content.data
    
    # ล้าง tags เก่าเพื่อเตรียมเพิ่ม tags ใหม่
    note.tags = []

    db = models.db
    # จัดการฟิลด์ tags ด้วยตัวเอง
    for tag_name in form.tags.data:
        # ค้นหา Tag ที่มีอยู่แล้ว หรือสร้างใหม่ถ้ายังไม่มี
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        # เพิ่ม Tag ลงในรายการ tags ของ Note
        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


# 1. แก้ไขโน้ต
@app.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
def notes_edit(note_id):
    db = models.db
    note = db.session.get(models.Note, note_id)
    if not note:
        return "Note not found", 404

    form = forms.NoteForm(obj=note)
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        note.tags = []
        for tag_name in form.tags.data:
            tag = db.session.execute(
                db.select(models.Tag).where(models.Tag.name == tag_name)
            ).scalar()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)
            note.tags.append(tag)

        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    # สำหรับ GET request, ดึง tags ของโน้ตมาแสดงในฟอร์ม
    form.tags.data = [tag.name for tag in note.tags]

    return flask.render_template("notes-edit.html", form=form, note_id=note_id)


# 3. ลบโน้ต
@app.route("/notes/delete/<int:note_id>", methods=["POST"])
def notes_delete(note_id):
    db = models.db
    note = db.session.get(models.Note, note_id)
    if not note:
        return "Note not found", 404
    
    db.session.delete(note)
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    if not tag:
        return "Tag not found", 404
    
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag=tag,
        notes=notes,
    )


# 2. แก้ไข Tag
@app.route("/tags/edit/<int:tag_id>", methods=["GET", "POST"])
def tags_edit(tag_id):
    db = models.db
    tag = db.session.get(models.Tag, tag_id)
    if not tag:
        return "Tag not found", 404

    class EditTagForm(forms.FlaskForm):
        name = models.db.Column("Tag Name")
        
    form = EditTagForm(obj=tag)

    if form.validate_on_submit():
        form.populate_obj(tag)
        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("tags-edit.html", form=form, tag=tag)

# 4. ลบ Tag
@app.route("/tags/delete/<int:tag_id>", methods=["POST"])
def tags_delete(tag_id):
    db = models.db
    tag = db.session.get(models.Tag, tag_id)
    if not tag:
        return "Tag not found", 404
    
    db.session.delete(tag)
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)