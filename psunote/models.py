from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ตารางเชื่อมความสัมพันธ์ Many-to-Many ระหว่าง Note และ Tag
note_tag_table = db.Table(
    "note_tag",
    db.Column("note_id", db.Integer, db.ForeignKey("note.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True)
)

class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)  # เพิ่มบรรทัดนี้
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ความสัมพันธ์ Many-to-Many กับ Tag
    tags = db.relationship(
        "Tag",
        secondary=note_tag_table,
        back_populates="notes"
    )

    def __repr__(self):
        return f"<Note {self.title}>"


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # ความสัมพันธ์ Many-to-Many กับ Note
    notes = db.relationship(
        "Note",
        secondary=note_tag_table,
        back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"


def init_app(app):
    """เชื่อมต่อ SQLAlchemy กับ Flask app และสร้างตาราง"""
    db.init_app(app)
    with app.app_context():
        db.create_all()