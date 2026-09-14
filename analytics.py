import matplotlib.pyplot as plt
import sqlite3
from pathlib import Path
import pandas as pd

DB = Path(__file__).resolve().parent / 'tracker.db'

def plot_history():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query('SELECT exercise, reps, duration, timestamp FROM sessions', conn, parse_dates=['timestamp'])
    conn.close()
    if df.empty:
        print('No sessions logged yet. Do some workouts!')
        return
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    summary = df.groupby(['date','exercise'])['reps'].sum().unstack(fill_value=0)
    summary.plot(kind='bar', figsize=(10,6))
    plt.title('Daily Reps by Exercise')
    plt.ylabel('Reps')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    plot_history()
