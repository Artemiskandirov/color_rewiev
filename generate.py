#!/usr/bin/env python3
"""V5 - Core names, Other group, Unmatched block, ALL colors verified."""

import math, json as _json
from collections import defaultdict, OrderedDict

# ============================================================
# COLOR MATH
# ============================================================
def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 8: h = h[2:]
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r,g,b): return f"#{max(0,min(255,r)):02X}{max(0,min(255,g)):02X}{max(0,min(255,b)):02X}"

def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c):
    c = max(0, min(1, c))
    return int((12.92 * c if c <= 0.0031308 else 1.055 * c**(1/2.4) - 0.055) * 255 + 0.5)

def rgb_to_xyz(r, g, b):
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    return (rl*0.4124564+gl*0.3575761+bl*0.1804375, rl*0.2126729+gl*0.7151522+bl*0.0721750, rl*0.0193339+gl*0.1191920+bl*0.9503041)

def xyz_to_lab(x, y, z):
    xn, yn, zn = 0.95047, 1.0, 1.08883
    def f(t): return t**(1/3) if t > 0.008856 else 7.787*t+16/116
    fx, fy, fz = f(x/xn), f(y/yn), f(z/zn)
    return 116*fy-16, 500*(fx-fy), 200*(fy-fz)

def rgb_to_lab(r, g, b): return xyz_to_lab(*rgb_to_xyz(r, g, b))

def delta_e_2000(lab1, lab2):
    L1,a1,b1=lab1; L2,a2,b2=lab2
    avg_L=(L1+L2)/2; C1=math.sqrt(a1**2+b1**2); C2=math.sqrt(a2**2+b2**2); avg_C=(C1+C2)/2
    avg_C7=avg_C**7; G=0.5*(1-math.sqrt(avg_C7/(avg_C7+25**7)))
    a1p=a1*(1+G); a2p=a2*(1+G); C1p=math.sqrt(a1p**2+b1**2); C2p=math.sqrt(a2p**2+b2**2); avg_Cp=(C1p+C2p)/2
    h1p=math.degrees(math.atan2(b1,a1p))%360; h2p=math.degrees(math.atan2(b2,a2p))%360
    if abs(h1p-h2p)<=180: avg_Hp=(h1p+h2p)/2
    elif h1p+h2p<360: avg_Hp=(h1p+h2p+360)/2
    else: avg_Hp=(h1p+h2p-360)/2
    T=1-0.17*math.cos(math.radians(avg_Hp-30))+0.24*math.cos(math.radians(2*avg_Hp))+0.32*math.cos(math.radians(3*avg_Hp+6))-0.20*math.cos(math.radians(4*avg_Hp-63))
    if abs(h2p-h1p)<=180: dhp=h2p-h1p
    elif h2p-h1p>180: dhp=h2p-h1p-360
    else: dhp=h2p-h1p+360
    dLp=L2-L1; dCp=C2p-C1p; dHp=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dhp/2))
    SL=1+0.015*(avg_L-50)**2/math.sqrt(20+(avg_L-50)**2); SC=1+0.045*avg_Cp; SH=1+0.015*avg_Cp*T
    dTheta=30*math.exp(-((avg_Hp-275)/25)**2); avg_Cp7=avg_Cp**7; RC=2*math.sqrt(avg_Cp7/(avg_Cp7+25**7)); RT=-RC*math.sin(math.radians(2*dTheta))
    return math.sqrt((dLp/SL)**2+(dCp/SC)**2+(dHp/SH)**2+RT*(dCp/SC)*(dHp/SH))

def de(h1, h2): return delta_e_2000(rgb_to_lab(*hex_to_rgb(h1)), rgb_to_lab(*hex_to_rgb(h2)))

def blend_on_white(hex_color, alpha):
    """Simple sRGB alpha compositing on white: result = base*alpha + 255*(1-alpha).
    This matches Figma / CSS behavior exactly."""
    r,g,b = hex_to_rgb(hex_color)
    ro = round(r * alpha + 255 * (1 - alpha))
    go = round(g * alpha + 255 * (1 - alpha))
    bo = round(b * alpha + 255 * (1 - alpha))
    return rgb_to_hex(ro, go, bo)

def generate_scale(base_hex):
    """Generate 100→10 scale: each step = base at that % opacity on white."""
    return {s: blend_on_white(base_hex, s/100.0) for s in STEPS}

def text_color(hex_c):
    r,g,b = hex_to_rgb(hex_c)
    return "#fff" if (0.299*r+0.587*g+0.114*b)<160 else "rgba(0,0,0,.55)"

STEPS = [100, 80, 60, 40, 20, 10]

# ============================================================
# ALL LEGACY COLORS - every single one from user's message
# (name, hex, note)
# ============================================================
# I mark each with a source comment so nothing is missed.

