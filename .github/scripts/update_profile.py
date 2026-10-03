#!/usr/bin/env python3
"""
Dynamic Telemetry & 3D Contribution City Generator
Updates SVG assets with live GitHub data and native SMIL animations for Madhu-0205.
"""

import urllib.request
import re
import datetime
import os
import sys

USERNAME = "Madhu-0205"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def fetch_contributions():
    url = f"https://github.com/users/{USERNAME}/contributions"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return None

    # Parse days and counts
    td_matches = re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"[^>]*>', html)
    date_count_pattern = re.findall(r'(\d+|No)\s+contributions?\s+on\s+([A-Za-z]+ \d{1,2}, \d{4})', html)
    
    counts_by_date = {}
    for c_str, d_str in date_count_pattern:
        cnt = 0 if c_str == 'No' else int(c_str)
        try:
            dt = datetime.datetime.strptime(d_str, '%B %d, %Y').strftime('%Y-%m-%d')
            counts_by_date[dt] = cnt
        except Exception:
            pass

    days_data = []
    for m in td_matches:
        date_str, level_str = m[0], int(m[1])
        cnt = counts_by_date.get(date_str)
        if cnt is None:
            if level_str == 1: cnt = 2
            elif level_str == 2: cnt = 5
            elif level_str == 3: cnt = 10
            elif level_str == 4: cnt = 20
            else: cnt = 0
        days_data.append({'date': date_str, 'level': level_str, 'count': cnt})

    return days_data

def generate_3d_city(days_data):
    if not days_data:
        return
    
    total_contribs = sum(d['count'] for d in days_data)
    grid = {}
    current_week = 0
    for i, d in enumerate(days_data):
        dt = datetime.datetime.strptime(d['date'], '%Y-%m-%d')
        dow = (dt.weekday() + 1) % 7 # 0 = Sun
        if dow == 0 and i > 0:
            current_week += 1
        grid[(current_week, dow)] = d

    total_weeks = current_week + 1
    svg_w = 1000
    svg_h = 440

    ox = 210
    oy = 150
    wx, wy = 13.0, 6.2
    dx, dy = -15.0, 7.5

    xs, ys = [], []
    for w in range(total_weeks):
        for d in range(7):
            bx = ox + w*wx + d*dx
            by = oy + w*wy + d*dy
            xs.append(bx)
            ys.append(by)

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    shift_x = (svg_w - (max_x - min_x)) / 2 - min_x
    shift_y = 230 - ((max_y + min_y) / 2)

    ox += shift_x
    oy += shift_y

    def get_colors(count, level):
        if count == 0:
            return {
                'top': '#0B1628', 'left': '#07101E', 'right': '#050B15',
                'stroke': 'rgba(56, 189, 248, 0.12)', 'glow': False
            }
        elif count < 4:
            return {
                'top': '#0284C7', 'left': '#0369A1', 'right': '#075985',
                'stroke': 'rgba(56, 189, 248, 0.4)', 'glow': False
            }
        elif count < 9:
            return {
                'top': '#0EA5E9', 'left': '#0284C7', 'right': '#0369A1',
                'stroke': 'rgba(56, 189, 248, 0.6)', 'glow': True
            }
        elif count < 16:
            return {
                'top': '#38BDF8', 'left': '#0284C7', 'right': '#4338CA',
                'stroke': '#7DD3FC', 'glow': True
            }
        else:
            return {
                'top': '#7DD3FC', 'left': '#38BDF8', 'right': '#6366F1',
                'stroke': '#BAE6FD', 'glow': True
            }

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}" fill="none">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050A14"/>
      <stop offset="50%" stop-color="#07111F"/>
      <stop offset="100%" stop-color="#0B162C"/>
    </linearGradient>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(56, 189, 248, 0.03)" stroke-width="1"/>
    </pattern>
    <filter id="cityGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <radialGradient id="platformGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.14"/>
      <stop offset="70%" stop-color="#6366F1" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#050A14" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0"/>
      <stop offset="50%" stop-color="#38BDF8" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="cityScanBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0"/>
      <stop offset="50%" stop-color="#38BDF8" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .mono {{ font-family: 'JetBrains Mono', 'SF Mono', Consolas, monospace; }}
    .sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif; }}
  </style>

  <!-- Canvas Background -->
  <rect width="{svg_w}" height="{svg_h}" rx="14" fill="url(#bgGrad)"/>
  <rect width="{svg_w}" height="{svg_h}" rx="14" fill="url(#grid)"/>
  <rect width="{svg_w}" height="{svg_h}" rx="14" stroke="#38BDF8" stroke-width="1" fill="none">
    <animate attributeName="stroke-opacity" values="0.15;0.35;0.15" dur="6s" repeatCount="indefinite"/>
  </rect>

  <!-- Breathing Platform Radial Light -->
  <ellipse cx="500" cy="275" rx="360" ry="110" fill="url(#platformGlow)">
    <animate attributeName="rx" values="340;380;340" dur="6s" repeatCount="indefinite"/>
    <animate attributeName="ry" values="100;120;100" dur="6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.75;1;0.75" dur="6s" repeatCount="indefinite"/>
  </ellipse>

  <!-- Section Header -->
  <g>
    <text x="24" y="28" class="mono" font-size="10.5" font-weight="600" fill="#38BDF8" letter-spacing="1.5">// ISOMETRIC TELEMETRY MAPPING • {total_contribs} CONTRIBUTIONS</text>
    <text x="24" y="50" class="sans" font-size="19" font-weight="800" fill="#F8FAFC" letter-spacing="0.5">3D CONTRIBUTION CITY</text>
    <path d="M 24 58 L 248 58" stroke="#38BDF8" stroke-width="2" stroke-linecap="round"/>
    <path d="M 256 58 L 976 58" stroke="rgba(56, 189, 248, 0.15)" stroke-width="1" stroke-dasharray="3 3">
      <animate attributeName="stroke-dashoffset" from="0" to="24" dur="4s" repeatCount="indefinite"/>
    </path>
    <line x1="256" y1="58" x2="390" y2="58" stroke="url(#beamGrad)" stroke-width="2">
      <animate attributeName="x1" values="256;840;256" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="390;972;390" dur="8s" repeatCount="indefinite"/>
    </line>
  </g>

  <!-- Top Right Badges -->
  <g transform="translate(680, 24)">
    <rect x="0" y="0" width="180" height="22" rx="4" fill="rgba(56, 189, 248, 0.08)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="0.8"/>
    <circle cx="12" cy="11" r="3" fill="#38BDF8">
      <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="22" y="15" class="mono" font-size="9" font-weight="700" fill="#38BDF8">REAL-TIME TOPOLOGY</text>

    <rect x="190" y="0" width="105" height="22" rx="4" fill="rgba(99, 102, 241, 0.12)" stroke="rgba(99, 102, 241, 0.3)" stroke-width="0.8"/>
    <text x="242" y="15" class="mono" font-size="9" font-weight="700" fill="#A78BFA" text-anchor="middle">{total_weeks} WEEKS</text>
  </g>
