from extensions import db

class Rule(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rule_string = db.Column(db.String(200), nullable=False) 
    ast = db.Column(db.JSON, nullable=False)