LEGACY = [
    # ===== NAMED LIST: BLUES =====
    ("active_teacher_blue_80", "#0D99F6", "80% alpha"),
    ("celestial_blue", "#0D99F6", ""),
    ("dodger_blue", "#3B73F4", ""),
    ("main_skyborn", "#378CED", ""),
    ("main_deep_marine", "#1368C9", ""),
    ("payment_blue_sky", "#003082", ""),
    ("payment_ultramarine", "#070688", "опечатка #07068"),
    ("main_federalio_blue", "#020159", ""),
    ("payment_federalio_blue", "#020159", "дубл. main_federalio_blue"),
    ("main_oxford_blue", "#021D49", ""),
    ("authentication_argentinian_blue_10", "#3AAFFF", "10% alpha"),
    ("librarium_light_blue", "#C4E7FF", ""),
    ("webinar_blue_light", "#ECF7FE", ""),

    # ===== NAMED LIST: PURPLES =====
    ("active_teacher_notification_deep_purple", "#8E75FF", ""),
    ("booster_palantine_blue", "#5137C7", ""),
    ("main_palantine_blue", "#5137C7", "дубл. booster"),
    ("email_consent_palatinate_blue", "#583CF5", ""),
    ("main_palatinate_blue", "#583CF5", "дубл. email_consent"),
    ("diamond_store_purple_primary", "#634AD6", ""),
    ("majorelle_blue", "#634AD6", ""),
    ("majorelle_blue_10_alpha", "#634AD6", "10% alpha"),
    ("majorelle_blue_20_alpha", "#634AD6", "20% alpha"),
    ("majorelle_blue_50_alpha", "#634AD6", "50% alpha"),
    ("diamond_store_persian_indigo", "#221073", ""),
    ("diamond_store_zaffre", "#331D98", ""),
    ("grape_deep", "#34006B", ""),
    ("main_grape", "#6937C7", ""),
    ("parent_electric_purple", "#6C2AC8", ""),
    ("quest_base_purple", "#6750F0", ""),
    ("state_blue", "#765FDE", ""),
    ("subject_statistics_purplish_blue", "#5842E2", ""),
    ("purple", "#B1A6FF", ""),
    ("homework_light_purple", "#E9E4FF", ""),
    ("payment_medium_slate_blue", "#9859FF", ""),
    ("player_classic_cosmic_tide", "#6D0BDE", ""),

    # ===== NAMED LIST: REDS/PINKS =====
    ("chili_red", "#EA3117", ""),
    ("chili_red_20", "#EA3117", "20% alpha"),
    ("main_off_red", "#F81B01", ""),
    ("active_teacher_coral", "#FF6170", ""),
    ("bright_pink", "#FF6170", ""),
    ("math_task_red_pink", "#EF5968", ""),
    ("hero_path_bittersweet", "#FC6E5C", ""),
    ("parent_paywall_persian_red", "#CA3B3B", ""),
    ("diamond_store_purple_pizzazz", "#FF4AE8", "маджента"),
    ("road_safety_membership_rose_light", "#FFCCD5", ""),
    ("webinar_strawberry_light", "#FFE3E3", ""),

    # ===== NAMED LIST: ORANGES/YELLOWS =====
    ("bright_orange", "#FF8811", ""),
    ("authentication_ut_orange_10", "#FF8811", "10% alpha"),
    ("orange", "#FF965A", ""),
    ("orange_paywall", "#FF965A", "дубл."),
    ("main_harvest_gold", "#EBA41B", ""),
    ("hero_path_selective_yellow", "#FFB800", ""),
    ("mikado", "#FFC500", ""),
    ("sun", "#FEC700", ""),
    ("lemonade", "#FFCC00", ""),
    ("bundle_promotion_sunglow", "#FFD335", ""),
    ("parent_paywall_sunglow", "#FFD335", "дубл."),
    ("blond", "#FFEDBF", ""),
    ("olympiad_sun_light", "#FFECA6", ""),

    # ===== NAMED LIST: GREENS =====
    ("diamond_store_lime_green", "#5FD34C", ""),
    ("lime_green", "#5FD34C", ""),
    ("green_paywall", "#029E79", ""),
    ("math_task_leafy_green", "#5ABD63", ""),
    ("librarium_medium_green", "#87E3A7", ""),
    ("librarium_light_green", "#B7EECA", ""),
    ("snowy_mint", "#CAFFDF", ""),
    ("classes_mint", "#B3E8E5", ""),
    ("librarium_light_mint", "#B3E8E5", "дубл. classes_mint"),
    ("subject_statistics_aqua_cyan", "#BCECE8", ""),
    ("robin_egg_blue", "#4CC9C2", ""),

    # ===== NAMED LIST: NEUTRALS =====
    ("black", "#000000", ""),
    ("black_60", "#000000", "60% alpha"),
    ("black_9", "#000000", "9% alpha"),
    ("rich_black", "#0C1821", ""),
    ("space_cadet", "#2F2F45", ""),
    ("yankees_blue", "#1D1D42", ""),
    ("onboarding_space_mandet", "#1D1D42", "дубл. yankees_blue"),
    ("bastard_grey", "#ACACB5", ""),
    ("librarium_iron_grey", "#555E65", ""),
    ("grey3", "#EEEEF1", ""),
    ("white", "#FFFFFF", ""),
    ("antiflash_white", "#F2F3F7", ""),
    ("payment_grey", "#F7F8FA", ""),

    # ===== SECOND LIST: Celestial Blue group =====
    ("_0D99F6", "#0D99F6", "алиас celestial_blue"),
    ("_0D99F6_80", "#0D99F6", "80% alpha"),
    ("badge_24pct", "#0D99F6", "24% alpha"),
    ("upperBackground_12pct", "#0D99F6", "12% alpha"),
    ("infoCell_8pct", "#0D99F6", "8% alpha"),
    ("_7FC3FB", "#7FC3FB", ""),
    ("_ECF7FE", "#ECF7FE", "дубл. webinar_blue_light"),
    ("_C4E7FF", "#C4E7FF", "дубл. librarium_light_blue"),

    # ===== SECOND LIST: Purples group =====
    ("_5842E2", "#5842E2", "дубл. subject_statistics"),
    ("feedback_violet", "#6935D7", ""),
    ("lottery_blue", "#5434E8", ""),
    ("_8E75FF", "#8E75FF", "дубл. deep_purple"),
    ("_E9E4FF", "#E9E4FF", "дубл. homework_light_purple"),
    ("violet_base", "#EAE6FF", ""),
    ("_E9E6FF", "#E9E6FF", ""),
    ("_746AA3", "#746AA3", "алиас ultra_violet"),
    ("scorelabel_background_8pct", "#746AA3", "8% alpha"),
    ("deep_purple_blue", "#0F0636", ""),

    # ===== SECOND LIST: Reds =====
    ("coral100", "#FF6170", "дубл. bright_pink"),
    ("_FF6170", "#FF6170", "дубл."),
    ("_FF506F", "#FF506F", ""),

    # ===== SECOND LIST: Orange/Yellow =====
    ("_FF965A", "#FF965A", "дубл."),
    ("_FF8811", "#FF8811", "дубл."),
    ("_FDE59E", "#FDE59E", ""),

    # ===== SECOND LIST: Greens =====
    ("_B3E8E5", "#B3E8E5", "дубл."),
    ("_1CC67F", "#1CC67F", ""),
    ("_BCECE8", "#BCECE8", "дубл."),
    ("_87E3A7", "#87E3A7", "дубл."),
    ("_B7EECA", "#B7EECA", "дубл."),
    ("_C0FDFF", "#C0FDFF", ""),
    ("_00B2A8", "#00B2A8", ""),
    ("_5FD34C", "#5FD34C", "дубл."),
    ("_20B47E", "#20B47E", ""),
    ("green_light_9pct", "#20B47E", "9% alpha"),

    # ===== SECOND LIST: Neutrals =====
    ("_091526", "#091526", "divider"),
    ("_091526_40pct", "#091526", "40% alpha"),
    ("_394E7F", "#394E7F", "selected"),
    ("_394E7F_shadow_10pct", "#394E7F", "10% alpha"),
    ("_394E7F_selected_4pct", "#394E7F", "4% alpha"),
    ("_2F2F45", "#2F2F45", "дубл. space_cadet"),
    ("_2F2F45_skeleton_15pct", "#2F2F45", "15% alpha"),
    ("_2F2F45_skeleton_8pct", "#2F2F45", "8% alpha"),
    ("white80", "#FFFFFF", "80% alpha"),
    ("white60", "#FFFFFF", "60% alpha"),
    ("white20", "#FFFFFF", "20% alpha"),
    ("_8E8E93", "#8E8E93", ""),
    ("_D5D5DA", "#D5D5DA", ""),
    ("_ECECEC", "#ECECEC", ""),
    ("_F8F8F8", "#F8F8F8", ""),
    ("_EEEEF1", "#EEEEF1", "дубл. grey3"),
    ("_F1F1F1", "#F1F1F1", ""),
    ("_E2E2E2", "#E2E2E2", ""),
    ("_555E65", "#555E65", "дубл. iron_grey"),

    # ===== THIRD LIST: unnamed hexes =====
    ("_F5F6F7", "#F5F6F7", ""),
    ("_6B58E4", "#6B58E4", ""),
    ("_E7FAED", "#E7FAED", ""),
    ("_7958A0", "#7958A0", ""),
    ("_029E79", "#029E79", "дубл. green_paywall"),
    ("_A0587F", "#A0587F", ""),
    ("_030B35", "#030B35", ""),
    ("_FAF7FB", "#FAF7FB", ""),
    ("_765FDE", "#765FDE", "дубл. state_blue"),
    ("_E7E7FF", "#E7E7FF", ""),
    ("_E5F7F6", "#E5F7F6", ""),
    ("_80D9D3", "#80D9D3", ""),
    ("_501C85", "#501C85", ""),
    ("_9F8FE8", "#9F8FE8", ""),
    ("_FFB800", "#FFB800", "дубл."),
    ("_F4E2B3", "#F4E2B3", ""),
    ("_5ABD63", "#5ABD63", "дубл. leafy_green"),
    ("_EF5968", "#EF5968", "дубл. math_task_red_pink"),
    ("_FFF3EC", "#FFF3EC", "дубл. pearl"),
    ("_453A98", "#453A98", ""),
    ("_9859FF", "#9859FF", "дубл."),
    ("_212645", "#212645", ""),
    ("_EA3117", "#EA3117", "дубл. chili_red"),
    ("_2F2F45_unnamed", "#2F2F45", "дубл."),
    ("_E5F3FD", "#E5F3FD", ""),
    ("_F2F3F7", "#F2F3F7", "дубл. antiflash"),
    ("_87D34C", "#87D34C", ""),
    ("_E1CAFF", "#E1CAFF", ""),
    ("_602EB2", "#602EB2", ""),
    ("_975CF8", "#975CF8", ""),
    ("_F1EEFF", "#F1EEFF", ""),
    ("_ACACB5", "#ACACB5", "дубл. bastard_grey"),
    ("_ECF7FE", "#ECF7FE", "дубл."),
    ("_F7F8FA", "#F7F8FA", "дубл. payment_grey"),
    ("_EBA41B", "#EBA41B", "дубл."),
    ("_1D1D42", "#1D1D42", "дубл. yankees_blue"),
    ("_2F2F59", "#2F2F59", ""),
    ("_021D49", "#021D49", "дубл. main_oxford_blue"),
    ("_FC6E5C", "#FC6E5C", "дубл. bittersweet"),
    ("_FFE8E5", "#FFE8E5", ""),
    ("_B07664", "#B07664", ""),
    ("_C06D63", "#C06D63", ""),
    ("_8A4646", "#8A4646", ""),
    ("_289FDC", "#289FDC", ""),
    ("_003082", "#003082", "дубл. payment_blue_sky"),
    ("_6750F0", "#6750F0", "дубл. quest_base_purple"),
    ("_3B73F4", "#3B73F4", "дубл. dodger_blue"),
    ("_378CED", "#378CED", "дубл. main_skyborn"),
    ("_1368C9", "#1368C9", "дубл. main_deep_marine"),
    ("_5137C7", "#5137C7", "дубл. booster"),
    ("_6937C7", "#6937C7", "дубл. main_grape"),
    ("_1F1B3C", "#1F1B3C", ""),
    ("_331D98", "#331D98", "дубл. zaffre"),
    ("_221073", "#221073", "дубл. persian_indigo"),
    ("_FFC500", "#FFC500", "дубл. mikado"),
    ("_352480", "#352480", ""),
    ("_FF4AE8", "#FF4AE8", "дубл. purple_pizzazz"),
    ("_6C2AC8", "#6C2AC8", "дубл. electric_purple"),
    ("_5513DA", "#5513DA", ""),
    ("_CA3B3B", "#CA3B3B", "дубл. persian_red"),
    ("_1D2B42", "#1D2B42", ""),
    ("_F04760", "#F04760", ""),
    ("_410ABB", "#410ABB", ""),
    ("_261168", "#261168", ""),
    ("_01A743", "#01A743", ""),
    ("_4F4FDB", "#4F4FDB", ""),
    ("_3D3D8B", "#3D3D8B", ""),
    ("_FFCCD5", "#FFCCD5", "дубл. rose_light"),
    ("_FFCC00", "#FFCC00", "дубл. lemonade"),
    ("_240F87", "#240F87", ""),
    ("_160F7F", "#160F7F", ""),
    ("_E4DEFF", "#E4DEFF", ""),
    ("_020159", "#020159", "дубл. federalio_blue"),
    ("_F81B01", "#F81B01", "дубл. main_off_red"),
    ("_34006B", "#34006B", "дубл. grape_deep"),
    ("_6D0BDE", "#6D0BDE", "дубл. cosmic_tide"),
    ("_322876", "#322876", ""),
    ("_F2F0FF", "#F2F0FF", ""),
    ("_F8F6FF", "#F8F6FF", ""),
    ("_2C2A49", "#2C2A49", ""),
    ("_CAFFDF", "#CAFFDF", "дубл. snowy_mint"),
    ("_FFE3E3", "#FFE3E3", "дубл. strawberry_light"),
    ("_FFD335", "#FFD335", "дубл. sunglow"),
    ("_FFECA6", "#FFECA6", "дубл. olympiad_sun"),
]