''')

    rw = 6.0
    rh = 3.0
    items = []
    for w in range(total_weeks):
        for d in range(7):
            data = grid.get((w, d), {'count': 0, 'level': 0, 'date': ''})
            cnt = data['count']
            lvl = data['level']
            if cnt == 0:
                h = 3.5
            elif cnt < 4:
                h = 10.0 + cnt * 2.0
            elif cnt < 9:
                h = 18.0 + (cnt - 3) * 3.0
            elif cnt < 16:
                h = 34.0 + (cnt - 8) * 2.5
            else:
                h = 52.0 + min(20.0, (cnt - 15) * 1.5)
            
            bx = ox + w*wx + d*dx
            by = oy + w*wy + d*dy
            items.append({
                'w': w, 'd': d, 'bx': bx, 'by': by,
                'h': h, 'count': cnt, 'level': lvl, 'date': data.get('date', '')
            })

    items.sort(key=lambda item: item['by'])

    # Traveling soft scan radar band across city skyline
    svg_parts.append(f'''  <!-- Traveling Skyline Scan Line -->
  <rect x="40" y="60" width="100" height="320" fill="url(#cityScanBeam)" opacity="0.5">
    <animate attributeName="x" values="40;860;40" dur="11s" repeatCount="indefinite"/>
  </rect>

  <!-- Floating Telemetry Particles -->
  <circle cx="260" cy="180" r="2" fill="#38BDF8">
    <animate attributeName="cx" values="260;640;260" dur="14s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="180;320;180" dur="14s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.2;0.85;0.2" dur="3s" repeatCount="indefinite"/>
  </circle>
  <circle cx="680" cy="200" r="2" fill="#818CF8">
    <animate attributeName="cx" values="680;320;680" dur="16s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="200;330;200" dur="16s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.2;0.75;0.2" dur="4s" repeatCount="indefinite"/>
  </circle>
