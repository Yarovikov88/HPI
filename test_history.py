import os
from src.dashboard.parsers.history import HistoryParser
import logging

logging.basicConfig(level=logging.INFO)

# Определяем корень проекта
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports_final')

parser = HistoryParser(REPORTS_DIR)
history = parser.get_history()

print("История значений HPI:")
for report in history:
    print(f"{report.date}: {report.hpi}") 