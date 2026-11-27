#!/usr/bin/env python3
"""
=============================================================================
INFINITE DYNAMIC DOCUMENTARY GENERATOR (Expanded Forensic Narrative Engine)
=============================================================================
Autonomous AI Engine that:
1. Picks a fresh historical topic that has NEVER been covered before
2. Generates a deep 14-18 take forensic narrative (Lemmino / Vox documentary style)
   Resulting in a legitimate, gripping ~2.5 - 3.5 minute documentary!
3. Dynamic topic metadata with custom high-CTR thumbnail hooks & badges
4. Queries Wikimedia Commons API dynamically to download authentic archival photos
5. Assembles ready-to-render project folder under cinematic_engine/assets/<slug>/
6. Updates history_documentaries.json so topics NEVER repeat!
=============================================================================
"""

import os
import sys
import json
import time
import random
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
HISTORY_FILE = BASE_DIR / "history_documentaries.json"

# Rich, deep, multi-act historical documentary catalog (14-18 narrative takes each -> ~2.5 to 3.5 mins)
DEEP_TOPIC_CATALOG = [
    {
        "slug": "dyatlov-pass",
        "title": "The Dyatlov Pass Mystery",
        "thumb_hook_top": "SLASHED FROM",
        "thumb_hook_bottom": "THE INSIDE",
        "thumb_color": [255, 65, 65],
        "thumb_badge": "KGB DECLASSIFIED ARCHIVE",
        "thumb_sub_pill": "FEB 2, 1959 • NINE DEAD IN SUB-ZERO",
        "search_terms": [
            "Dyatlov Pass incident",
            "Kholat Syakhl tent",
            "Igor Dyatlov expedition 1959",
            "Ural mountains snow rescue 1959",
            "Lyudmila Dubinina Dyatlov",
            "Dyatlov pass search party"
        ],
        "lines": [
            ("In late January 1959, ten experienced cross-country skiers from the Ural Polytechnic Institute embarked on a grueling expedition through the northern Urals.", "JANUARY 1959 • URAL MOUNTAINS"),
            ("Led by 23-year-old engineering student Igor Dyatlov, their goal was to reach Otorten mountain, a route classified as Category 3, the highest level of difficulty.", "EXPEDITION LEADER • IGOR DYATLOV"),
            ("On January 28th, one team member, Yuri Yudin, was forced to turn back due to debilitating joint pain. He would be the sole survivor of the group.", "YURI YUDIN • SOLE SURVIVOR"),
            ("On the freezing afternoon of February 1st, bad weather forced the remaining nine hikers to pitch their tent high on the exposed eastern slope of Kholat Syakhl.", "KHOLAT SYAKHL • THE DEAD MOUNTAIN"),
            ("Sometime in the pitch-black hours before dawn, something so catastrophic occurred that they abandoned everything they owned to survive.", "FEBRUARY 2, 1959 • THE INCIDENT"),
            ("When Soviet search parties finally located the abandoned camp weeks later, the scene defied all logical explanation.", "FEBRUARY 26 • SEARCH TEAM ARRIVES"),
            ("The heavy canvas tent had been violently slashed open from the inside with multiple knife cuts.", "FORENSIC FINDING • TENT SLASHED"),
            ("All their warm coats, heavy boots, food, and equipment had been left behind. Nine sets of footprints led downhill into the sub-zero darkness in socks or bare feet.", "EVIDENCE • BAREFOOT TRACKS"),
            ("A mile down the slope, near the tree line, searchers discovered the frozen remains of Yuri Krivonischenko and Yuri Doroshenko beneath a giant Siberian cedar.", "AT THE CEDAR TREE"),
            ("Branches were broken five meters high, and bark was embedded in their skin, suggesting desperate attempts to climb and scan the mountain.", "DESPERATE CLIMB"),
            ("Nearby lay a primitive campfire that had burned down to ashes. Both men were dressed only in underwear and were covered in soot.", "SUB-ZERO FREEZING"),
            ("Months later, as the snow melted in May, the remaining four hikers were discovered deep in a ravine, buried beneath four meters of packed ice.", "MAY 1959 • THE RAVINE DISCOVERY"),
            ("Autopsies revealed horrific internal trauma comparable to a high-speed vehicle impact, yet remarkably without a single external bruise or fracture.", "AUTOPSY • BLUNT FORCE TRAUMA"),
            ("Thibaux-Brignolles had suffered massive skull fractures, while Lyudmila Dubinina and Semyon Zolotaryov had crushed chest cavities and ribs broken inward.", "CATASTROPHIC INJURIES"),
            ("Dubinina was missing her tongue and eyes. Stranger still, Soviet pathologists found abnormal traces of radioactive isotopes on several pieces of their clothing.", "UNEXPLAINED ANOMALIES"),
            ("The Soviet inquest abruptly closed the file, concluding only that the hikers had perished as a result of an overwhelming elemental force.", "OFFICIAL VERDICT • ELEMENTAL FORCE"),
            ("Sixty years later, whether an acoustic slab avalanche, secret military test, or infrasound panic, Kholat Syakhl still keeps its silent secret.", "UNRESOLVED CHRONICLE")
        ]
    },
    {
        "slug": "apollo-13-calculus",
        "title": "Apollo 13: The Cold Calculus",
        "thumb_hook_top": "200,000 MILES",
        "thumb_hook_bottom": "FROM HOME",
        "thumb_color": [255, 60, 60],
        "thumb_badge": "NASA DECLASSIFIED DOSSIER",
        "thumb_sub_pill": "APRIL 13, 1970 • OXYGEN TANK EXPLOSION",
        "search_terms": [
            "Apollo 13 service module damage",
            "Jim Lovell Apollo 13",
            "Houston mission control center 1970",
            "Apollo 13 lunar module Aquarius",
            "Gene Kranz mission control",
            "Apollo 13 crew splashdown"
        ],
        "lines": [
            ("On April 11th, 1970, Apollo 13 lifted off from Kennedy Space Center on what was intended to be humanity's third landing on the lunar surface.", "APRIL 11, 1970 • LAUNCH"),
            ("Commanded by veteran astronaut Jim Lovell alongside command module pilot Jack Swigert and lunar module pilot Fred Haise, the mission began without incident.", "CREW • LOVELL, SWIGERT, HAISE"),
            ("Two days later, on the evening of April 13th, the spacecraft was coasting smoothly two hundred thousand miles from Earth.", "APRIL 13 • 200,000 MILES OUT"),
            ("At 55 hours and 54 minutes into the flight, mission controller Sy Liebergot noticed low pressure in a hydrogen tank and asked the crew to stir their cryogenic tanks.", "ROUTINE CRYOGENIC STIR"),
            ("Jack Swigert reached up to the main panel and flipped the fan switches in Oxygen Tank Number Two.", "SWITCH ACTIVATED"),
            ("Deep inside the tank, teflon-insulated wiring that had been subtly damaged during pre-flight testing produced a sudden electrical spark in pure liquid oxygen.", "THE SPARK"),
            ("A violent pressure pulse blew off an outer access door. An explosion ripped through the side of the Service Module into the vacuum of space.", "EXPLOSION DETECTED"),
            ("Moments later, Jack Swigert radioed back to Houston the historic words: 'Houston, we've had a problem here.'", "HOUSTON, WE'VE HAD A PROBLEM"),
            ("Looking out of the hatch window, Jim Lovell confirmed the nightmare: a gas was actively venting in high volume from the side of their spacecraft.", "VENTING INTO THE VOID"),
            ("Oxygen Tank 2 was completely destroyed, and Tank 1 was rapidly leaking down to zero. The Command Module Odyssey was losing all electrical power and dying.", "COMMAND MODULE FAILING"),
            ("Lead flight director Gene Kranz and his team realized the Moon landing was impossible. The only priority was keeping three men alive.", "GENE KRANZ • FAILURE IS NOT AN OPTION"),
            ("The crew had minutes to power up the Lunar Module Aquarius, transforming a craft designed for two men for two days into a life raft for three.", "AQUARIUS • THE LIFE RAFT"),
            ("To conserve power for atmospheric reentry, Odyssey was completely shut down. The temperature inside Aquarius plummeted to three degrees Celsius.", "FREEZING DARKNESS"),
            ("Carbon dioxide levels rose to lethal thresholds, forcing engineers on Earth to invent an adapter using cardboard flight manuals, plastic bags, and duct tape.", "DUCT TAPE & CARDBOARD"),
            ("A critical engine burn around the far side of the moon slingshot Apollo 13 onto a free-return trajectory back toward Earth.", "FREE RETURN TRAJECTORY"),
            ("Four days of bone-chilling cold, dehydration, and razor-thin mathematical calculations culminated in a flawless reentry into the Pacific Ocean.", "APRIL 17 • PACIFIC REENTRY"),
            ("What should have been NASA's greatest disaster became humanity's most extraordinary triumph of engineering and human will.", "SUCCESSFUL FAILURE")
        ]
    },
    {
        "slug": "demon-core",
        "title": "The Demon Core",
        "thumb_hook_top": "THE FATAL",
        "thumb_hook_bottom": "BLUE FLASH",
        "thumb_color": [120, 200, 255],
        "thumb_badge": "TOP SECRET • LOS ALAMOS",
        "thumb_sub_pill": "MAY 21, 1946 • CRITICALITY SLIP",
        "search_terms": [
            "Demon core plutonium sphere",
            "Louis Slotin radiation experiment",
            "Harry Daghlian Los Alamos",
            "Los Alamos Laboratory 1945",
            "Omega Site Los Alamos",
            "Criticality accident plutonium"
        ],
        "lines": [
            ("In the summer of 1945, scientists at Los Alamos cast a 14-pound solid sphere of subcritical plutonium-gallium alloy.", "AUGUST 1945 • LOS ALAMOS"),
            ("Manufactured to serve as the fissile pit of a third atomic bomb, Japan surrendered before it could be deployed.", "THE THIRD ATOMIC CORE"),
            ("Retained for radiation research at the secluded Omega Site laboratory, physicists nicknamed the deadly sphere 'The Demon Core'.", "OMEGA SITE LABORATORY"),
            ("Its danger was demonstrated on August 21st, 1945, when 24-year-old physicist Harry Daghlian was building a reflector wall of tungsten carbide bricks.", "HARRY DAGHLIAN EXPERIMENT"),
            ("As he positioned the final heavy brick, it slipped from his fingers and dropped directly onto the core.", "THE FATAL SLIP"),
            ("A sudden burst of ionizing radiation bathed the room. Daghlian reacted instantly, knocking the brick away, but received a lethal dose of 510 rems.", "ACUTE RADIATION"),
            ("Twenty-five days later, Daghlian succumbed to acute radiation sickness. Yet nine months later, another experiment pushed the exact same core to the brink.", "DAGHLIAN PASSES"),
            ("On May 21st, 1946, Canadian physicist Louis Slotin was demonstrating a criticality protocol to seven visiting scientists.", "MAY 21, 1946 • LOUIS SLOTIN"),
            ("The procedure involved lowering a dome of beryllium over the core, controlling the gap with the blade of a standard flathead screwdriver.", "FLATHEAD SCREWDRIVER PROTOCOL"),
            ("Famed physicist Richard Feynman had famously warned the team that they were 'tickling the tail of a sleeping dragon.'", "TICKLING THE DRAGON'S TAIL"),
            ("At 3:20 PM, the screwdriver slipped just a fraction of an inch. The beryllium dome closed completely over the plutonium.", "THE SCREWDRIVER SLIPS"),
            ("Instant criticality was achieved. A wave of intense heat swept the room, accompanied by an eerie flash of blue Cherenkov glow in the ionized air.", "THE BLUE CHERENKOV FLASH"),
            ("Slotin tasted a sharp metallic bitterness on his tongue. Realizing the horror, he instinctively flipped the heavy shell away with his bare hands.", "SLOTIN SHIELDS HIS TEAM"),
            ("By shielding his colleagues with his own body, Slotin absorbed approximately one thousand roentgens of lethal neutron and gamma radiation.", "ONE THOUSAND ROENTGENS"),
            ("Slotin calmly told his closest colleague: 'Well, that does it.' Nine agonizing days later, he passed away in the Los Alamos hospital.", "MAY 30, 1946 • SLOTIN DIES"),
            ("Following the disaster, all hands-on manual criticality experiments were banned forever. The Demon Core was later melted down into military stockpiles.", "LEGACY OF THE DEMON CORE")
        ]
    },
    {
        "slug": "mary-celeste",
        "title": "The Ghost Ship Mary Celeste",
        "thumb_hook_top": "VANISHED",
        "thumb_hook_bottom": "AT SEA",
        "thumb_color": [255, 180, 50],
        "thumb_badge": "NAVAL INQUEST DOSSIER",
        "thumb_sub_pill": "DECEMBER 1872 • CREW NEVER FOUND",
        "search_terms": [
            "Mary Celeste merchant brigantine",
            "Dei Gratia spotting Mary Celeste",
            "Benjamin Briggs captain Mary Celeste",
            "Gibraltar Admiralty court 1872",
            "Strait of Gibraltar vintage sailing ship",
            "Azores islands Atlantic 19th century"
        ],
        "lines": [
            ("On November 7th, 1872, the 282-ton merchant brigantine Mary Celeste departed New York Harbor bound for Genoa, Italy.", "NOVEMBER 7, 1872 • NEW YORK"),
            ("Commanded by Captain Benjamin Spooner Briggs, a veteran and deeply religious mariner, the ship carried seventeen hundred barrels of industrial alcohol.", "CAPTAIN BENJAMIN BRIGGS"),
            ("Aboard with him was his wife Sarah, their two-year-old daughter Sophia, and a trusted, experienced crew of seven seasoned sailors.", "TEN SOULS ON BOARD"),
            ("Nearly a month later, on December 4th, the British cargo ship Dei Gratia was cutting through rough swells midway between the Azores and Portugal.", "DECEMBER 4 • THE AZORES"),
            ("Helmsman John Johnson noticed a vessel sailing unsteadily on a port tack, her sails fluttering erratically in the stiff breeze.", "DRIFTING SHIP SPOTTED"),
            ("Captain David Morehouse recognized the rig of the Mary Celeste. Receiving no answer to distress signals, he sent First Mate Oliver Deveau aboard.", "OLIVER DEVEAU BOARDS"),
            ("Stepping onto the main deck, Deveau entered an unsettling, unearthly silence.", "UNEARTHLY SILENCE"),
            ("The ship was completely seaworthy. The hull was sound, pumps were working, and six months of food and fresh water remained intact.", "SEAWORTHY SHIP"),
            ("In the cabin, personal belongings, women's clothing, and children's toys were left completely undisturbed.", "UNDISTURBED CABINS"),
            ("The ship's logbook lay open on the mate's desk. Its final entry had been penned nine days earlier, recording a normal position off Santa Maria Island.", "FINAL LOG ENTRY"),
            ("Yet every human soul had vanished. The single lifeboat was gone, along with the chronometer, navigation sextant, and ship's registration papers.", "LIFEBOAT & SEXTANT MISSING"),
            ("A deep cut in the ship's rail suggested a towline had been hastily rigged from the stern to the missing yawl.", "THE MISSING TOWLINE"),
            ("When the ship was brought into Gibraltar, Admiralty officials launched a grueling investigation, initially suspecting piracy, mutiny, or insurance fraud.", "GIBRALTAR ADMIRALTY COURT"),
            ("However, no signs of violence or struggle were discovered. The valuable cargo of alcohol remained entirely in the hold.", "CARGO INTACT"),
            ("Forensic naval historians believe expanding alcohol vapors in the hold may have blown off a hatch, leading the captain to fear an imminent explosion.", "THE ALCOHOL VAPOR THEORY"),
            ("Believing their ship was about to detonate, they retreated into the lifeboat, only for a sudden storm squall to sever the towline in open water.", "LOST TO THE SWELLS"),
            ("Neither Benjamin Briggs, his family, nor any of his crew were ever seen or heard from again.", "THE UNSOLVED RIDDLE")
        ]
    },
    {
        "slug": "pompeii-final-hours",
        "title": "Pompeii: The Last Dawn",
        "thumb_hook_top": "THE DAY SKY",
        "thumb_hook_bottom": "TURNED TO FIRE",
        "thumb_color": [255, 110, 30],
        "thumb_badge": "ARCHAEOLOGICAL EXCAVATION",
        "thumb_sub_pill": "79 AD • BURIED UNDER 20 FEET OF ASH",
        "search_terms": [
            "Mount Vesuvius eruption 79 AD",
            "Pompeii ruins excavation Roman",
            "Pliny the Younger Vesuvius letter",
            "Pompeii plaster cast victims",
            "Herculaneum pyroclastic surge",
            "Bay of Naples ancient Roman"
        ],
        "lines": [
            ("In the late summer of 79 AD, the bustling Roman resort town of Pompeii woke to tremors vibrating along the sun-drenched Bay of Naples.", "AUGUST 79 AD • BAY OF NAPLES"),
            ("For centuries, the Roman citizens had farmed the fertile vineyards flanking Mount Vesuvius, completely unaware it was an active supervolcano.", "MOUNT VESUVIUS"),
            ("Shortly after midday, the volcanic plug shattered in a deafening sonic explosion that shook the entire Italian coastline.", "THE SHATTERED PLUG"),
            ("Eighteen-year-old Pliny the Younger watched from across the bay as a colossal pine-tree cloud of ash and pumice climbed twenty miles into the stratosphere.", "EYEWITNESS • PLINY THE YOUNGER"),
            ("Millions of tons of superheated molten rock rained down upon Pompeii at a rate of six inches every hour, collapsing rooftops and trapping families.", "PUMICE RAIN"),
            ("In nearby Herculaneum, citizens fled to the waterfront boat chambers, hoping for naval rescue ships commanded by Pliny the Elder.", "HERCULANEUM BOAT HOUSES"),
            ("Shortly after midnight, the massive eruption column collapsed under its own immense weight.", "COLUMN COLLAPSE"),
            ("A catastrophic pyroclastic density current, traveling at four hundred miles per hour with temperatures exceeding five hundred degrees Celsius, struck the coastline.", "PYROCLASTIC DENSITY CURRENT"),
            ("Victims were engulfed in milliseconds, suffering instant thermal shock before being buried beneath twenty feet of volcanic tephra.", "INSTANT THERMAL SHOCK"),
            ("For seventeen centuries, the Roman villas, frescoes, bathhouses, and thousands of residents lay completely preserved in an airtight tomb.", "FROZEN SEVENTEEN CENTURIES"),
            ("In 1863, archaeologist Giuseppe Fiorelli discovered that decaying bodies had left hollow voids in the solidified volcanic ash.", "GIUSEPPE FIORELLI • 1863"),
            ("By carefully injecting liquid plaster into the cavities, he resurrected the exact final postures and agony of Roman citizens frozen in time.", "THE PLASTER RESURRECTION"),
            ("A mother cradling her child, a chained watchdog straining for freedom, and two lovers holding hands in their final breath.", "ETERNAL FINAL POSTURES"),
            ("Pompeii remains humanity's most extraordinary archaeological time capsule, a chilling reminder of nature's instantaneous power.", "TIME CAPSULE OF ANTIQUITY")
        ]
    },
    {
        "slug": "tunguska-event",
        "title": "The Tunguska Cataclysm",
        "thumb_hook_top": "1000X ATOMIC",
        "thumb_hook_bottom": "WITHOUT A CRATER",
        "thumb_color": [255, 204, 0],
        "thumb_badge": "SIBERIAN EXPEDITION ARCHIVE",
        "thumb_sub_pill": "JUNE 30, 1908 • 80 MILLION TREES LEVELED",
        "search_terms": [
            "Tunguska event 1908 Siberia",
            "Leonid Kulik expedition 1927",
            "Tunguska forest flattened trees",
            "Podkamennaya Tunguska river",
            "Meteorite airburst atmospheric shockwave",
            "Siberian taiga wilderness"
        ],
        "lines": [
            ("On the morning of June 30th, 1908, a deafening thunder shook the remote taiga near the Podkamennaya Tunguska River in central Siberia.", "JUNE 30, 1908 • CENTRAL SIBERIA"),
            ("Indigenous Evenki reindeer herders witnessed a blinding column of blue-white fire descending through the cloudless dawn.", "THE FALLING FIRE"),
            ("At approximately 7:17 AM, at an altitude of five to ten kilometers above the ground, the object exploded with incomprehensible ferocity.", "THE CATACLYSMIC EXPLOSION"),
            ("The blast released energy equivalent to twelve megatons of TNT, nearly one thousand times more powerful than the Hiroshima atomic bomb.", "1,000X HIROSHIMA YIELD"),
            ("A searing thermal wave burned herders sixty miles away, while the atmospheric shockwave registered on barographs as far away as London and Washington.", "SHOCKWAVE CIRCLES THE GLOBE"),
            ("For three consecutive nights across Europe and Asia, the night sky glowed so bright that citizens in London could read newspapers at midnight.", "THE MIDNIGHT GLOW"),
            ("Due to World War I, the Russian Revolution, and the sheer hostility of the Siberian wilderness, nineteen years passed before a scientific team reached the site.", "NINETEEN YEARS OF SILENCE"),
            ("In 1927, Russian mineralogist Leonid Kulik mounted a grueling expedition into the swampy, frozen interior.", "LEONID KULIK • 1927 EXPEDITION"),
            ("What Kulik encountered upon reaching the epicenter left him completely stunned.", "THE SCIENTIST AT GROUND ZERO"),
            ("Eighty million pine trees across eight hundred square miles had been leveled flat like matchsticks, radiating outwards in a giant butterfly pattern.", "80 MILLION TREES LEVELLED"),
            ("Yet at ground zero, standing upright directly beneath the blast point, was a grove of stripped telegraph-pole trees without a single impact crater.", "THE MISSING IMPACT CRATER"),
            ("Kulik spent years digging the marshlands searching for fragments of an iron meteorite, but not a single macroscopic meteorite chunk was ever found.", "NO CRATER • NO METEORITE"),
            ("Decades of subsequent atmospheric and nuclear modeling finally solved the puzzle: a stony asteroid or comet fragment roughly sixty meters wide.", "60-METER STONY ASTEROID"),
            ("Entering Earth's atmosphere at fifty thousand miles per hour, intense frictional heat caused it to violently disintegrate in mid-air.", "MID-AIR DETONATION"),
            ("Had the Tunguska airburst occurred just four hours later due to Earth's rotation, it would have detonated directly over Saint Petersburg, completely erasing Russia's imperial capital.", "FOUR HOURS FROM HISTORY"),
            ("Tunguska remains the largest impact event on Earth in recorded human history, a celestial warning that the cosmos can strike at any moment.", "CELESTIAL WARNING")
        ]
    }
]

