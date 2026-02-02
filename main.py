import os
import requests
import time
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# --- PODESAVANJA ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ODDS_API_KEY = os.environ.get("ODDS_API_KEY")

izvestaj = "🎯 *KAI SNIPER v12.4 (NOVI NALOG)* 🎯\n"
izvestaj += f"📅 *{time.strftime('%d.%m.%Y')}* (Anti-Crash Sistem)\n"
izvestaj += "-----------------------------------\n"

global_tiket = []

STAR_PLAYERS = {
    "celtics": "J. Tatum", "bucks": "G. Antetokounmpo", "76ers": "J. Embiid", 
    "magic": "P. Banchero", "heat": "J. Butler", "pacers": "T. Haliburton", 
    "knicks": "J. Brunson", "cavaliers": "D. Mitchell", "nets": "C. Thomas", 
    "hawks": "T. Young", "raptors": "S. Barnes", "bulls": "Z. LaVine", 
    "hornets": "L. Ball", "wizards": "J. Poole", "pistons": "C. Cunningham", 
    "timberwolves": "A. Edwards", "thunder": "S. Gilgeous-Alexander", 
    "nuggets": "N. Jokic", "clippers": "J. Harden", "kings": "D. Fox", 
    "suns": "K. Durant", "pelicans": "Z. Williamson", 
    "mavericks": "C. Flagg", "lakers": "L. Doncic", 
    "warriors": "S. Curry", "rockets": "A. Sengun", "jazz": "L. Markkanen", 
    "grizzlies": "J. Morant", "trail blazers": "A. Simons", "spurs": "V. Wembanyama"
}

def posalji_telegram(tekst):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    if len(tekst) > 4000:
        delovi = [tekst[i:i+4000] for i in range(0, len(tekst), 4000)]
        for deo in delovi:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": deo, "parse_mode": "Markdown"}
            requests.post(url, json=payload)
            time.sleep(1)
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": tekst, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

