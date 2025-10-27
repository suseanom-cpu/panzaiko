# models/inventory.py

import datetime
import pandas as pd

class InventoryManager:
    def __init__(self):
        self.pans = ["細パン", "太パン", "サンドパン", "バゲット"]
        self.shelf_life = 3  # 日数

    def update_inventory(self, purchase_data, leftover_data, current_stock):
        """
        purchase_data: {'細パン': 10, '太パン': 8, ...}
        leftover_data: {'細パン': 2, '太パン': 3, ...}
        current_stock: {'細パン': 5, '太パン': 2, ...}
        """
        next_order = {}

        for pan in self.pans:
            # 消費率を計算
            consumed = purchase_data[pan] - leftover_data[pan]
            avg_consumption = (consumed + current_stock[pan]) / 2

            # 次の日に必要な数を予測
            next_order[pan] = max(0, int(avg_consumption - current_stock[pan]))

        return next_order

    def get_expiry_status(self, baked_date):
        """
        焼いた日付を基に、消費期限や残り日数を算出
        """
        today = datetime.date.today()
        delta = (today - baked_date).days
        remain = self.shelf_life - delta

        if remain <= 0:
            return "今日廃棄"
        elif remain == 1:
            return "+1日"
        else:
            return f"残り{remain}日"
