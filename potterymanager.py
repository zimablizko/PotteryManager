from app import app, db
from app.models import Clay, Item

print(app.name)

# создаёт контекст для команды flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Item': Item, 'Clay': Clay}
