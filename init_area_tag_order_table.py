from src.database.db_manager import DBManager

def init_db():
    db = DBManager()
    db.ensure_area_tag_orders_table()
    print("Table area_tag_orders ensured.")

if __name__ == "__main__":
    init_db()