TOTAL_INPUT = len(LEGACY)
print(f"Всего цветов во входных данных: {TOTAL_INPUT}")

# ============================================================
# FAMILIES (names from Core tokens)
# ============================================================

# Families WITH 100→10 scale
SCALE_FAMILIES = OrderedDict([
    ("celestial_blue", {
        "desc": "Голубая шкала (Cross Blue + Core celestial_blue)",
        "base_100": "#0D99F6",
        "existing_solid": {100: "#3AAFFF", 80: "#75C7FF", 60: "#9DD7FF", 40: "#C4E7FF", 20: "#EBF7FF"},
        "cross_name": "Blue",
        "alpha_base": "#0D99F6", "alpha_label": "celestial_blue",
        "alpha_existing": {100: 1.0, 80: 0.8, 60: 0.6, 20: 0.2, 10: 0.1},
        "refs": ["#3AAFFF","#75C7FF","#9DD7FF","#C4E7FF","#EBF7FF","#0D99F6"],
    }),
    ("majorelle_blue", {
        "desc": "Фиолетово-синяя шкала (Cross Majorelle_blue + Core majorelle_blue)",
        "base_100": "#3C20BA",
        "existing_solid": {100: "#3C20BA", 80: "#5137C7", 60: "#634AD6", 40: "#9D8BF1", 20: "#E8E4FF", 10: "#F1EEFF"},
        "cross_name": "Majorelle_blue",
        "alpha_base": "#634AD6", "alpha_label": "majorelle_blue",
        "alpha_existing": {100: 1.0, 10: 0.1},
        "refs": ["#3C20BA","#5137C7","#634AD6","#9D8BF1","#E8E4FF","#F1EEFF"],
    }),
    ("ultra_violet", {
        "desc": "Ультрафиолетовый (Core ultra_violet)",
        "base_100": "#746AA3",
        "existing_solid": {},
        "alpha_base": "#746AA3", "alpha_label": "ultra_violet",
        "alpha_existing": {100: 1.0, 50: 0.5, 20: 0.2, 8: 0.08},
        "refs": ["#746AA3"],
    }),
    ("bright_pink", {
        "desc": "Коралловая/розовая шкала (Cross Brand_coral + Core bright_pink)",
        "base_100": "#FF6170",
        "existing_solid": {100: "#FF6170", 80: "#FF909B", 60: "#FFB0B8", 40: "#FFD0D4", 20: "#FFEFF1"},
        "cross_name": "Brand_coral",
        "alpha_base": "#FF6170", "alpha_label": "bright_pink",
        "alpha_existing": {100: 1.0, 40: 0.4, 20: 0.2},
        "refs": ["#FF6170","#FF909B","#FFB0B8","#FFD0D4","#FFEFF1"],
    }),
    ("chili_red", {
        "desc": "Красная шкала (Cross Red + Core chili_red)",
        "base_100": "#EA3117",
        "existing_solid": {},
        "cross_name": "Red",
        "alpha_base": "#EA3117", "alpha_label": "chili_red",
        "alpha_existing": {100: 1.0, 7: 0.07},
        "extra_tokens": {"Red/Base": "#EA3117", "Red/Hover": "#D5260E", "Red/Active": "#BB210C"},
        "extra_tokens_reason": "Состояния кнопок (Base/Hover/Active) — не являются частью шкалы прозрачности, а обозначают интерактивные состояния.",
        "refs": ["#EA3117","#D5260E","#BB210C"],
    }),
    ("lime_green", {
        "desc": "Лаймово-зелёная (Core lime_green)",
        "base_100": "#5FD34C",
        "existing_solid": {},
        "alpha_base": "#5FD34C", "alpha_label": "lime_green",
        "alpha_existing": {100: 1.0, 80: 0.8, 60: 0.6, 40: 0.4, 10: 0.1},
        "refs": ["#5FD34C"],
    }),
    ("robin_egg_blue", {
        "desc": "Мятная шкала (Cross Mint + Core robin_egg_blue)",
        "base_100": "#00B2A8",
        "existing_solid": {100: "#00B2A8", 80: "#4CC9C2", 60: "#80D9D3", 40: "#B3E8E5", 20: "#E5F7F6"},
        "cross_name": "Mint",
        "alpha_base": "#4CC9C2", "alpha_label": "robin_egg_blue",
        "alpha_existing": {100: 1.0, 15: 0.15},
        "refs": ["#00B2A8","#4CC9C2","#80D9D3","#B3E8E5","#E5F7F6"],
    }),
    ("green", {
        "desc": "Зелёная шкала (Cross Green)",
        "base_100": "#10C84E",
        "existing_solid": {100: "#10C84E", 80: "#58D883", 60: "#87E3A7", 40: "#B7EECA", 20: "#E7FAED"},
        "cross_name": "Green",
        "alpha_base": "#10C84E", "alpha_label": "green",
        "alpha_existing": {100: 1.0},
        "refs": ["#10C84E","#58D883","#87E3A7","#B7EECA","#E7FAED"],
    }),
    ("yellow", {
        "desc": "Жёлтая шкала (Cross Yellow + Core lemonade)",
        "base_100": "#FBCC3C",
        "existing_solid": {100: "#FBCC3C", 80: "#FCDB76", 60: "#FDE59E", 40: "#FEF0C5", 20: "#FFFAEB"},
        "cross_name": "Yellow",
        "alpha_base": "#FBCC3C", "alpha_label": "yellow",
        "alpha_existing": {100: 1.0},
        "extra_tokens": {"lemonade": "#FFCC00"},
        "extra_tokens_reason": "Отдельный Core-токен lemonade (#FFCC00) — близкий к Yellow 100, но с другим оттенком; хранится как самостоятельное значение.",
        "refs": ["#FBCC3C","#FCDB76","#FDE59E","#FEF0C5","#FFFAEB","#FFCC00"],
    }),
    ("orange_bright", {
        "desc": "Оранжевая шкала (Cross Orange + Core orange_bright + orange)",
        "base_100": "#FF8811",
        "existing_solid": {100: "#FF8811", 80: "#FFAC58", 60: "#FFC388", 40: "#FFDBB8", 20: "#FFF3E7"},
        "cross_name": "Orange",
        "alpha_base": "#FF8811", "alpha_label": "orange_bright",
        "alpha_existing": {100: 1.0, 10: 0.1},
        "extra_tokens": {"orange": "#FF965A"},
        "extra_tokens_reason": "Core-токен orange (#FF965A) — отличается от orange_bright (#FF8811) по оттенку; не укладывается в шкалу прозрачности.",
        "refs": ["#FF8811","#FFAC58","#FFC388","#FFDBB8","#FFF3E7","#FF965A"],
    }),
    ("deep_purple", {
        "desc": "Глубокий фиолетовый (Core deep_purple + purple + state_blue)",
        "base_100": "#8E75FF",
        "existing_solid": {},
        "alpha_base": "#8E75FF", "alpha_label": "deep_purple",
        "alpha_existing": {100: 1.0},
        "extra_tokens": {"deep_purple": "#8E75FF", "purple": "#B1A6FF", "state_blue": "#765FDE"},
        "extra_tokens_reason": "Три отдельных Core-токена с разной насыщенностью; не формируют единую линейную шкалу, поэтому хранятся как самостоятельные значения.",
        "refs": ["#8E75FF","#B1A6FF","#765FDE"],
    }),
    ("space_cadet", {
        "desc": "Сине-серый тёмный (Core + Cross space_cadet)",
        "base_100": "#2F2F45",
        "existing_solid": {},
        "alpha_base": "#2F2F45", "alpha_label": "space_cadet",
        "alpha_existing": {100: 1.0, 80: 0.8, 65: 0.65, 60: 0.6, 40: 0.4, 25: 0.25, 20: 0.2, 10: 0.1, 9: 0.09, 4: 0.04},
        "refs": ["#2F2F45"],
    }),
    ("white", {
        "desc": "Белый (Core + Cross white)",
        "base_100": "#FFFFFF",
        "existing_solid": {},
        "alpha_base": "#FFFFFF", "alpha_label": "white",
        "alpha_existing": {100: 1.0, 85: 0.85, 80: 0.8, 75: 0.75, 60: 0.6, 40: 0.4, 20: 0.2, 9: 0.09},
        "skip_solid_scale": True,
        "refs": ["#FFFFFF"],
    }),
    ("black", {
        "desc": "Чёрный (Core black)",
        "base_100": "#000000",
        "existing_solid": {},
        "alpha_base": "#000000", "alpha_label": "black",
        "alpha_existing": {100: 1.0, 60: 0.6, 15: 0.15},
        "refs": ["#000000"],
    }),
    ("rich_black", {
        "desc": "Насыщенный чёрный (Core rich_black)",
        "base_100": "#0C1821",
        "existing_solid": {},
        "alpha_base": "#0C1821", "alpha_label": "rich_black",
        "alpha_existing": {100: 1.0, 95: 0.95},
        "refs": ["#0C1821"],
    }),
    # ===== NEW FAMILIES (created from legacy) =====
    ("dark_navy", {
        "desc": "НОВОЕ: Тёмно-синий / navy",
        "base_100": "#020159",
        "existing_solid": {},
        "is_new": True,
        "alpha_base": "#020159", "alpha_label": "dark_navy",
        "alpha_existing": {100: 1.0},
        "refs": ["#020159","#021D49","#003082"],
    }),
    ("dark_indigo", {
        "desc": "НОВОЕ: Тёмный индиго / фиолетовый",
        "base_100": "#221073",
        "existing_solid": {},
        "is_new": True,
        "alpha_base": "#221073", "alpha_label": "dark_indigo",
        "alpha_existing": {100: 1.0},
        "refs": ["#221073","#331D98","#34006B","#0F0636"],
    }),
    ("grey_neutral", {
        "desc": "НОВОЕ: Нейтральные серые",
        "base_100": "#555E65",
        "existing_solid": {},
        "is_new": True,
        "alpha_base": "#555E65", "alpha_label": "grey_neutral",
        "alpha_existing": {100: 1.0},
        "refs": ["#ACACB5","#555E65","#8E8E93","#D5D5DA"],
    }),
    ("magenta", {
        "desc": "НОВОЕ: Маджента / фуксия",
        "base_100": "#FF4AE8",
        "existing_solid": {},
        "is_new": True,
        "alpha_base": "#FF4AE8", "alpha_label": "magenta",
        "alpha_existing": {100: 1.0},
        "refs": ["#FF4AE8"],
    }),
    ("warm_brown", {
        "desc": "НОВОЕ: Тёплые коричневые / терракотовые",
        "base_100": "#8A4646",
        "existing_solid": {},
        "is_new": True,
        "alpha_base": "#8A4646", "alpha_label": "warm_brown",
        "alpha_existing": {100: 1.0},
        "refs": ["#B07664","#8A4646","#C06D63"],
    }),
])

