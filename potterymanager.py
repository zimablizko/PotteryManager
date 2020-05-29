from app import app, db
from app.models import Clay, Item


# создаёт контекст для команды flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Item': Item, 'Clay': Clay}
