"""
chart.py — Vedic chart computation using Swiss Ephemeris
pip install pyswisseph
"""
import swisseph as swe
from datetime import datetime

swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa (standard for Vedic)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
              "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
              "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
              "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
              "Uttara Bhadrapada", "Revati"]

PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,  # Ketu = Rahu + 180
}

# Vimshottari dasha: nakshatra lord sequence and years
DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
               "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}


def _sidereal_lon(jd, planet_id):
    lon = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)[0][0]
    return lon % 360


def _sign_of(lon):
    return SIGNS[int(lon // 30)]


def _nakshatra_of(lon):
    idx = int(lon // (360 / 27))
    pada = int((lon % (360 / 27)) // (360 / 108)) + 1
    return NAKSHATRAS[idx], pada, idx


def compute_chart(dob: str, tob: str, lat: float, lon: float, tz_offset: float):
    """
    dob: 'YYYY-MM-DD', tob: 'HH:MM' (local time)
    lat/lon: birthplace coordinates
    tz_offset: e.g. 5.5 for IST
    """
    dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    ut_hour = dt.hour + dt.minute / 60 - tz_offset
    jd = swe.julday(dt.year, dt.month, dt.day, ut_hour)

    # Ascendant (Lagna) — whole sign houses
    ayanamsa = swe.get_ayanamsa_ut(jd)
    cusps, ascmc = swe.houses(jd, lat, lon, b"W")
    asc_lon = (ascmc[0] - ayanamsa) % 360
    asc_sign_idx = int(asc_lon // 30)

    chart = {
        "ascendant": {
            "longitude": round(asc_lon, 2),
            "sign": SIGNS[asc_sign_idx],
        },
        "planets": {},
    }

    moon_lon = None
    for name, pid in PLANETS.items():
        plon = _sidereal_lon(jd, pid)
        if name == "Moon":
            moon_lon = plon
        _add_planet(chart, name, plon, asc_sign_idx)

    # Ketu = opposite Rahu
    ketu_lon = (chart["planets"]["Rahu"]["longitude"] + 180) % 360
    _add_planet(chart, "Ketu", ketu_lon, asc_sign_idx)

    # Moon sign (Rashi) + current Mahadasha
    chart["moon_sign"] = _sign_of(moon_lon)
    chart["mahadasha"] = _vimshottari(moon_lon, dt)

    return chart


def _add_planet(chart, name, plon, asc_sign_idx):
    sign_idx = int(plon // 30)
    house = (sign_idx - asc_sign_idx) % 12 + 1  # whole-sign house
    nak, pada, _ = _nakshatra_of(plon)
    chart["planets"][name] = {
        "longitude": round(plon, 2),
        "sign": SIGNS[sign_idx],
        "house": house,
        "nakshatra": nak,
        "pada": pada,
    }


def _vimshottari(moon_lon, birth_dt):
    """Return dasha sequence with start years from birth."""
    nak_span = 360 / 27
    nak_idx = int(moon_lon // nak_span)
    lord_idx = nak_idx % 9
    start_lord = DASHA_LORDS[lord_idx]

    # fraction of nakshatra already traversed = fraction of dasha elapsed
    traversed = (moon_lon % nak_span) / nak_span
    balance_years = DASHA_YEARS[start_lord] * (1 - traversed)

    sequence = []
    year_cursor = birth_dt.year + birth_dt.timetuple().tm_yday / 365.25
    # first (partial) dasha
    sequence.append({"lord": start_lord,
                     "start": round(year_cursor, 1),
                     "end": round(year_cursor + balance_years, 1)})
    year_cursor += balance_years
    # subsequent dashas
    for i in range(1, 9):
        lord = DASHA_LORDS[(lord_idx + i) % 9]
        yrs = DASHA_YEARS[lord]
        sequence.append({"lord": lord,
                         "start": round(year_cursor, 1),
                         "end": round(year_cursor + yrs, 1)})
        year_cursor += yrs

    # mark current
    now = datetime.now().year + datetime.now().timetuple().tm_yday / 365.25
    for d in sequence:
        d["current"] = d["start"] <= now < d["end"]
    return sequence


if __name__ == "__main__":
    import json
    # Example: 15 Aug 1995, 10:30 AM, Gurgaon (28.46 N, 77.03 E), IST
    chart = compute_chart("1995-08-15", "10:30", 28.46, 77.03, 5.5)
    print(json.dumps(chart, indent=2))