# Other group (single Core tokens without 100→10 scale)
OTHER_TOKENS = OrderedDict([
    ("anti_flash_white", "#F2F3F7"),
    ("sugar", "#FFE6DC"),
    ("pearl", "#FFF3EC"),
    ("orange", "#FF965A"),
    ("blond", "#FFEDBF"),
    ("lemonade", "#FFCC00"),
])

# Build solid scales for all scale families
for fname, fdata in SCALE_FAMILIES.items():
    if fdata.get("skip_solid_scale"):
        continue
    existing = fdata.get("existing_solid", {})
    base = fdata["base_100"]
    proposed = generate_scale(base)
    final = {}
    for s in STEPS:
        if s in existing:
            final[s] = {"hex": existing[s], "src": "base"}
        else:
            final[s] = {"hex": proposed[s], "src": "proposed"}
    fdata["final_solid"] = final

# ============================================================
# MATCHING: assign every legacy color to a family or Other or Unmatched
# ============================================================

def find_best(hex_color):
    best_f = None; best_de = 999; best_ref = None
    # Check scale families
    for fname, fdata in SCALE_FAMILIES.items():
        for ref in fdata.get("refs", []):
            d = de(hex_color, ref)
            if d < best_de: best_de = d; best_f = ("scale", fname); best_ref = ref
    # Check Other tokens
    for tname, thex in OTHER_TOKENS.items():
        d = de(hex_color, thex)
        if d < best_de: best_de = d; best_f = ("other", tname); best_ref = thex
    return best_f, best_ref, best_de