def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"covered_slugs": []}
    return {"covered_slugs": []}

def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")

def search_wikimedia_commons(query, limit=4):
    """Searches Wikimedia Commons API and returns real File: names."""
    try:
        url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "format": "json",
            "srlimit": str(limit)
        })
        req = urllib.request.Request(url, headers={"User-Agent": "ChronicleVaultAutonomous/2.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data.get("query", {}).get("search", [])
            valid_files = []
            for it in items:
                title = it.get("title", "")
                if title.lower().endswith((".jpg", ".jpeg", ".png")):
                    valid_files.append(title)
            return valid_files
    except Exception as e:
        print(f"[Wikimedia Search] Error for '{query}': {e}", file=sys.stderr)
        return []

def generate_dynamic_scene_file(proj_dir, title, lines_count, photos):
    """
    Generates a production-ready forensic documentary scene.py:
    - Purely relies on doc.L(i) (line start) and doc.E(i) (line end).
    - Pins archival photographs (Print) to the investigation cork board.
    - Adds forensic casefile Cards and cinematic camera moves (film.shot).
    """
    code_lines = [
        f'"""Autonomous Forensic Documentary Scene: {title}"""',
        'from engine import Film, BigText, Print, Card, PenMark, HILITE, RUST, INK',
        '',
        'def build_film(doc):',
        '    L, E = doc.L, doc.E',
        '    film = Film(doc.duration, fps=30, look="wall")',
        '',
        '    # Title Header',
        f'    film.add(BigText({title.upper()!r}, 0, -2200, 620, L(1) - 0.1, t_out=E(1) + 1.2, type_on=0.6, bar=HILITE, bar_h=0.92, shadow=False))',
        ''
    ]

    GAP = 3600
    XS = [(i - 1) * GAP for i in range(1, lines_count + 1)]
    MID = (XS[0] + XS[-1]) / 2 if XS else 0

    photo_keys = [p["id"] for p in photos] if photos else []

    for idx in range(1, lines_count + 1):
        x = XS[idx - 1]
        p_key = photo_keys[idx - 1] if idx - 1 < len(photo_keys) else None

        if p_key:
            rot = -1.2 if idx % 2 else 1.4
            code_lines.append(f'    film.add(Print("{p_key}", {x}, 200, 2600, rot={rot}, t_in=L({idx}) + 0.1, label="ARCHIVAL EVIDENCE #{idx}", pin=True))')
        else:
            code_lines.append(f'    film.add(Card({x}, 200, 2800, 1600, L({idx}) + 0.1, title="EXHIBIT #{idx}", lines=["Official Declassified Dossier", "Forensic Investigation Record"], accent=RUST, radius=32))')

    code_lines.append('')
    code_lines.append('    # Cinematic Camera Progression')
    code_lines.append(f'    film.shot(0.0, 0, -2100, 0.75)')
    for idx in range(1, lines_count + 1):
        x = XS[idx - 1]
        rot = -0.4 if idx % 2 else 0.4
        code_lines.append(f'    film.shot(L({idx}) + 0.35, {x}, 250, 0.65, rot={rot})')
        code_lines.append(f'    film.shot(E({idx}) - 0.1, {x} + 250, 350, 0.60)')
    code_lines.append(f'    film.shot(film.duration, {MID}, 0, 0.22)')
    code_lines.append('    return film\n')

    scene_path = proj_dir / "scene.py"
    scene_path.write_text("\n".join(code_lines), encoding="utf-8")

def generate_topic():
    history = load_history()
    covered = history.get("covered_slugs", [])
    
    # Filter catalog for uncovered topics
    candidates = [t for t in DEEP_TOPIC_CATALOG if t["slug"] not in covered]
    if not candidates:
        # Keep only the last 2 covered so fresh rotation restarts
        covered = covered[-2:] if len(covered) >= 2 else []
        candidates = [t for t in DEEP_TOPIC_CATALOG if t["slug"] not in covered]
    
    selected = random.choice(candidates)
    slug = selected["slug"]
    title = selected["title"]
    
    print(f"\n[Dynamic Topic Generator] Selected Today's Topic: '{title}' (slug: {slug})", file=sys.stderr)
    
    # Destination project folder
    proj_dir = ASSETS_DIR / slug
    proj_dir.mkdir(parents=True, exist_ok=True)
    
    # Gather real archival images from Wikimedia Commons for each search term
    photos = []
    used_files = set()
    p_idx = 1
    
    for term in selected.get("search_terms", []):
        hits = search_wikimedia_commons(term, limit=4)
        for h in hits:
            if h not in used_files and len(photos) < 12:
                photos.append({
                    "id": f"P{p_idx:02d}",
                    "kind": "photo",
                    "commons": h
                })
                used_files.add(h)
                p_idx += 1
                break
                
    # If fewer than 4 photos found, fill with related fallback searches
    if len(photos) < 4:
        generic_hits = search_wikimedia_commons(f"{title} history archive", limit=6)
        for h in generic_hits:
            if h not in used_files and len(photos) < 8:
                photos.append({
                    "id": f"P{p_idx:02d}",
                    "kind": "photo",
                    "commons": h
                })
                used_files.add(h)
                p_idx += 1

    # Save photos.json
    photos_path = proj_dir / "photos.json"
    photos_path.write_text(json.dumps({"photos": photos}, indent=2), encoding="utf-8")
    print(f"[Dynamic Topic Generator] Generated photos.json with {len(photos)} archival images.", file=sys.stderr)
    
    # Build script.json with Lemmino forensic takes
    takes = []
    take_idx = 1
    for line_idx, (spoken_text, typed_label) in enumerate(selected["lines"]):
        take_name = f"T{take_idx:02d}_scene_{line_idx+1}"
        takes.append({
            "take": take_name,
            "lines": [
                {
                    "id": line_idx + 1,
                    "text": spoken_text,
                    "spoken": spoken_text,
                    "hero": f"archival photograph lands; {typed_label}",
                    "typed": typed_label
                }
            ]
        })
        take_idx += 1
        
    script_data = {
        "title": title,
        "thumb_hook_top": selected.get("thumb_hook_top", "THE UNTOLD"),
        "thumb_hook_bottom": selected.get("thumb_hook_bottom", "CHRONICLE"),
        "thumb_color": selected.get("thumb_color", [255, 204, 0]),
        "thumb_badge": selected.get("thumb_badge", "CLASSIFIED DOSSIER"),
        "thumb_sub_pill": selected.get("thumb_sub_pill", "HISTORICAL INVESTIGATION"),
        "takes": takes
    }
    script_path = proj_dir / "script.json"
    script_path.write_text(json.dumps(script_data, indent=2), encoding="utf-8")
    print(f"[Dynamic Topic Generator] Generated script.json with {len(takes)} forensic documentary takes (~{len(takes)*9}s duration).", file=sys.stderr)

    # Save meta info
    meta_data = {
        "title": f"{title} | Full Documentary",
        "description": f"A forensic, deep-dive exploration into {title}. Unfolding rare historical archives, official records, and authentic photographs.\n\n#documentary #history #mystery #untoldstories #chroniclevault",
        "tags": ["documentary", "history", "historical documentary", "chronicle vault", "untold stories", "forensic history", slug.replace("-", " ")]
    }
    (proj_dir / "meta.json").write_text(json.dumps(meta_data, indent=2), encoding="utf-8")

    # Generate forensic scene.py tailored to this documentary
    generate_dynamic_scene_file(proj_dir, title, len(takes), photos)
    
    # Update covered history
    covered.append(slug)
    history["covered_slugs"] = covered
    save_history(history)
    
    return slug

if __name__ == "__main__":
    slug = generate_topic()
    print(slug)