''')

    svg_parts.append('  <!-- 3D Isometric Buildings with Staggered Build & Pulsing Beacons -->\n  <g id="isometric-blocks">\n')

    for item in items:
        bx, by, h = item['bx'], item['by'], item['h']
        cnt, lvl, date, w = item['count'], item['level'], item['date'], item['w']
        colors = get_colors(cnt, lvl)

        top_v = f"{bx:.1f},{by - h - rh:.1f}"
        right_v = f"{bx + rw:.1f},{by - h:.1f}"
        bottom_v = f"{bx:.1f},{by - h + rh:.1f}"
        left_v = f"{bx - rw:.1f},{by - h:.1f}"

        left_face = f"M {bx - rw:.1f} {by - h:.1f} L {bx:.1f} {by - h + rh:.1f} L {bx:.1f} {by + rh:.1f} L {bx - rw:.1f} {by:.1f} Z"
        right_face = f"M {bx:.1f} {by - h + rh:.1f} L {bx + rw:.1f} {by - h:.1f} L {bx + rw:.1f} {by:.1f} L {bx:.1f} {by + rh:.1f} Z"
        top_face = f"M {top_v} L {right_v} L {bottom_v} L {left_v} Z"

        title_el = f"<title>{date}: {cnt} contributions</title>" if date else ""
        glow_attr = ' filter="url(#cityGlow)"' if colors['glow'] and cnt >= 15 else ''
        
        # Staggered build appearance on initial load based on week index
        anim_delay = f"{0.015 * w:.3f}s"

        # Beacon for high activity towers
        beacon = ""
        if cnt >= 10:
            beacon_dur = f"{1.8 + (w % 4) * 0.4:.1f}s"
            beacon = f'''
      <circle cx="{bx:.1f}" cy="{by - h - rh:.1f}" r="1.8" fill="#BAE6FD">
        <animate attributeName="opacity" values="0.3;1;0.3" dur="{beacon_dur}" repeatCount="indefinite"/>
      </circle>'''

        # Pulse for active roof faces
        top_anim = ""
        if cnt >= 4:
            top_dur = f"{2.2 + (w % 5) * 0.4:.1f}s"
            top_anim = f'''
        <animate attributeName="fill-opacity" values="0.75;1;0.75" dur="{top_dur}" repeatCount="indefinite"/>'''

        svg_parts.append(f'''    <g{glow_attr} opacity="0">
      <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{anim_delay}" fill="freeze"/>
      {title_el}
      <path d="{left_face}" fill="{colors['left']}" stroke="{colors['stroke']}" stroke-width="0.3"/>
      <path d="{right_face}" fill="{colors['right']}" stroke="{colors['stroke']}" stroke-width="0.3"/>
      <path d="{top_face}" fill="{colors['top']}" stroke="{colors['stroke']}" stroke-width="0.4">{top_anim}
      </path>{beacon}
    </g>''')

    svg_parts.append('  </g>\n')

    svg_parts.append(f'''
  <!-- Footer Telemetry & Legend -->
  <g transform="translate(24, {svg_h - 38})">
    <text x="0" y="16" class="mono" font-size="9" fill="#64748B">CONTRIBUTION DENSITY:</text>
    <rect x="155" y="6" width="12" height="12" rx="2" fill="#0B1628" stroke="rgba(56, 189, 248, 0.2)" stroke-width="0.8"/>
    <text x="173" y="16" class="mono" font-size="8.5" fill="#94A3B8">0</text>

    <rect x="200" y="6" width="12" height="12" rx="2" fill="#0284C7" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
    <text x="218" y="16" class="mono" font-size="8.5" fill="#94A3B8">1-3</text>

    <rect x="255" y="6" width="12" height="12" rx="2" fill="#0EA5E9" stroke="rgba(56, 189, 248, 0.6)" stroke-width="0.8"/>
    <text x="273" y="16" class="mono" font-size="8.5" fill="#94A3B8">4-8</text>

    <rect x="310" y="6" width="12" height="12" rx="2" fill="#38BDF8" stroke="#7DD3FC" stroke-width="0.8"/>
    <text x="328" y="16" class="mono" font-size="8.5" fill="#94A3B8">9-15</text>

    <rect x="370" y="6" width="12" height="12" rx="2" fill="#7DD3FC" stroke="#BAE6FD" stroke-width="0.8"/>
    <text x="388" y="16" class="mono" font-size="8.5" fill="#94A3B8">16+</text>

    <text x="952" y="16" class="mono" font-size="9" fill="#38BDF8" text-anchor="end" font-weight="600">ISOMETRIC SKYLINE GENERATED FROM AUTHENTIC GITHUB REPOSITORY EVENTS</text>
  </g>