fam_legacy = defaultdict(list)
other_legacy = defaultdict(list)
unmatched = []

for lname, lhex, lnote in LEGACY:
    is_dup = "дубл" in lnote.lower() or "алиас" in lnote.lower()
    best, ref, delta = find_best(lhex)
    entry = {"name": lname, "hex": lhex, "note": lnote, "delta": round(delta,1), "is_dup": is_dup, "ref": ref}

    if best[0] == "scale":
        fname = best[1]
        fdata = SCALE_FAMILIES[fname]
        final = fdata.get("final_solid", {})
        if final:
            best_s = None; best_d = 999
            for s in STEPS:
                d = de(lhex, final[s]["hex"])
                if d < best_d: best_d = d; best_s = s
            entry["assigned_step"] = best_s
            entry["step_de"] = round(best_d, 1)
        fam_legacy[fname].append(entry)
    else:
        other_legacy[best[1]].append(entry)

TOTAL_OUTPUT = sum(len(v) for v in fam_legacy.values()) + sum(len(v) for v in other_legacy.values())
print(f"Распределено: {TOTAL_OUTPUT} (семейства: {sum(len(v) for v in fam_legacy.values())}, other: {sum(len(v) for v in other_legacy.values())})")
assert TOTAL_OUTPUT == TOTAL_INPUT, f"ПОТЕРЯНЫ ЦВЕТА! {TOTAL_INPUT} != {TOTAL_OUTPUT}"
print("✓ Все цвета на месте!")

# ============================================================
# HTML GENERATION
# ============================================================

exact_c = sum(1 for items in fam_legacy.values() for i in items if i["delta"]<0.1) + sum(1 for items in other_legacy.values() for i in items if i["delta"]<0.1)
merged_c = sum(1 for items in fam_legacy.values() for i in items if 0.1<=i["delta"]<5) + sum(1 for items in other_legacy.values() for i in items if 0.1<=i["delta"]<5)
far_c = sum(1 for items in fam_legacy.values() for i in items if i["delta"]>=10) + sum(1 for items in other_legacy.values() for i in items if i["delta"]>=10)

