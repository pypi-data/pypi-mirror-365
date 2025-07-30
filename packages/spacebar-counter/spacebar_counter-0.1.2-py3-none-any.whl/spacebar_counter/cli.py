import os
import json
from datetime import datetime, date
from pynput import keyboard
import typer
import plotly.graph_objs as go

app = typer.Typer()

def get_data_dir():
    home = os.path.expanduser("~")
    data_dir = os.path.join(home, "spacebar_counter")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

STATS_FILE = os.path.join(get_data_dir(), 'spacebar_stats.json')
DASHBOARD_FILE = os.path.join(get_data_dir(), 'spacebar_dashboard.html')

@app.command()
def start():
    def get_today():
        return str(date.today())

    stats = {}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            try:
                stats = json.load(f)
            except Exception:
                stats = {}
    today = get_today()
    count = stats.get(today, {}).get('count', 0)
    first_press = stats.get(today, {}).get('first_press', None)
    last_press = stats.get(today, {}).get('last_press', None)

    def on_press(key):
        nonlocal count, first_press, last_press, stats, today
        current_day = get_today()
        if current_day != today:
            today = current_day
            count = 0
            first_press = None
            last_press = None
        if key == keyboard.Key.space:
            count += 1
            now = datetime.now().isoformat(timespec='seconds')
            if not first_press:
                first_press = now
            last_press = now
            stats[today] = {
                'count': count,
                'first_press': first_press,
                'last_press': last_press
            }
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f, indent=2)
            print(f"{today} | Spacebar count: {count} | First: {first_press} | Last: {last_press}")

    with keyboard.Listener(on_press=on_press) as listener:
        print("Press the spacebar. Press Ctrl+C to exit.")
        listener.join()

@app.command()
def dashboard():
    if not os.path.exists(STATS_FILE):
        print("No stats file found. Run 'spacebar-counter start' first.")
        return
    with open(STATS_FILE, 'r') as f:
        stats = json.load(f)
    if not stats:
        print("No data to display.")
        return
    days = list(stats.keys())
    counts = [stats[day]['count'] for day in days]
    firsts = [stats[day]['first_press'] for day in days]
    lasts = [stats[day]['last_press'] for day in days]
    hover_text = [f"First: {f}<br>Last: {l}" for f, l in zip(firsts, lasts)]
    fig = go.Figure([go.Scatter(x=days, y=counts, mode='markers', marker=dict(size=12), text=hover_text, hoverinfo='text+name', name='Spacebar Count')])
    fig.update_layout(title="Spacebar Hits Per Day", xaxis_title="Date", yaxis_title="Hits")
    fig.write_html(DASHBOARD_FILE)
    print(f"Dashboard saved to {DASHBOARD_FILE}")

if __name__ == "__main__":
    app() 