def is_match_today(commence_time_str):
    try:
        match_date = datetime.strptime(commence_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if match_date.date() == now.date(): return True
        if (match_date - now).total_seconds() < 14 * 3600 and (match_date - now).total_seconds() > -4 * 3600: return True
        return False
    except: return True

def clean_team_name(name):
    words = name.split()
    return words[-1] if len(words) > 1 else name

def get_confidence_bar(diff):
    if diff >= 10: return "🟩🟩🟩🟩🟩 (TOP!)"
    elif diff >= 7: return "🟩🟩🟩🟩⬜ (Jako)"
    elif diff >= 5: return "🟩🟩🟩⬜⬜ (Srednje)"
    else: return "🟩🟩⬜⬜⬜ (Rizično)"

def get_stake_diamonds(diff):
    if diff >= 9: return "💎💎💎 (Max Bet)"
    elif diff >= 6: return "💎💎 (Srednji)"
    else: return "💎 (Oprezno)"

def get_live_standings_cbs():
    form_data = {}
    try:
        url = "https://www.cbssports.com/nba/standings/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            rows = soup.find_all('tr')
            for row in rows:
                text_row = row.get_text()
                found_team = None
                for team in STAR_PLAYERS.keys():
                    if team in text_row.lower():
                        found_team = team; break
                if found_team:
                    streak_match = re.search(r'(W|L)\s?(\d+)', text_row)
                    if streak_match:
                        type_s = streak_match.group(1)
                        count_s = int(streak_match.group(2))
                        form_data[found_team] = {'is_winning': (type_s == 'W'), 'streak': count_s}
    except: return None
    return form_data

def get_nba_stats():
    return {
        "Boston Celtics": {'OFF': 120.8, 'DEF': 110.5}, "Oklahoma City Thunder": {'OFF': 121.5, 'DEF': 111.0},
        "Milwaukee Bucks": {'OFF': 122.0, 'DEF': 117.5}, "Minnesota Timberwolves": {'OFF': 113.5, 'DEF': 106.8},
        "Denver Nuggets": {'OFF': 114.8, 'DEF': 111.2}, "LA Clippers": {'OFF': 117.5, 'DEF': 113.0},
        "Cleveland Cavaliers": {'OFF': 114.5, 'DEF': 109.5}, "New York Knicks": {'OFF': 115.0, 'DEF': 112.0},
        "Phoenix Suns": {'OFF': 117.2, 'DEF': 114.5}, "Indiana Pacers": {'OFF': 123.5, 'DEF': 122.0},
        "Los Angeles Lakers": {'OFF': 117.0, 'DEF': 116.5}, "Golden State Warriors": {'OFF': 118.5, 'DEF': 117.0},
        "Sacramento Kings": {'OFF': 118.0, 'DEF': 117.5}, "Dallas Mavericks": {'OFF': 118.2, 'DEF': 116.8},
        "Miami Heat": {'OFF': 110.5, 'DEF': 109.8}, "Orlando Magic": {'OFF': 111.5, 'DEF': 109.5},
        "Philadelphia 76ers": {'OFF': 115.5, 'DEF': 113.5}, "New Orleans Pelicans": {'OFF': 116.0, 'DEF': 112.5},
        "Houston Rockets": {'OFF': 113.8, 'DEF': 112.8}, "Atlanta Hawks": {'OFF': 120.5, 'DEF': 123.0},
        "Brooklyn Nets": {'OFF': 112.5, 'DEF': 115.5}, "Utah Jazz": {'OFF': 116.5, 'DEF': 120.0},
        "Toronto Raptors": {'OFF': 114.0, 'DEF': 118.0}, "Memphis Grizzlies": {'OFF': 108.5, 'DEF': 112.5},
        "Chicago Bulls": {'OFF': 111.5, 'DEF': 113.0}, "San Antonio Spurs": {'OFF': 112.5, 'DEF': 119.0},
        "Portland Trail Blazers": {'OFF': 108.0, 'DEF': 116.5}, "Charlotte Hornets": {'OFF': 109.5, 'DEF': 120.5},
        "Washington Wizards": {'OFF': 114.5, 'DEF': 124.0}, "Detroit Pistons": {'OFF': 110.5, 'DEF': 121.0}
    }

def match_team_stats(odds_name, stats_dict):
    odds_clean = re.sub(r'[^a-zA-Z]', '', odds_name).lower()
    overrides = {"sixers": "76ers", "76ers": "76ers", "cavs": "cavaliers", "ny": "knicks", "bk": "nets", "la": "lakers", "losangeles": "lakers", "gs": "warriors", "nopelicans": "pelicans"}
    for k, v in stats_dict.items():
        stat_clean = re.sub(r'[^a-zA-Z]', '', k).lower()
        if odds_clean in stat_clean or stat_clean in odds_clean: return v
        for ok, ov in overrides.items():
            if ok in odds_clean and ov in stat_clean: return v
    return None

def run_nba_analytics():
    global izvestaj, global_tiket
    live_data = get_live_standings_cbs()
    team_stats = get_nba_stats()
    
    if live_data: izvestaj += "📡 LIVE DATA: CBS Sports (Scraper) ✅\n\n"
    else: izvestaj += "📡 LIVE DATA: Backup Mode (Stats Only) ⚠️\n\n"

    if not ODDS_API_KEY: 
        izvestaj += "❌ NEMA API KLJUČA!\n"
        return
        
    try:
        url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,spreads,totals&oddsFormat=decimal"
        response = requests.get(url).json()
        
        if isinstance(response, dict) and 'message' in response:
            izvestaj += f"⚠️ API GREŠKA: {response['message']}\n"
            return
        
        top_picks = []
        for mec in response:
            if not is_match_today(mec['commence_time']): continue 
            home, away = mec['home_team'], mec['away_team']
            h_stats = match_team_stats(home, team_stats)
            a_stats = match_team_stats(away, team_stats)
            
            if h_stats and a_stats:
                proj_home = (h_stats['OFF'] + a_stats['DEF']) / 2 + 3.0
                proj_away = (a_stats['OFF'] + h_stats['DEF']) / 2 - 3.0
                handicap_proj = proj_home - proj_away
                total_proj = proj_home + proj_away

                for book in mec['bookmakers']:
                    if book['key'] in ['pinnacle', 'bet365', 'unibet']:
                        spread_h, spread_a, total, h_win, a_win = None, None, 0, 0, 0
                        
                        for m in book['markets']:
                            if m['key'] == 'spreads':
                                for o in m['outcomes']:
                                    if o['name'] == home: spread_h = o['point']
                                    if o['name'] == away: spread_a = o['point']
                            if m['key'] == 'totals': total = m['outcomes'][0]['point']
                            if m['key'] == 'h2h':
                                for o in m['outcomes']:
                                    if o['name'] == home: h_win = o['price']
                                    if o['name'] == away: a_win = o['price']
                        
                        if spread_h is None: continue

                        # 1x2
                        winner_pick = None
                        if handicap_proj > 8.0 and h_win > 1.35: winner_pick = (home, h_win)
                        elif handicap_proj < -8.0 and a_win > 1.35: winner_pick = (away, a_win)
                        
                        if winner_pick:
                            team_name = clean_team_name(winner_pick[0])
                            global_tiket.append(f"{team_name} POBEDA|{winner_pick[1]}")
                            top_picks.append({
                                'mec': f"{clean_team_name(home)} vs {clean_team_name(away)}",
                                'tip': f"POBEDA {team_name} (1x2)",
                                'bar': "🟩🟩🟩🟩⬜", 'ulog': "💎💎", 'conf': 8.0
                            })

                        # Hendikep
                        spread_diff = abs(handicap_proj - (-spread_h))
                        tip_team = home if (handicap_proj - (-spread_h)) > 0 else away
                        final_line = spread_h if tip_team == home else spread_a
                        znak = f"{final_line:+}"
                        
                        warning_msg = ""
                        if live_data:
                            t_clean = clean_team_name(tip_team).lower()
                            overrides = {"76ers": "sixers", "cavaliers": "cavs", "trail blazers": "blazers"}
                            if t_clean in overrides: t_clean = overrides[t_clean]
                            
                            form_key = None
                            for k in live_data.keys():
                                if t_clean in k or k in t_clean: form_key = k; break
                            
                            if form_key:
                                form = live_data[form_key]
                                if not form['is_winning'] and form['streak'] >= 3:
                                    spread_diff -= 5.0
                                    warning_msg = "(⚠️ L" + str(form['streak']) + ")"

                        if spread_diff > 4.0:
                            bar = get_confidence_bar(spread_diff)
                            ulog = get_stake_diamonds(spread_diff)
                            if spread_diff > 7.0: global_tiket.append(f"{clean_team_name(tip_team)} {znak}|1.90")
                            top_picks.append({
                                'mec': f"{clean_team_name(home)} vs {clean_team_name(away)}", 
                                'tip': f"HENDIKEP {clean_team_name(tip_team)} ({znak}) {warning_msg}", 
                                'bar': bar, 'ulog': ulog, 'conf': spread_diff
                            })
                        
                        # Total
                        total_diff = abs(total_proj - total)
                        if total_diff > 5.0:
                            smer = "VIŠE (Over)" if total_proj > total else "MANJE (Under)"
                            prop_suggestion = ""
                            if smer == "VIŠE (Over)":
                                h_clean = clean_team_name(home).lower()
                                star = None
                                for k, v in STAR_PLAYERS.items():
                                    if k in h_clean or h_clean in k: star = v; break
                                if star: prop_suggestion = f"\n   🔥 *BONUS:* Igraj {star} - VIŠE poena!"

                            top_picks.append({
                                'mec': f"{clean_team_name(home)} vs {clean_team_name(away)}", 
                                'tip': f"MEČ UKUPNO {smer} {total}{prop_suggestion}", 
                                'bar': get_confidence_bar(total_diff), 'ulog': get_stake_diamonds(total_diff), 'conf': total_diff
                            })
                            if total_diff > 8.0: global_tiket.append(f"{clean_team_name(home)} MEČ {smer} {total}|1.90")
                        break
        
        top_picks = sorted(top_picks, key=lambda x: x['conf'], reverse=True)[:4]
        if top_picks:
            izvestaj += "\n🏀 *NBA TIP DANA & IGRAČI:*\n"
            for p in top_picks:
                izvestaj += f"👉 *{p['mec']}*\n   🛡️ Igraj: *{p['tip']}*\n   🔋 Sigurnost: {p['bar']}\n   💵 Ulog: {p['ulog']}\n\n"
    except Exception as e: izvestaj += f"Greška NBA: {e}"

def run_nhl_analytics():
    global izvestaj, global_tiket
    if not ODDS_API_KEY: return
    try:
        url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals&oddsFormat=decimal"
        response = requests.get(url).json()
        
        if isinstance(response, dict) and 'message' in response: return

        nhl_picks = []
        for mec in response:
            if not is_match_today(mec['commence_time']): continue
            for book in mec['bookmakers']:
                if book['key'] in ['pinnacle', 'bet365']:
                    for m in book['markets']:
                        if m['key'] == 'totals':
                            over_p = 0
                            point = m['outcomes'][0]['point']
                            for o in m['outcomes']:
                                if o['name'] == 'Over': over_p = o['price']
                            if over_p < 1.90: 
                                pick = f"VIŠE od {point}"
                                nhl_picks.append({'mec': f"{clean_team_name(mec['home_team'])} vs {clean_team_name(mec['away_team'])}", 'tip': pick, 'kvota': over_p, 'conf': 2.0/over_p})
                                if over_p < 1.75: global_tiket.append(f"NHL: {clean_team_name(mec['home_team'])} {pick}|{over_p}")
                    break
        nhl_picks = sorted(nhl_picks, key=lambda x: x['conf'], reverse=True)[:3]
        if nhl_picks:
            izvestaj += "🏒 *NHL HOKEJ:*\n"
            for p in nhl_picks: 
                izvestaj += f"👉 *{p['mec']}*\n   ❄️ Tip: *{p['tip']}* (Kvota: {p['kvota']})\n"
            izvestaj += "\n"
    except: pass

def run_football_module():
    global izvestaj, global_tiket
    if not ODDS_API_KEY: return
    leagues = ['soccer_epl', 'soccer_germany_bundesliga', 'soccer_spain_la_liga', 'soccer_italy_serie_a', 'soccer_france_ligue_one']
    picks_str = ""
    for league in leagues:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
            response = requests.get(url).json()
            
            if isinstance(response, dict) and 'message' in response: continue

            for mec in response:
                if not is_match_today(mec['commence_time']): continue
                home, away = mec['home_team'], mec['away_team']
                for book in mec['bookmakers']:
                    if book['key'] in ['pinnacle', 'bet365', 'unibet']:
                        home_win = 0
                        for m in book['markets']:
                            if m['key'] == 'h2h':
                                for o in m['outcomes']:
                                    if o['name'] == home: home_win = o['price']
                        if 1.20 < home_win < 1.70:
                            picks_str += f"⚽ *{home}* vs {away}\n   🎯 Tip: *POBEDA DOMAĆINA (1)*\n   💰 Kvota: {home_win}\n\n"
                            global_tiket.append(f"{home} POBEDA|{home_win}")
                        break
        except: continue
    if picks_str: izvestaj += "🌍 *FUDBAL ZICERI:*\n" + picks_str

def generisi_tiket_dana():
    global izvestaj, global_tiket
    if len(global_tiket) >= 2:
        top_tiket = global_tiket[:5] 
        ukupna_kvota = 1.0
        izvestaj += "-----------------------------------\n"
        izvestaj += "🎫 *KAI VIP TIKET DANA (All-In-One)*\n"
        for stavka in top_tiket:
            delovi = stavka.split('|')
            opis = delovi[0]
            kvota = float(delovi[1])
            ukupna_kvota *= kvota
            izvestaj += f"✅ {opis} ({kvota})\n"
        izvestaj += f"\n🚀 *UKUPNA KVOTA: {ukupna_kvota:.2f}*\n"
    else: izvestaj += "\nℹ️ Nema dovoljno parova za tiket."

if __name__ == "__main__":
    try: run_nba_analytics()
    except: pass
    try: run_nhl_analytics()
    except: pass
    try: run_football_module()
    except: pass
    try: generisi_tiket_dana()
    except: pass
    posalji_telegram(izvestaj)
    print("✅ GOTOVO!")