CSS = """
:root{--bg:#F5F5F7;--card:#FFF;--text:#1D1D1F;--t2:#86868B;--t3:#AEAEB2;--brd:rgba(0,0,0,.06);--sh:0 1px 3px rgba(0,0,0,.04),0 4px 14px rgba(0,0,0,.06);--sh2:0 2px 8px rgba(0,0,0,.04),0 12px 40px rgba(0,0,0,.08);--r:16px;--g:#34C759;--bl:#007AFF;--o:#FF9500;--rd:#FF3B30}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue',sans-serif;background:var(--bg);color:var(--text);line-height:1.47;-webkit-font-smoothing:antialiased;padding:0}
.c{max-width:1280px;margin:0 auto;padding:0 20px}
.hdr{text-align:center;padding:40px 20px 24px}
.hdr h1{font-size:44px;font-weight:700;letter-spacing:-.03em;background:linear-gradient(135deg,#634AD6,#0D99F6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
.hdr p{font-size:17px;color:var(--t2)}

/* Delta E info block */
.de-info{background:var(--card);border-radius:var(--r);box-shadow:var(--sh);padding:28px 32px;margin-bottom:32px}
.de-info h2{font-size:20px;font-weight:700;margin-bottom:12px}
.de-info p{font-size:14px;color:var(--t2);line-height:1.6;margin-bottom:8px}
.de-info .de-scale{display:flex;gap:12px;flex-wrap:wrap;margin-top:16px}
.de-chip{display:flex;align-items:center;gap:8px;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:600}
.de-chip.exact{background:#E8FAE6;color:#1B7A12}
.de-chip.close{background:#E3F2FD;color:#0A5EB5}
.de-chip.mid{background:#FFF8E1;color:#A67C00}
.de-chip.far{background:#FDE8E7;color:#C62828}

/* TABS */
.tabs-bar{display:flex;justify-content:center;gap:0;background:var(--card);border-bottom:1px solid var(--brd);position:sticky;top:0;z-index:100;padding:0 40px}
.tabs-inner{display:flex;gap:4px;background:var(--bg);padding:4px;border-radius:12px;margin:10px 0}
.tab-btn{padding:10px 28px;font-size:14px;font-weight:600;color:var(--t2);cursor:pointer;border:none;background:transparent;border-radius:9px;transition:all .2s;white-space:nowrap}
.tab-btn:hover{color:var(--text)}
.tab-btn.active{color:var(--text);background:var(--card);box-shadow:0 1px 4px rgba(0,0,0,.08)}
.tab-pane{display:none;padding:40px 0}
.tab-pane.active{display:block}

.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:32px}
.st{background:var(--card);border-radius:var(--r);padding:22px;box-shadow:var(--sh);text-align:center;transition:transform .15s}
.st:hover{transform:translateY(-1px);box-shadow:var(--sh2)}
.st-n{font-size:36px;font-weight:700;line-height:1.1}
.st-l{font-size:11px;color:var(--t2);font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:.06em}
.section-title{font-size:28px;font-weight:700;letter-spacing:-.02em;margin:40px 0 16px}

.fam{background:var(--card);border-radius:var(--r);box-shadow:var(--sh);margin-bottom:24px;overflow:hidden;transition:box-shadow .2s}
.fam:hover{box-shadow:var(--sh2)}
.fam-top{padding:24px 28px 20px;display:flex;align-items:center;gap:12px}
.fam-strip{display:flex;gap:3px;flex-shrink:0}
.fam-strip-sw{width:8px;height:32px;border-radius:4px}
.fam-info{flex:1}
.fam-name{font-size:20px;font-weight:700;display:flex;align-items:center;gap:8px}
.fam-desc{font-size:13px;color:var(--t2);margin-top:1px}
.new-tag{background:linear-gradient(135deg,#FF3B30,#FF9500);color:#fff;padding:2px 9px;border-radius:20px;font-size:10px;font-weight:700}
.json-btn{margin-left:auto;padding:5px 12px;border:1px solid var(--brd);border-radius:8px;background:var(--card);color:var(--t2);font-size:11px;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap}
.json-btn:hover{background:var(--bg);color:var(--text);box-shadow:var(--sh)}

.sep{height:1px;background:var(--brd);margin:0 28px}
.sc{padding:20px 28px}
.sc-lbl{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--t2);margin-bottom:12px;display:flex;align-items:center;gap:8px}
.sc-row{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:8px}
.sc-col{min-width:0}
.sw-box{border-radius:14px;border:1px solid rgba(0,0,0,.06);overflow:hidden;transition:transform .1s}
.sw-box:hover{transform:scale(1.03)}
.sw-box.proposed{border:2px dashed rgba(255,149,0,.45)}
.sw-main{height:80px;display:flex;align-items:center;justify-content:center}
.sw-lbl{font-size:15px;font-weight:700}
.sc-hex{font-size:11px;font-family:'SF Mono',Menlo,monospace;color:var(--t2);text-align:center;word-break:break-all;margin-top:5px}
.sc-tag{font-size:10px;text-align:center;font-weight:600;margin-top:2px}
.sc-tag.ex{color:var(--g)}
.sc-tag.pr{color:var(--o)}

/* Legacy items — 2 lines, no truncation */
.lg-list{margin-top:10px;display:flex;flex-direction:column;gap:4px}
.lg{display:flex;align-items:flex-start;gap:6px;padding:6px 8px;border-radius:8px;background:var(--bg);font-size:12px;line-height:1.4;transition:background .1s}
.lg:hover{background:rgba(0,0,0,.06)}
.lg.dup{opacity:.4;font-style:italic}
.lg.far{border-left:3px solid var(--o)}
.lg-sw{width:18px;height:18px;border-radius:5px;border:1px solid rgba(0,0,0,.1);flex-shrink:0;margin-top:1px}
.lg-body{flex:1;min-width:0}
.lg-n{font-weight:600;word-break:break-word}
.lg-d{color:var(--t3);font-family:'SF Mono',Menlo,monospace;font-size:10px;margin-top:1px}
.lg-far-tag{background:var(--o);color:#fff;padding:1px 5px;border-radius:4px;font-size:9px;font-weight:700;margin-left:4px}

/* Alpha blocks — bigger */
.al-row{display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap}
.al-col{width:72px;text-align:center;flex-shrink:0}
.al-sw{height:48px;border-radius:10px;border:1px solid rgba(0,0,0,.06);margin-bottom:4px}
.al-sw.proposed{border:2px dashed rgba(255,149,0,.45)}
.al-num{font-size:13px;font-weight:700}
.al-val{font-size:10px;color:var(--t2);font-family:'SF Mono',Menlo,monospace}
.al-base-sw{width:18px;height:18px;border-radius:5px;border:1px solid rgba(0,0,0,.08);display:inline-block;vertical-align:middle;margin-right:6px}

.ex-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px}
.ex-chip{display:flex;align-items:center;gap:6px;padding:6px 12px 6px 6px;background:var(--bg);border-radius:10px;font-size:13px}
.ex-sw{width:26px;height:26px;border-radius:7px;border:1px solid rgba(0,0,0,.08)}
.ex-nm{font-weight:600}
.ex-hx{font-family:'SF Mono',Menlo,monospace;font-size:11px;color:var(--t2)}

.other-grid{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:16px}
.other-block{background:var(--bg);border-radius:14px;padding:14px;min-width:200px;flex:1}
.other-main{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.other-sw-lg{width:44px;height:44px;border-radius:12px;border:1px solid rgba(0,0,0,.08)}
.other-name{font-size:15px;font-weight:700}
.other-hex{font-size:12px;font-family:'SF Mono',Menlo,monospace;color:var(--t2)}

/* TAB 2: comparison — bigger blocks */
.cmp-row{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px}
.cmp-col{background:var(--card);border-radius:var(--r);box-shadow:var(--sh);overflow:hidden}
.cmp-col-hdr{padding:16px 24px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--brd)}
.cmp-col-hdr.app{background:linear-gradient(135deg,#634AD6 0%,#0D99F6 100%);color:#fff}
.cmp-col-hdr.web{background:#1D1D1F;color:#fff}
.cmp-body{padding:20px 24px}
.cmp-fam{margin-bottom:24px}
.cmp-fam-name{font-size:16px;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px}
.cmp-scale{display:flex;gap:6px;margin-bottom:6px;flex-wrap:wrap}
.cmp-sw{width:64px;height:44px;border-radius:10px;border:1px solid rgba(0,0,0,.06);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
.cmp-sw-label{font-size:10px;text-align:center;color:var(--t2);font-family:'SF Mono',Menlo,monospace;margin-top:3px}
.placeholder-box{border:2px dashed var(--brd);border-radius:var(--r);padding:48px;text-align:center;color:var(--t3);font-size:15px}
.badge-new{background:var(--g);color:#fff;padding:1px 5px;border-radius:3px;font-size:8px;font-weight:700}

@media(max-width:900px){.stats{grid-template-columns:repeat(2,1fr)}.sc-row{grid-template-columns:repeat(3,1fr)}.cmp-row{grid-template-columns:1fr}}
"""

JS = """
function switchTab(idx){
  document.querySelectorAll('.tab-btn').forEach((b,i)=>{b.classList.toggle('active',i===idx)});
  document.querySelectorAll('.tab-pane').forEach((p,i)=>{p.classList.toggle('active',i===idx)});
}
function exportJSON(fname){
  var el=document.getElementById('json-'+fname);
  if(!el) return;
  var data=JSON.parse(el.textContent);
  var blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=fname+'.tokens.json';
  a.click();
}
"""

# Build JSON data for each family (Figma-compatible token format)
family_jsons = {}
for fname, fdata in SCALE_FAMILIES.items():
    tokens = {}
    final_solid = fdata.get("final_solid", {})
    alpha_base = fdata.get("alpha_base")
    alpha_existing = fdata.get("alpha_existing", {})
    skip_solid = fdata.get("skip_solid_scale", False)

    if final_solid and not skip_solid:
        for s in STEPS:
            tokens[f"{fname}_{s}"] = {"$type": "color", "$value": final_solid[s]["hex"]}
    if alpha_base:
        all_a = sorted(set(list(alpha_existing.keys()) + STEPS), reverse=True)
        for s in all_a:
            av = alpha_existing.get(s, s/100.0) if s in alpha_existing else s/100.0
            ahex = alpha_base.lstrip('#')
            alpha_int = round(av * 255)
            tokens[f"{fname}_alpha_{s}"] = {"$type": "color", "$value": f"#{alpha_int:02X}{ahex}"}
    family_jsons[fname] = tokens

html = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Color Tokens — Final Palette</title>
<style>{CSS}</style></head><body>

<div class="hdr"><h1>Color Tokens — Final Palette</h1>
<p>{TOTAL_INPUT} устаревших цветов &middot; {len(SCALE_FAMILIES)} семейств &middot; {len(OTHER_TOKENS)} токенов Other</p></div>

<div class="tabs-bar"><div class="tabs-inner">
<button class="tab-btn active" onclick="switchTab(0)">Анализ цветов</button>
<button class="tab-btn" onclick="switchTab(1)">Сравнение с вебом</button>
</div></div>

<!-- ===================== TAB 1: ANALYSIS ===================== -->
<div class="tab-pane active" id="tab-analysis"><div class="c">

<div class="stats" style="margin-top:32px">
<div class="st"><div class="st-n">{TOTAL_INPUT}</div><div class="st-l">Всего цветов</div></div>
<div class="st"><div class="st-n" style="color:var(--g)">{exact_c}</div><div class="st-l">Exact Match</div></div>
<div class="st"><div class="st-n" style="color:var(--bl)">{merged_c}</div><div class="st-l">Merged (ΔE&lt;5)</div></div>
<div class="st"><div class="st-n" style="color:var(--o)">{far_c}</div><div class="st-l">Далёкие (ΔE≥10)</div></div>
</div>

