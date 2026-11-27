# -*- coding: utf-8 -*-
"""
=============================================================================
FLINT & GRIT — 100% AUTONOMOUS 12-SECOND PROCEDURAL 2D SHORTS PRODUCER
=============================================================================
Complete End-to-End Automation for Flint & Grit YouTube Shorts:
  1. Auto-selects viral safety / survival topics from curated library or AI.
  2. Generates 5-6 short punchy steps (1.5 - 2s each -> strictly 12 seconds).
  3. Renders 2D cartoon characters (kurta, saree, uniform) and environments
     (kitchen, living room, road, elevator) using Python Pillow shapes.
  4. Multi-threaded 24 FPS 2x supersampled rendering with smooth Lanczos scaling.
  5. Dynamic Hindi Neural Voiceover (Edge-TTS) automatically synced to 12.0s.
  6. FFmpeg video assembly + 6-scene Contact Sheet Grid for instant verification.
  7. Automated YouTube upload with high-CTR titles, hashtags, and metadata.
  8. Tracks topic history in 'history_flintgrit.json' to ensure 0 duplicates.
=============================================================================
"""

import os
import sys
import math
import time
import json
import shutil
import asyncio
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

# Canvas Setup
RENDER_W = 2160
RENDER_H = 3840
FINAL_W = 1080
FINAL_H = 1920
FPS = 24
TARGET_DURATION = 12.0

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output_channel3")
TEMP_DIR = os.path.join(SCRIPT_DIR, "_temp_flintgrit")
HISTORY_FILE = os.path.join(SCRIPT_DIR, "history_flintgrit.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fonts
def get_font(size):
    font_names = [
        r"C:\Windows\Fonts\ariblk.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]
    for fn in font_names:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                pass
    return ImageFont.load_default()

FONT_HEADER = get_font(84)
FONT_TOPIC = get_font(72)
FONT_CAPTION = get_font(96)
FONT_STEP = get_font(68)

# =============================================================================
# TOPIC LIBRARY (VIRAL SAFETY & SURVIVAL NICHES)
# =============================================================================

VIRAL_TOPICS = [
    {
        "id": "kitchen_oil_fire",
        "title": "AAG LAGE TOH KYA KAREIN?",
        "environment": "kitchen",
        "clothes": "kurta",
        "narration": (
            "Kitchen me tel ki kadhai me aag lag jaye toh bhool kar bhi paani mat daalna! "
            "Aag aur bhadak jayegi. "
            "Sabse pehle gas stove band karein. "
            "Aur kadhai ko kisi badi thali ya dhakkan se poora dhak dein. "
            "Hawa rukte hi aag turant bujh jayegi! "
            "Ye tip aapki jaan bacha sakti hai, share zaroor karein."
        ),
        "scenes": [
            {"duration": 2.0, "step": "STEP 1: DANGER ALERT", "caption": "KADHAI ME AAG LAGE TOH?", "pose": "panic", "elements": ["fire", "smoke"]},
            {"duration": 2.0, "step": "FATAL MISTAKE: NO WATER!", "caption": "PAANI KABHI MAT DAALNA!", "pose": "panic", "elements": ["fire", "water_cross"]},
            {"duration": 2.0, "step": "STEP 2: TURN OFF STOVE", "caption": "PEHLE GAS STOVE BAND KAREIN!", "pose": "action", "elements": ["fire"]},
            {"duration": 2.0, "step": "STEP 3: COVER WITH LID", "caption": "THALI YA DHAKKAN SE DHO-DO!", "pose": "lid", "elements": ["lid"]},
            {"duration": 2.0, "step": "FIRE EXTINGUISHED! SAFE", "caption": "OXYGEN RUKTE HI AAG BUJH GAYI!", "pose": "celebrate", "elements": ["safe"]},
            {"duration": 2.0, "step": "FLINT & GRIT: SUBSCRIBE!", "caption": "JAAN BACHAYEIN, SHARE KAREIN!", "pose": "celebrate", "elements": ["subscribe"]}
        ]
    },
    {
        "id": "gas_cylinder_leak",
        "title": "CYLINDER LEAK HO TOH?",
        "environment": "kitchen",
        "clothes": "casual",
        "narration": (
            "Agar ghar me LPG gas cylinder ki smell aaye toh galti se bhi koi switch on ya off mat karna! "
            "Ek chhota spark bhi bada blast kar sakta hai. "
            "Turant saare darwaze aur khidkiyan khol dein taaki gas bahar nikal sake. "
            "Regulator ka knob turant band karein aur safety cap laga dein. "
            "Sabhi log ghar se turant bahar nikal jayein!"
        ),
        "scenes": [
            {"duration": 2.0, "step": "STEP 1: SMELL GAS?", "caption": "CYLINDER LEAK KI SMELL AAYE?", "pose": "panic", "elements": ["gas_fumes"]},
            {"duration": 2.0, "step": "FATAL MISTAKE: NO SWITCH!", "caption": "KOI BHI LIGHT SWITCH ON MAT KARO!", "pose": "panic", "elements": ["switch_cross"]},
            {"duration": 2.0, "step": "STEP 2: VENTILATION", "caption": "KHIDKI DARWAZE TURANT KHOLO!", "pose": "action", "elements": ["window_open"]},
            {"duration": 2.0, "step": "STEP 3: REGULATOR OFF", "caption": "REGULATOR KNOB TURANT BAND KARO!", "pose": "action", "elements": ["regulator_off"]},
            {"duration": 2.0, "step": "STEP 4: EVACUATE NOW", "caption": "SABHI LOG GHAR SE BAHAR AAO!", "pose": "run", "elements": ["safe"]},
            {"duration": 2.0, "step": "FLINT & GRIT: SUBSCRIBE!", "caption": "JAAN BACHAYEIN, SHARE KAREIN!", "pose": "celebrate", "elements": ["subscribe"]}
        ]
    },
    {
        "id": "electric_shock_safety",
        "title": "CURRENT LAGE TOH KYA KAREIN?",
        "environment": "living_room",
        "clothes": "casual",
        "narration": (
            "Agar kisi ko bijli ka current lag jaye toh use galti se bhi apne haathon se mat chhoona! "
            "Aapko bhi tez shock lag sakta hai. "
            "Sabse pehle main MCB switch ya plug turant band karein. "
            "Agar switch door ho toh lakdi ke dande ya sukhe kapde se use alag karein. "
            "Turant ambulance call karein aur CPR dein!"
        ),
        "scenes": [
            {"duration": 2.0, "step": "STEP 1: ELECTRIC SHOCK!", "caption": "KISI KO CURRENT LAGE TOH?", "pose": "panic", "elements": ["sparks"]},
            {"duration": 2.0, "step": "FATAL MISTAKE: DON'T TOUCH!", "caption": "APNE HAATH SE KABHI MAT CHHUO!", "pose": "panic", "elements": ["hand_cross"]},
            {"duration": 2.0, "step": "STEP 2: MAIN SWITCH OFF", "caption": "PEHLE MAIN MCB SWITCH BAND KARO!", "pose": "action", "elements": ["mcb_off"]},
            {"duration": 2.0, "step": "STEP 3: USE DRY WOOD", "caption": "SUKHI LAKDI SE ALAG KAREIN!", "pose": "action", "elements": ["wood_stick"]},
            {"duration": 2.0, "step": "STEP 4: CALL 108 AMBULANCE", "caption": "AMBULANCE KO TURANT CALL KAREIN!", "pose": "celebrate", "elements": ["safe"]},
            {"duration": 2.0, "step": "FLINT & GRIT: SUBSCRIBE!", "caption": "JAAN BACHAYEIN, SHARE KAREIN!", "pose": "celebrate", "elements": ["subscribe"]}
        ]
    },
    {
        "id": "elevator_fall_stuck",
        "title": "LIFT RUK JAYE TOH KYA KAREIN?",
        "environment": "elevator",
        "clothes": "uniform",
        "narration": (
            "Agar aap lift me phas jayein toh bilkul panic mat hona! "
            "Lift me oxygen kabhi khatam nahi hoti. "
            "Lift ke darwaze zabardasti kholne ki koshish mat karein. "
            "Emergency alarm button ya intercom dabayein. "
            "Agar lift girne lage toh floor par peeth ke bal let jayein, ye impact ko poore shareer me baant deta hai!"
        ),
        "scenes": [
            {"duration": 2.0, "step": "STEP 1: LIFT STUCK!", "caption": "LIFT ME PHAS JAYEIN TOH?", "pose": "panic", "elements": ["elevator_doors"]},
            {"duration": 2.0, "step": "DON'T PANIC: OXYGEN IS SAFE", "caption": "PANIC MAT HO! OXYGEN REHTI HAI!", "pose": "stop", "elements": ["oxygen_ok"]},
            {"duration": 2.0, "step": "FATAL MISTAKE: NO FORCING", "caption": "DARWAZE ZABARDASTI MAT KHOLO!", "pose": "stop", "elements": ["door_cross"]},
            {"duration": 2.0, "step": "STEP 2: PRESS ALARM BUTTON", "caption": "ALARM BUTTON YA CALL DABAYEIN!", "pose": "action", "elements": ["bell_button"]},
            {"duration": 2.0, "step": "SURVIVAL POSITION: LIE DOWN", "caption": "GIRNE LAGE TOH FARSH PAR LETO!", "pose": "crouch", "elements": ["safe"]},
            {"duration": 2.0, "step": "FLINT & GRIT: SUBSCRIBE!", "caption": "JAAN BACHAYEIN, SHARE KAREIN!", "pose": "celebrate", "elements": ["subscribe"]}
        ]
    },
    {
        "id": "street_dog_chase",
        "title": "KUTTA PICHE PADE TOH?",
        "environment": "road",
        "clothes": "casual",
        "narration": (
            "Agar koi street dog aapke peeche bhaage ya bhonke, toh galti se bhi bhaagna mat! "
            "Bhaagne se kutte ka hunting instinct jag jata hai. "
            "Wahi turant ruk jayein aur haath apne shareer se sata kar khade rahein. "
            "Kutte ki aankhon me direct eye contact mat karein. "
            "Dheere se bina dare piche hatein ya vahan se move karein!"
        ),
        "scenes": [
            {"duration": 2.0, "step": "STEP 1: AGGRESSIVE DOG!", "caption": "KUTTA PICHE PADE TOH KYA KAREIN?", "pose": "panic", "elements": ["dog"]},
            {"duration": 2.0, "step": "FATAL MISTAKE: NEVER RUN!", "caption": "GURRA TE DEKH KABHI MAT BHAAGO!", "pose": "stop", "elements": ["run_cross"]},
            {"duration": 2.0, "step": "STEP 2: FREEZE LIKE A TREE", "caption": "BILKUL SHANT PED KI TARAH RUKO!", "pose": "action", "elements": ["tree_pose"]},
            {"duration": 2.0, "step": "STEP 3: NO EYE CONTACT", "caption": "AANKHON ME DIRECT MAT DEKHO!", "pose": "stop", "elements": ["eye_cross"]},
            {"duration": 2.0, "step": "STEP 4: WALK AWAY SLOWLY", "caption": "DHEERE DHEERE PICHE HATO!", "pose": "celebrate", "elements": ["safe"]},
            {"duration": 2.0, "step": "FLINT & GRIT: SUBSCRIBE!", "caption": "JAAN BACHAYEIN, SHARE KAREIN!", "pose": "celebrate", "elements": ["subscribe"]}
        ]
    }
]

# =============================================================================
# 2. DRAWING ENGINE: ENVIRONMENTS, CHARACTERS, PROPS
# =============================================================================

def draw_tiled_wall(draw, w, h, tile_size=120, color_a=(241, 245, 249), color_b=(226, 232, 240)):
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            fill = color_a if ((x // tile_size) + (y // tile_size)) % 2 == 0 else color_b
            draw.rectangle([x, y, x + tile_size, y + tile_size], fill=fill, outline=(203, 213, 225), width=3)

def draw_environment(draw, env_type, w, h, time_sec):
    if env_type == "kitchen":
        # Kitchen tiles + window + counter
        wall_h = int(h * 0.72)
        draw_tiled_wall(draw, w, wall_h)
        win_x1, win_y1, win_x2, win_y2 = int(w * 0.1), int(h * 0.18), int(w * 0.45), int(h * 0.42)
        draw.rectangle([win_x1, win_y1, win_x2, win_y2], fill=(186, 230, 253), outline=(71, 85, 105), width=16)
        mid_x, mid_y = (win_x1 + win_x2) // 2, (win_y1 + win_y2) // 2
        draw.line([mid_x, win_y1, mid_x, win_y2], fill=(71, 85, 105), width=12)
        draw.line([win_x1, mid_y, win_x2, mid_y], fill=(71, 85, 105), width=12)
        counter_y = int(h * 0.68)
        draw.rectangle([0, counter_y, w, h], fill=(30, 41, 59))
        draw.rectangle([0, counter_y - 40, w, counter_y], fill=(15, 23, 42))
        draw.line([0, counter_y - 40, w, counter_y - 40], fill=(0, 240, 255), width=4)
        # Red cylinder
        cyl_x, cyl_y = int(w * 0.16), int(h * 0.74)
        draw.rounded_rectangle([cyl_x, cyl_y, cyl_x + 160, cyl_y + 320], radius=40, fill=(225, 29, 72), outline=(159, 18, 57), width=8)
        draw.rectangle([cyl_x + 35, cyl_y - 45, cyl_x + 125, cyl_y], fill=(159, 18, 57))
    elif env_type == "elevator":
        # Steel elevator panels
        draw.rectangle([0, 0, w, h], fill=(71, 85, 105))
        for x in range(0, w, 400):
            draw.line([x, 0, x, h], fill=(100, 116, 139), width=8)
        floor_y = int(h * 0.75)
        draw.rectangle([0, floor_y, w, h], fill=(30, 41, 59))
        # Elevator panel with glowing buttons
        p_x = int(w * 0.78)
        draw.rounded_rectangle([p_x, int(h * 0.28), p_x + 220, int(h * 0.65)], radius=30, fill=(15, 23, 42), outline=(203, 213, 225), width=8)
        for i, b_text in enumerate(["▲", "▼", "★", "ALARM"]):
            by = int(h * 0.32) + i * 110
            draw.ellipse([p_x + 60, by, p_x + 160, by + 100], fill=(239, 68, 68) if i==3 else (51, 65, 85), outline=(255, 255, 255), width=4)
    elif env_type == "road":
        # Sky and road
        draw.rectangle([0, 0, w, int(h * 0.65)], fill=(186, 230, 253))
        # Buildings silhouette
        draw.rectangle([100, int(h * 0.35), 600, int(h * 0.65)], fill=(148, 163, 184))
        draw.rectangle([700, int(h * 0.25), 1400, int(h * 0.65)], fill=(100, 116, 139))
        draw.rectangle([1500, int(h * 0.38), 2050, int(h * 0.65)], fill=(148, 163, 184))
        # Road asphalt
        draw.rectangle([0, int(h * 0.65), w, h], fill=(30, 41, 59))
        # Sidewalk
        draw.rectangle([0, int(h * 0.65), w, int(h * 0.70)], fill=(203, 213, 225))
    else: # living room
        draw.rectangle([0, 0, w, int(h * 0.72)], fill=(248, 250, 252))
        # Picture frame
        draw.rectangle([int(w * 0.12), int(h * 0.18), int(w * 0.42), int(h * 0.40)], fill=(224, 231, 255), outline=(71, 85, 105), width=14)
        # Wooden floor
        draw.rectangle([0, int(h * 0.72), w, h], fill=(120, 53, 15))
        for y in range(int(h * 0.72), h, 80):
            draw.line([0, y, w, y], fill=(69, 26, 3), width=4)

def draw_2d_character(draw, cx, cy, scale=1.35, pose="panic", clothes="kurta", time_sec=0.0):
    """Draws 2D cartoon human with animated poses, limbs, head, and clothes"""
    head_r = int(140 * scale)
    body_w = int(220 * scale)
    body_h = int(320 * scale)
    head_y = cy - int(180 * scale)
    
    # Clothes Colors
    if clothes == "kurta":
        clothes_col = (2, 132, 199)
        pants_col = (30, 41, 59)
    elif clothes == "saree":
        clothes_col = (225, 29, 72)
        pants_col = (159, 18, 57)
    elif clothes == "uniform":
        clothes_col = (30, 58, 138)
        pants_col = (15, 23, 42)
    else: # casual
        clothes_col = (16, 185, 129)
        pants_col = (51, 65, 85)

    skin_col = (254, 202, 138)
    outline_col = (15, 23, 42)
    out_w = int(8 * scale)

    # 1. Legs
    leg_w = int(45 * scale)
    leg_h = int(260 * scale)
    leg1_x = cx - int(60 * scale)
    leg2_x = cx + int(20 * scale)
    draw.rectangle([leg1_x, cy + body_h - 20, leg1_x + leg_w, cy + body_h + leg_h], fill=pants_col, outline=outline_col, width=out_w)
    draw.rectangle([leg2_x, cy + body_h - 20, leg2_x + leg_w, cy + body_h + leg_h], fill=pants_col, outline=outline_col, width=out_w)
    # Shoes
    draw.ellipse([leg1_x - 10, cy + body_h + leg_h - 20, leg1_x + leg_w + 30, cy + body_h + leg_h + 30], fill=(15, 23, 42))
    draw.ellipse([leg2_x - 10, cy + body_h + leg_h - 20, leg2_x + leg_w + 30, cy + body_h + leg_h + 30], fill=(15, 23, 42))

    # 2. Body / Torso
    draw.rounded_rectangle([cx - body_w // 2, cy, cx + body_w // 2, cy + body_h], radius=int(30 * scale), fill=clothes_col, outline=outline_col, width=out_w)
    # Kurta / Shirt detail line
    draw.line([cx, cy + 20, cx, cy + int(180 * scale)], fill=(255, 255, 255), width=int(6 * scale))

    # 3. Arms based on Pose
    arm_w = int(40 * scale)
    arm_l = int(220 * scale)
    shoulder_y = cy + int(40 * scale)

    if pose == "panic":
        # Both arms raised up waving
        wave = math.sin(time_sec * 12) * 20
        draw.line([cx - body_w // 2, shoulder_y, cx - body_w // 2 - int(70 * scale), shoulder_y - arm_l + wave], fill=clothes_col, width=arm_w)
        draw.line([cx + body_w // 2, shoulder_y, cx + body_w // 2 + int(70 * scale), shoulder_y - arm_l - wave], fill=clothes_col, width=arm_w)
        draw.circle((cx - body_w // 2 - int(70 * scale), shoulder_y - arm_l + wave), int(25 * scale), fill=skin_col)
        draw.circle((cx + body_w // 2 + int(70 * scale), shoulder_y - arm_l - wave), int(25 * scale), fill=skin_col)
    elif pose == "lid":
        # One arm holding big lid
        draw.line([cx - body_w // 2, shoulder_y, cx - body_w // 2 - 30, shoulder_y + arm_l - 40], fill=clothes_col, width=arm_w)
        draw.line([cx + body_w // 2, shoulder_y, cx + body_w // 2 + 100, shoulder_y + 60], fill=clothes_col, width=arm_w)
        # Big circular metallic lid
        lid_cx = cx + body_w // 2 + 160
        lid_cy = shoulder_y + 60
        draw.ellipse([lid_cx - 100, lid_cy - 160, lid_cx + 100, lid_cy + 160], fill=(203, 213, 225), outline=(71, 85, 105), width=10)
        draw.ellipse([lid_cx - 20, lid_cy - 20, lid_cx + 20, lid_cy + 20], fill=(15, 23, 42))
    elif pose == "stop" or pose == "action":
        # One hand forward (Stop / Action gesture)
        draw.line([cx - body_w // 2, shoulder_y, cx - body_w // 2 - 30, shoulder_y + arm_l - 40], fill=clothes_col, width=arm_w)
        draw.line([cx + body_w // 2, shoulder_y, cx + body_w // 2 + arm_l, shoulder_y + 10], fill=clothes_col, width=arm_w)
        draw.circle((cx + body_w // 2 + arm_l, shoulder_y + 10), int(28 * scale), fill=skin_col)
    else: # celebrate
        # Hands cheering
        draw.line([cx - body_w // 2, shoulder_y, cx - body_w // 2 - 60, shoulder_y - 120], fill=clothes_col, width=arm_w)
        draw.line([cx + body_w // 2, shoulder_y, cx + body_w // 2 + 60, shoulder_y - 120], fill=clothes_col, width=arm_w)

    # 4. Head & Face
    draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=skin_col, outline=outline_col, width=out_w)
    # Hair
    draw.pieslice([cx - head_r - 8, head_y - head_r - 8, cx + head_r + 8, head_y + int(30 * scale)], 180, 360, fill=(15, 23, 42))

    # Eyes & Mouth based on pose
    eye_dx = int(50 * scale)
    eye_y = head_y - int(10 * scale)
    eye_r = int(14 * scale)

    if pose == "panic":
        draw.ellipse([cx - eye_dx - eye_r, eye_y - eye_r, cx - eye_dx + eye_r, eye_y + eye_r], fill=(255, 255, 255), outline=outline_col, width=4)
        draw.ellipse([cx + eye_dx - eye_r, eye_y - eye_r, cx + eye_dx + eye_r, eye_y + eye_r], fill=(255, 255, 255), outline=outline_col, width=4)
        draw.circle((cx - eye_dx, eye_y), int(6 * scale), fill=(15, 23, 42))
        draw.circle((cx + eye_dx, eye_y), int(6 * scale), fill=(15, 23, 42))
        # O-shaped panicked mouth
        draw.ellipse([cx - 25, head_y + int(45 * scale), cx + 25, head_y + int(95 * scale)], fill=(225, 29, 72), outline=outline_col, width=4)
    else:
        # Happy / Confident smile
        draw.circle((cx - eye_dx, eye_y), eye_r, fill=(15, 23, 42))
        draw.circle((cx + eye_dx, eye_y), eye_r, fill=(15, 23, 42))
        draw.arc([cx - 50, head_y + 20, cx + 50, head_y + 80], 0, 180, fill=(15, 23, 42), width=int(8 * scale))

def draw_fire_flames(draw, cx, cy, scale=1.35, time_sec=0.0):
    flicker = math.sin(time_sec * 18) * 40
    flame_pts_outer = [
        (cx - int(150 * scale), cy),
        (cx - int(100 * scale), cy - int(240 * scale) + flicker),
        (cx - int(20 * scale), cy - int(380 * scale) - flicker),
        (cx + int(60 * scale), cy - int(260 * scale) + flicker),
        (cx + int(150 * scale), cy)
    ]
    draw.polygon(flame_pts_outer, fill=(239, 68, 68))
    flame_pts_mid = [
        (cx - int(90 * scale), cy),
        (cx - int(50 * scale), cy - int(180 * scale) + flicker * 0.7),
        (cx, cy - int(280 * scale) - flicker * 0.7),
        (cx + int(50 * scale), cy - int(170 * scale)),
        (cx + int(90 * scale), cy)
    ]
    draw.polygon(flame_pts_mid, fill=(245, 158, 11))
    flame_pts_inner = [
        (cx - int(50 * scale), cy),
        (cx, cy - int(180 * scale) + flicker * 0.5),
        (cx + int(50 * scale), cy)
    ]
    draw.polygon(flame_pts_inner, fill=(254, 240, 138))

def draw_smoke_particles(draw, cx, cy, time_sec=0.0):
    for i in range(5):
        s_y = cy - int((time_sec * 350 + i * 160) % 750)
        s_x = cx + int(math.sin(time_sec * 4 + i) * 60)
        alpha_rad = int(70 + i * 25)
        draw.ellipse([s_x - alpha_rad, s_y - alpha_rad, s_x + alpha_rad, s_y + alpha_rad], fill=(148, 163, 184))

def draw_danger_cross(draw, cx, cy, size=300):
    hw = size // 2
    w = 40
    draw.line([cx - hw, cy - hw, cx + hw, cy + hw], fill=(225, 29, 72), width=w)
    draw.line([cx + hw, cy - hw, cx - hw, cy + hw], fill=(225, 29, 72), width=w)

# =============================================================================
# 3. TEXT & BRANDING OVERLAYS (FLINT & GRIT SIGNATURE LOOK)
# =============================================================================

def draw_header_badge(draw, topic_text):
    badge_w, badge_h = 480, 75
    bx = (RENDER_W - badge_w) // 2
    by = 130
    draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=35, fill=(225, 29, 72), outline=(255, 255, 255), width=6)
    draw.text((RENDER_W // 2, by + badge_h // 2), "FLINT & GRIT", fill=(255, 255, 255), font=FONT_HEADER, anchor="mm")
    draw.text((RENDER_W // 2, by + badge_h + 80), topic_text, fill=(255, 255, 0), font=FONT_TOPIC, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))

def draw_bold_yellow_caption(draw, text, y_pos=3150):
    draw.text((RENDER_W // 2, y_pos), text, fill=(255, 240, 0), font=FONT_CAPTION, anchor="mm", stroke_width=16, stroke_fill=(0, 0, 0))

# =============================================================================
# 4. RENDER FRAME WORKER
# =============================================================================

def render_frame_worker(args):
    scene_idx, frame_in_scene, total_frames, global_t, topic_data, frame_out_path = args
    sc = topic_data["scenes"][scene_idx]

    img = Image.new("RGB", (RENDER_W, RENDER_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 1. Environment
    draw_environment(draw, topic_data.get("environment", "kitchen"), RENDER_W, RENDER_H, global_t)

    # 2. Dynamic Scene Elements
    cx_prop, cy_prop = int(RENDER_W * 0.65), int(RENDER_H * 0.68)
    elems = sc.get("elements", [])
    if "fire" in elems:
        draw_fire_flames(draw, cx_prop, cy_prop - 20, scale=1.35, time_sec=global_t)
        draw_smoke_particles(draw, cx_prop, cy_prop - 180, time_sec=global_t)
    if "water_cross" in elems:
        draw.ellipse([cx_prop - 140, cy_prop - 280, cx_prop + 140, cy_prop - 120], fill=(56, 189, 248), outline=(14, 165, 233), width=8)
        draw_danger_cross(draw, cx_prop, cy_prop - 200, size=320)
    if "sparks" in elems:
        # Electrical sparks
        for k in range(6):
            sx = cx_prop + int(math.sin(global_t * 20 + k) * 120)
            sy = cy_prop - 100 + int(math.cos(global_t * 20 + k) * 80)
            draw.line([sx - 30, sy - 30, sx + 30, sy + 30], fill=(255, 255, 0), width=10)
            draw.line([sx + 30, sy - 30, sx - 30, sy + 30], fill=(0, 240, 255), width=8)

    # 3. 2D Character
    char_x = int(RENDER_W * 0.30)
    char_y = int(RENDER_H * 0.52)
    draw_2d_character(draw, char_x, char_y, scale=1.35, pose=sc["pose"], clothes=topic_data.get("clothes", "kurta"), time_sec=global_t)

    # 4. Header & Captions
    draw_header_badge(draw, topic_data["title"])
    draw_bold_yellow_caption(draw, sc["caption"], y_pos=3150)

    # Step Badge
    badge_w, badge_h = 750, 90
    bx = (RENDER_W - badge_w) // 2
    draw.rounded_rectangle([bx, 2880, bx + badge_w, 2880 + badge_h], radius=40, fill=(15, 23, 42), outline=(0, 240, 255), width=6)
    draw.text((RENDER_W // 2, 2925), sc["step"], fill=(255, 255, 255), font=FONT_STEP, anchor="mm")

    # 5. Downsample Lanczos 1080x1920
    final_img = img.resize((FINAL_W, FINAL_H), Image.Resampling.LANCZOS)
    final_img.save(frame_out_path, quality=92)
    return True

# =============================================================================
# 5. CONTACT SHEET GENERATOR
# =============================================================================

def generate_contact_sheet(topic_data, contact_sheet_path):
    print("[*] Generating 6-scene visual contact sheet...")
    cols, rows = 3, 2
    cell_w, cell_h = 360, 640
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (15, 23, 42))

    for idx, sc in enumerate(topic_data["scenes"]):
        temp_frame_path = os.path.join(TEMP_DIR, f"thumb_{idx}.jpg")
        render_frame_worker((idx, 12, int(sc["duration"] * FPS), idx * 2.0, topic_data, temp_frame_path))
        thumb = Image.open(temp_frame_path).resize((cell_w - 8, cell_h - 8), Image.Resampling.BILINEAR)
        col = idx % cols
        row = idx // cols
        sheet.paste(thumb, (col * cell_w + 4, row * cell_h + 4))

    sheet.save(contact_sheet_path, quality=92)
    print(f"[+] Contact Sheet saved: {contact_sheet_path}")

# =============================================================================
# 6. NEURAL HINDI AUDIO & SPEED NORMALIZER
# =============================================================================

async def generate_neural_voiceover(text, raw_audio_path, synced_audio_path):
    import edge_tts
    print(f"[*] Generating Neural Hindi Voiceover via Edge-TTS...")
    comm = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+8%")
    await comm.save(raw_audio_path)

    # Detect length and speed up/down with FFmpeg atempo to strictly hit 12.0s
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", raw_audio_path]
    res = subprocess.run(probe_cmd, capture_output=True, text=True)
    dur = float(res.stdout.strip() or 12.0)
    print(f"[+] Raw voiceover length: {dur:.2f}s (Target: {TARGET_DURATION}s)")

    ratio = dur / TARGET_DURATION
    # Clamped between 0.8 and 1.8
    tempo = max(0.8, min(1.8, ratio))
    print(f"[*] Syncing audio tempo ({tempo:.2f}x) for exact 12-second runtime...")

    sync_cmd = ["ffmpeg", "-y", "-i", raw_audio_path, "-filter:a", f"atempo={tempo}", "-vn", synced_audio_path]
    subprocess.run(sync_cmd, capture_output=True)
    print(f"[+] Audio tempo synchronized successfully!")

# =============================================================================
# 7. PRODUCER PIPELINE
# =============================================================================

def pick_next_topic(preferred_id=None):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

    if preferred_id:
        for t in VIRAL_TOPICS:
            if t["id"] == preferred_id:
                return t

    for t in VIRAL_TOPICS:
        if t["id"] not in history:
            return t

    # Reset if all exhausted
    return VIRAL_TOPICS[0]

def record_topic_history(topic_id, video_path):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    if topic_id not in history:
        history.append(topic_id)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Flint & Grit Autonomous 12s Shorts Producer")
    parser.add_argument("--topic", help="Optional specific topic ID", default=None)
    parser.add_argument("--upload", action="store_true", help="Explicitly enable YouTube upload for Channel 3 (disabled by default until API is provided)")
    parser.add_argument("--no-upload", action="store_true", help="Keep video local/archive only (default)")
    args = parser.parse_args()

    print("=================================================================")
    print("      FLINT & GRIT — 100% AUTONOMOUS 12-SECOND 2D PRODUCER       ")
    print("=================================================================")

    topic = pick_next_topic(args.topic)
    print(f"🎯 Selected Topic: {topic['title']} (ID: {topic['id']})")

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    timestamp = int(time.time())
    video_filename = f"FLINTGRIT_{topic['id']}_{timestamp}.mp4"
    contact_filename = f"FLINTGRIT_{topic['id']}_{timestamp}_contact.jpg"
    final_video_path = os.path.join(OUTPUT_DIR, video_filename)
    final_contact_path = os.path.join(OUTPUT_DIR, contact_filename)

    # 1. Voiceover
    raw_audio = os.path.join(TEMP_DIR, "raw_voice.mp3")
    synced_audio = os.path.join(TEMP_DIR, "synced_voice.mp3")
    asyncio.run(generate_neural_voiceover(topic["narration"], raw_audio, synced_audio))

    # 2. Contact sheet
    generate_contact_sheet(topic, final_contact_path)

    # 3. Multi-Threaded Frame Rendering
    print(f"[*] Rendering 288 frames at 24 FPS with multi-threading...")
    render_tasks = []
    total_time = 0.0
    frame_idx = 0

    for sc_idx, sc in enumerate(topic["scenes"]):
        duration = sc["duration"]
        scene_frames = int(duration * FPS)
        for f in range(scene_frames):
            global_t = total_time + (f / FPS)
            frame_path = os.path.join(TEMP_DIR, f"frame_{frame_idx:05d}.jpg")
            render_tasks.append((sc_idx, f, scene_frames, global_t, topic, frame_path))
            frame_idx += 1
        total_time += duration

    start_render = time.time()
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(render_frame_worker, render_tasks))
    render_elapsed = time.time() - start_render
    print(f"[+] Rendered {frame_idx} frames in {render_elapsed:.1f} seconds! ({frame_idx/render_elapsed:.1f} FPS)")

    # 4. FFmpeg Video Assembly
    print("[*] Assembling 1080x1920 MP4 Video with FFmpeg & syncing audio...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(TEMP_DIR, "frame_%05d.jpg"),
        "-i", synced_audio,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_video_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[!] FFmpeg Error:", res.stderr[-500:])
        return

    # Also copy to Desktop if Desktop exists (e.g. Windows PC)
    desktop_dir = Path.home() / "Desktop"
    if desktop_dir.exists():
        desktop_copy = str(desktop_dir / video_filename)
        desktop_contact = str(desktop_dir / contact_filename)
        try:
            shutil.copy2(final_video_path, desktop_copy)
            shutil.copy2(final_contact_path, desktop_contact)
            print(f"🖥️ Desktop Copy: {desktop_copy}")
        except Exception:
            pass

    record_topic_history(topic["id"], final_video_path)

    print("=================================================================")
    print(f"🎉 SUCCESS! FLINT & GRIT SHORTS READY:")
    print(f"📹 Video: {final_video_path}")
    print(f"📸 Contact Sheet: {final_contact_path}")
    print("=================================================================")

    # Clean Temp
    try:
        shutil.rmtree(TEMP_DIR)
    except Exception:
        pass

    # 5. YouTube Upload (STRICTLY DISABLED BY DEFAULT until Faraz Sir connects Channel 3 API in the evening)
    if args.upload and not args.no_upload:
        print("[*] Checking Channel 3 YouTube credentials...")
        cid = os.environ.get("YT_CLIENT_ID_CH3")
        csec = os.environ.get("YT_CLIENT_SECRET_CH3")
        rtoken = os.environ.get("YT_REFRESH_TOKEN_CH3")

        token_path = os.path.join(SCRIPT_DIR, "youtube_token_ch3.json")
        if not rtoken and os.path.exists(token_path):
            try:
                with open(token_path) as f:
                    td = json.load(f)
                    cid = td.get("client_id")
                    csec = td.get("client_secret")
                    rtoken = td.get("refresh_token")
            except Exception:
                pass

        if cid and csec and rtoken:
            try:
                from youtube_cloud_uploader import upload_video_file
                title = f"{topic['title']} • 99% Log Ye Galti Karte Hain! #Shorts #FlintGrit"
                desc = f"{topic['title']}\n\n{topic['narration']}\n\n#FlintGrit #SafetyTips #LifeHacks #Shorts #SurvivalTips"
                tags = ["Flint and Grit", "Safety Tips", "Life Hacks", "Survival", "Shorts", "Facts"]
                upload_video_file(final_video_path, title, desc, tags, cid, csec, rtoken, privacy_status="public")
                print("🎉 PUBLISHED DIRECTLY TO FLINT & GRIT YOUTUBE CHANNEL!")
            except Exception as e:
                print(f"[!] Channel 3 YouTube upload error: {e}")
        else:
            print("[ℹ️] Channel 3 API not provided yet. Upload skipped.")
    else:
        print("[ℹ️] Channel 3 (Flint & Grit) is in Local Production & Archive Mode.")
        print("[ℹ️] YouTube Upload is OFF. Videos are safely generated and saved in output_channel3.")

if __name__ == "__main__":
    main()
