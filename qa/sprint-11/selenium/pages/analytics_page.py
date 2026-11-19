import csv
from pathlib import Path
from .base_page import BasePage


class AnalyticsPage(BasePage):
    def visible_table_rows(self):
        rows=[]
        for row in self.driver.find_elements("css selector", "table tbody tr"):
            values=[cell.text.strip() for cell in row.find_elements("css selector", "th,td")]
            if values: rows.append(values)
        return rows

    @staticmethod
    def csv_rows(path):
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            return [row for row in csv.reader(handle)]