<div class="de-info">
<h2>Что такое ΔE (Delta E)?</h2>
<p>ΔE (Delta E 2000) — это международный стандарт измерения перцептивного различия между двумя цветами.
Формула учитывает особенности человеческого зрения: преобразует цвета из sRGB → XYZ → CIE LAB (перцептивно-равномерное пространство),
затем вычисляет разницу с поправками на яркость, насыщенность и оттенок.</p>
<p>Чем <strong>меньше</strong> ΔE — тем <strong>ближе</strong> цвета друг к другу визуально.</p>
<div class="de-scale">
<div class="de-chip exact">ΔE &lt; 1 — Exact match, неразличимы</div>
<div class="de-chip close">ΔE &lt; 5 — Очень близкие, можно объединить</div>
<div class="de-chip mid">ΔE 5–10 — Заметно отличаются, но в одной семье</div>
<div class="de-chip far">ΔE ≥ 10 — Далёкие, требуют решения</div>
</div>
</div>
"""

# ===== TAB 1: SCALE FAMILIES =====
html += '<div class="section-title">Семейства со шкалой 100 → 10</div>\n'

for fname, fdata in SCALE_FAMILIES.items():
    items = fam_legacy.get(fname, [])
    is_new = fdata.get("is_new", False)
    skip_solid = fdata.get("skip_solid_scale", False)
    final_solid = fdata.get("final_solid", {})
    alpha_base = fdata.get("alpha_base")
    alpha_existing = fdata.get("alpha_existing", {})
    alpha_label = fdata.get("alpha_label", "")
    also_alpha = fdata.get("also_alpha", [])
    extra_tokens = fdata.get("extra_tokens", {})

    strip_colors = []
    if final_solid:
        for s in STEPS: strip_colors.append(final_solid[s]["hex"])
    elif alpha_base:
        for s in STEPS: strip_colors.append(blend_on_white(alpha_base, s/100.0))

    json_id = f"json-{fname}"
    json_data = _json.dumps(family_jsons.get(fname, {}))

    html += '<div class="fam">\n<div class="fam-top">\n<div class="fam-strip">'
    for sc in strip_colors: html += f'<div class="fam-strip-sw" style="background:{sc}"></div>'
    html += f'</div>\n<div class="fam-info"><div class="fam-name">{fname} {"<span class=new-tag>НОВОЕ</span>" if is_new else ""}</div><div class="fam-desc">{fdata["desc"]}</div></div>'
    html += f'<button class="json-btn" onclick="exportJSON(\'{fname}\')">&#x2B73; JSON</button>'
    html += f'<script type="application/json" id="{json_id}">{json_data}</script>'
    html += '</div>\n'

    # SOLID SCALE
    if final_solid and not skip_solid:
        html += '<div class="sc"><div class="sc-lbl">Шкала 100 → 10 (solid hex)</div><div class="sc-row">\n'
        for s in STEPS:
            sd = final_solid[s]; hx = sd["hex"]; is_ex = sd["src"]=="base"
            tc = text_color(hx); box_cls = "" if is_ex else " proposed"
            step_items = sorted([i for i in items if i.get("assigned_step")==s], key=lambda x: x.get("step_de",999))
            html += f'<div class="sc-col"><div class="sw-box{box_cls}" style="background:{hx}"><div class="sw-main"><span class="sw-lbl" style="color:{tc}">{s}</span></div></div>'
            html += f'<div class="sc-hex">{hx}</div><div class="sc-tag {"ex" if is_ex else "pr"}">{"из мобилки" if is_ex else "предложен"}</div>'
            if step_items:
                html += '<div class="lg-list">'
                for si in step_items:
                    cls = " dup" if si["is_dup"] else ""
                    if si.get("step_de",0) >= 10: cls += " far"
                    de_lbl = "exact" if si.get("step_de",99)<0.1 else f'ΔE {si.get("step_de","?")}'
                    far_tag = '<span class="lg-far-tag">далёкий</span>' if si.get("step_de",0)>=10 else ""
                    html += f'<div class="lg{cls}" title="{si["note"]}"><div class="lg-sw" style="background:{si["hex"]}"></div><div class="lg-body"><div class="lg-n">{si["name"]}</div><div class="lg-d">{si["hex"]} {de_lbl}{far_tag}</div></div></div>'
                html += '</div>'
            html += '</div>\n'
        html += '</div></div>\n'

    # ALPHA SCALE
    if alpha_base:
        all_steps = sorted(set(list(alpha_existing.keys()) + STEPS), reverse=True)
        html += '<div class="sep"></div><div class="sc">'
        html += f'<div class="sc-lbl"><span class="al-base-sw" style="background:{alpha_base}"></span>{alpha_label} — альфа ({alpha_base})</div><div class="al-row">'
        for s in all_steps:
            is_ex = s in alpha_existing and alpha_existing[s] is not None
            av = alpha_existing.get(s) if is_ex else (s/100.0)
            bl = blend_on_white(alpha_base, av)
            sw_cls = "" if is_ex else " proposed"
            html += f'<div class="al-col"><div class="al-sw{sw_cls}" style="background:{bl}"></div><div class="al-num">{s}</div><div class="al-val">@ {int(av*100)}%</div>'
            if not is_ex: html += '<div class="sc-tag pr">NEW</div>'
            html += '</div>'
        html += '</div>'
        for (albl, ahex, asteps) in also_alpha:
            html += f'<div class="sc-lbl" style="margin-top:8px"><span class="al-base-sw" style="background:{ahex}"></span>{albl} — альфа ({ahex})</div><div class="al-row">'
            for s2 in sorted(asteps.keys(), reverse=True):
                bl2 = blend_on_white(ahex, asteps[s2])
                html += f'<div class="al-col"><div class="al-sw" style="background:{bl2}"></div><div class="al-num">{s2}</div><div class="al-val">@ {int(asteps[s2]*100)}%</div></div>'
            html += '</div>'
        html += '</div>\n'

    # EXTRA TOKENS
    if extra_tokens:
        et_reason = fdata.get("extra_tokens_reason", "")
        html += '<div class="sep"></div><div class="sc"><div class="sc-lbl">Отдельные токены</div>'
        if et_reason:
            html += f'<p style="font-size:12px;color:var(--t2);margin-bottom:12px;line-height:1.5">{et_reason}</p>'
        html += '<div class="ex-row">'
        for k, h in extra_tokens.items():
            html += f'<div class="ex-chip"><div class="ex-sw" style="background:{h}"></div><span class="ex-nm">{k}</span><span class="ex-hx">{h}</span></div>'
        html += '</div></div>\n'

    # For families with skip_solid_scale or without solid: show all legacy
    if skip_solid or not final_solid:
        if items:
            html += '<div class="sep"></div><div class="sc"><div class="sc-lbl">Устаревшие цвета → это семейство</div><div class="lg-list">'
            for item in sorted(items, key=lambda x: x["delta"]):
                cls = " dup" if item["is_dup"] else ""
                if item["delta"]>=10: cls += " far"
                de_lbl = "exact" if item["delta"]<0.1 else f'ΔE {item["delta"]}'
                far_tag = '<span class="lg-far-tag">далёкий</span>' if item["delta"]>=10 else ""
                html += f'<div class="lg{cls}"><div class="lg-sw" style="background:{item["hex"]}"></div><div class="lg-body"><div class="lg-n">{item["name"]}</div><div class="lg-d">{item["hex"]} {de_lbl}{far_tag}</div></div></div>'
            html += '</div></div>\n'

    html += '</div>\n\n'

# ===== OTHER GROUP =====
html += '<div class="section-title">Other — одиночные Core-токены</div>\n'
html += '<div class="fam"><div class="fam-top"><div class="fam-info"><div class="fam-name">Other</div><div class="fam-desc">Цвета из Core без шкалы 100→10. Одиночные токены.</div></div></div>\n'
html += '<div class="sc"><div class="other-grid">'
for tname, thex in OTHER_TOKENS.items():
    items = other_legacy.get(tname, [])
    html += f'<div class="other-block"><div class="other-main"><div class="other-sw-lg" style="background:{thex}"></div><div><div class="other-name">{tname}</div><div class="other-hex">{thex}</div></div></div>'
    if items:
        html += '<div class="lg-list">'
        for it in sorted(items, key=lambda x: x["delta"]):
            cls = " dup" if it["is_dup"] else ""
            if it["delta"]>=10: cls += " far"
            de_lbl = "exact" if it["delta"]<0.1 else f'ΔE {it["delta"]}'
            far_tag = '<span class="lg-far-tag">далёкий</span>' if it["delta"]>=10 else ""
            html += f'<div class="lg{cls}"><div class="lg-sw" style="background:{it["hex"]}"></div><div class="lg-body"><div class="lg-n">{it["name"]}</div><div class="lg-d">{it["hex"]} {de_lbl}{far_tag}</div></div></div>'
        html += '</div>'
    html += '</div>'
html += '</div></div></div>\n\n'

# ===== UNMATCHED =====
all_far = []
for items_list in fam_legacy.values():
    for i in items_list:
        if i["delta"] >= 15: all_far.append(i)
for items_list in other_legacy.values():
    for i in items_list:
        if i["delta"] >= 15: all_far.append(i)
all_far.sort(key=lambda x: -x["delta"])

if all_far:
    html += '<div class="section-title" style="color:var(--rd)">Unmatched — далёкие от всех семейств (ΔE ≥ 15)</div>\n'
    html += '<div class="fam" style="border-left:4px solid var(--rd)"><div class="sc"><div class="sc-lbl" style="color:var(--rd)">Требуют отдельного решения</div>'
    html += '<div class="lg-list">'
    for item in all_far:
        html += f'<div class="lg far"><div class="lg-sw" style="background:{item["hex"]}"></div><div class="lg-body"><div class="lg-n">{item["name"]}</div><div class="lg-d">{item["hex"]} ΔE {item["delta"]}<span class="lg-far-tag">ΔE≥15</span></div></div></div>'
    html += '</div></div></div>\n'

html += '</div></div>\n\n'  # close .c and #tab-analysis

# ===================== TAB 2: COMPARISON WITH WEB (ALPHA ONLY) =====================
html += '<div class="tab-pane" id="tab-compare"><div class="c">\n'
html += '<div class="section-title" style="margin-top:32px">Альфа-палитра — Apps vs Web</div>\n'
html += '<p style="color:var(--t2);margin-bottom:24px;font-size:14px">Левая колонка — альфа-цвета приложений (solid-on-white эквивалент). Правая — веб-палитра (скинь цвета, и я заполню).</p>\n'

for fname, fdata in SCALE_FAMILIES.items():
    alpha_base = fdata.get("alpha_base")
    if not alpha_base:
        continue  # Skip families without alpha
    alpha_existing = fdata.get("alpha_existing", {})
    alpha_label = fdata.get("alpha_label", "")
    also_alpha = fdata.get("also_alpha", [])
    is_new = fdata.get("is_new", False)

    html += '<div class="cmp-row">\n'

    # LEFT: App alpha palette
    html += '<div class="cmp-col"><div class="cmp-col-hdr app">Apps — ' + fname + (' <span class="badge-new">NEW</span>' if is_new else '') + '</div><div class="cmp-body">\n'

    all_alpha_steps = sorted(set(list(alpha_existing.keys()) + STEPS), reverse=True)
    html += f'<div class="cmp-fam"><div class="cmp-fam-name">{alpha_label} {alpha_base}</div>'
    html += '<div class="cmp-scale">'
    for s in all_alpha_steps:
        av = alpha_existing.get(s, s/100.0) if s in alpha_existing else s/100.0
        bl = blend_on_white(alpha_base, av)
        tc = text_color(bl)
        html += f'<div><div class="cmp-sw" style="background:{bl};color:{tc}">{s}</div><div class="cmp-sw-label">{bl}<br>@{int(av*100)}%</div></div>'
    html += '</div></div>\n'

    for (albl, ahex, asteps) in also_alpha:
        html += f'<div class="cmp-fam"><div class="cmp-fam-name">{albl} {ahex}</div>'
        html += '<div class="cmp-scale">'
        for s2 in sorted(asteps.keys(), reverse=True):
            bl2 = blend_on_white(ahex, asteps[s2])
            tc2 = text_color(bl2)
            html += f'<div><div class="cmp-sw" style="background:{bl2};color:{tc2}">{s2}</div><div class="cmp-sw-label">{bl2}<br>@{int(asteps[s2]*100)}%</div></div>'
        html += '</div></div>\n'

    html += '</div></div>\n'

    # RIGHT: Web palette (placeholder)
    html += '<div class="cmp-col"><div class="cmp-col-hdr web">Web — ' + fname + '</div><div class="cmp-body">\n'
    html += '<div class="placeholder-box">Скинь веб-палитру,<br>и я заполню эту колонку</div>\n'
    html += '</div></div>\n'

    html += '</div>\n'

html += '</div></div>\n'  # close .c and #tab-compare

html += f'<script>{JS}</script></body></html>'

for p in ["/tmp/color_analysis/color_consolidation.html"]:
    try:
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Written: {p} ({len(html)} bytes)")
    except Exception as e:
        print(f"SKIP {p}: {e}")
