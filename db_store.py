import sqlite3

class DBStore:
    def __init__(self):
        self._conn = sqlite3.connect('yelp_data.db')

    def save_menu_items(self, biz_id, items):
        items = map(lambda item: item.replace(';', ','), items)
        items_list = ';'.join(items)
        self._conn.execute(
            'INSERT INTO menu_items (id, items) VALUES (?, ?)',
            (biz_id, items_list)
            )
        self._conn.commit()

    def get_menu_items(self, biz_id):
        cursor = self._conn.execute(
            'SELECT items FROM menu_items WHERE id=?',
            (biz_id, )
            )
        row = cursor.fetchone()
        if row == None: return None
        if row[0] == '': return []
        return row[0].split(';')

    def save_reviews(self, biz_id, reviews):
        reviews = map(lambda r: (biz_id, int(r[0]), r[1]), reviews)
        self._conn.executemany(
            'INSERT INTO reviews (id, rating, review) VALUES (?, ?, ?)',
            reviews
            )
        self._conn.commit()

    def get_reviews(self, biz_id):
        cursor = self._conn.execute(
            'SELECT rating, review FROM reviews WHERE id=?',
            (biz_id, )
            )
        return cursor.fetchall()