</svg>
''')

    city_path = os.path.join(ASSETS_DIR, "contribution-city.svg")
    with open(city_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"Updated {city_path}")

def generate_activity_matrix(days_data):
    if not days_data:
        return

    total_contribs = sum(d['count'] for d in days_data)
    grid = {}
    current_week = 0
    for i, d in enumerate(days_data):
        dt = datetime.datetime.strptime(d['date'], '%Y-%m-%d')
        dow = (dt.weekday() + 1) % 7 # 0 = Sun
        if dow == 0 and i > 0:
            current_week += 1
        grid[(current_week, dow)] = d

    total_weeks = current_week + 1
    svg_w = 1000
    svg_h = 215

    def get_cell_color(count):
        if count == 0:
            return '#0B1728', 'rgba(56, 189, 248, 0.12)', 0.8
        elif count < 4:
            return '#075985', 'rgba(56, 189, 248, 0.4)', 1.0
        elif count < 9:
            return '#0284C7', 'rgba(56, 189, 248, 0.5)', 1.0
        elif count < 16:
            return '#38BDF8', 'rgba(56, 189, 248, 0.6)', 1.0
        else:
            return '#7DD3FC', 'rgba(56, 189, 248, 0.8)', 1.0

    # Build month header labels
    month_labels = []
    prev_month = ""
    for w in range(total_weeks):
        d0 = grid.get((w, 0))
        if d0:
            dt = datetime.datetime.strptime(d0['date'], '%Y-%m-%d')
            m_str = dt.strftime('%b')
            if m_str != prev_month:
                month_labels.append((56 + w * 17, m_str))
                prev_month = m_str

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}" fill="none">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050A14"/>
      <stop offset="50%" stop-color="#07111F"/>
      <stop offset="100%" stop-color="#0B162C"/>
    </linearGradient>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(56, 189, 248, 0.035)" stroke-width="1"/>
    </pattern>
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0"/>
      <stop offset="50%" stop-color="#38BDF8" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="matrixScan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0"/>
      <stop offset="50%" stop-color="#38BDF8" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .mono {{ font-family: 'JetBrains Mono', 'SF Mono', Consolas, monospace; }}
    .sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif; }}
  </style>

  <rect width="{svg_w}" height="{svg_h}" rx="14" fill="url(#bgGrad)"/>
  <rect width="{svg_w}" height="{svg_h}" rx="14" fill="url(#grid)"/>
  <rect width="{svg_w}" height="{svg_h}" rx="14" stroke="#38BDF8" stroke-width="1" fill="none">
    <animate attributeName="stroke-opacity" values="0.15;0.35;0.15" dur="6s" repeatCount="indefinite"/>
  </rect>

  <!-- Header -->
  <g>
    <text x="24" y="26" class="mono" font-size="10" font-weight="600" fill="#38BDF8" letter-spacing="1.5">// {total_contribs} CONTRIBUTIONS IN 2025–2026 • {total_weeks} WEEKS</text>
    <text x="24" y="46" class="sans" font-size="17" font-weight="800" fill="#F8FAFC" letter-spacing="0.5">CONTRIBUTION ACTIVITY</text>
    <path d="M 24 53 L 230 53" stroke="#38BDF8" stroke-width="2" stroke-linecap="round"/>
    <path d="M 238 53 L 976 53" stroke="rgba(56, 189, 248, 0.15)" stroke-width="1" stroke-dasharray="3 3">
      <animate attributeName="stroke-dashoffset" from="0" to="24" dur="4s" repeatCount="indefinite"/>
    </path>
    <line x1="238" y1="53" x2="370" y2="53" stroke="url(#beamGrad)" stroke-width="2">
      <animate attributeName="x1" values="238;840;238" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="370;972;370" dur="8s" repeatCount="indefinite"/>
    </line>
  </g>

  <!-- Days of week labels -->
  <text x="24" y="78" class="mono" font-size="8.5" fill="#64748B">Sun</text>
  <text x="24" y="112" class="mono" font-size="8.5" fill="#94A3B8">Wed</text>
  <text x="24" y="163" class="mono" font-size="8.5" fill="#64748B">Sat</text>

  <!-- Month labels -->
''')

    for mx, mstr in month_labels:
        svg_parts.append(f'  <text x="{mx}" y="56" class="mono" font-size="9" fill="#94A3B8">{mstr}</text>')

    # Horizontal Radar Scanning Line across matrix
    svg_parts.append(f'''
  <!-- Matrix Scanning Beam -->
  <rect x="56" y="64" width="60" height="120" fill="url(#matrixScan)" opacity="0.45">
    <animate attributeName="x" values="56;920;56" dur="10s" repeatCount="indefinite"/>
  </rect>
''')

    # Grid Cells Grouped by Week with Staggered Fade-in
    svg_parts.append('  <!-- 53-Week Grid Matrix with Column Reveal -->\n  <g id="matrix-cells">\n')

    for w in range(total_weeks):
        col_x = 56 + w * 17
        col_delay = f"{0.015 * w:.3f}s"
        svg_parts.append(f'    <g opacity="0">\n      <animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{col_delay}" fill="freeze"/>')
        for d in range(7):
            cell_y = 66 + d * 17
            data = grid.get((w, d), {'count': 0, 'level': 0, 'date': ''})
            cnt = data['count']
            date = data['date']
            fill_c, stroke_c, sw = get_cell_color(cnt)
            title = f"<title>{date}: {cnt} contributions</title>" if date else ""

            pulse_anim = ""
            if cnt > 0:
                pulse_dur = f"{2.0 + (w % 4)*0.4:.1f}s"
                pulse_anim = f'<animate attributeName="stroke-opacity" values="0.4;1;0.4" dur="{pulse_dur}" repeatCount="indefinite"/>'

            svg_parts.append(f'      <rect x="{col_x}" y="{cell_y}" width="13" height="13" rx="2.5" fill="{fill_c}" stroke="{stroke_c}" stroke-width="{sw}">{title}{pulse_anim}</rect>')
        svg_parts.append('    </g>')

    svg_parts.append('  </g>\n')

    # Footer legend
    svg_parts.append(f'''
  <!-- Matrix Footer Legend -->
  <g transform="translate(24, {svg_h - 22})">
    <text x="0" y="10" class="mono" font-size="8.5" fill="#64748B">LESS</text>
    <rect x="35" y="1" width="10" height="10" rx="2" fill="#0B1728" stroke="rgba(56, 189, 248, 0.12)" stroke-width="0.8"/>
    <rect x="50" y="1" width="10" height="10" rx="2" fill="#075985" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1"/>
    <rect x="65" y="1" width="10" height="10" rx="2" fill="#0284C7" stroke="rgba(56, 189, 248, 0.5)" stroke-width="1"/>
    <rect x="80" y="1" width="10" height="10" rx="2" fill="#38BDF8" stroke="rgba(56, 189, 248, 0.6)" stroke-width="1"/>
    <rect x="95" y="1" width="10" height="10" rx="2" fill="#7DD3FC" stroke="rgba(56, 189, 248, 0.8)" stroke-width="1"/>
    <text x="112" y="10" class="mono" font-size="8.5" fill="#64748B">MORE</text>
    <text x="952" y="10" class="mono" font-size="8.5" fill="#38BDF8" text-anchor="end">// 53-WEEK ROLLING CADENCE SYNCHRONIZED WITH GITHUB TELEMETRY</text>
  </g>
</svg>
''')

    matrix_path = os.path.join(ASSETS_DIR, "contribution-activity.svg")
    with open(matrix_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"Updated {matrix_path}")

def main():
    print(f"Executing telemetry update for {USERNAME}...")
    days_data = fetch_contributions()
    if days_data:
        generate_3d_city(days_data)
        generate_activity_matrix(days_data)
        print("Telemetry update complete.")
    else:
        print("Failed to fetch contributions.")

if __name__ == "__main__":
    main()
