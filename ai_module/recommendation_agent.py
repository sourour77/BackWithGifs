import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from datetime import date
from ai_module.dashboard import build_product_loyalty_message
from urllib.parse import quote
from ai_module.product_db import (
    get_product_knowledge_dict,
    get_quantity_offers_dict,
    get_bundle_offers,
    
)  
from ai_module.user_memory_db import (
    get_user_memory,
    get_user_profile,
    log_recommendation,
    get_recent_checkins,
    get_recent_chat_history,
    get_recent_recommendation_history,
)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

LANGUAGE_NAMES = {
    "ar": "Arabic",
    "fr": "French",
    "en": "English",
}
PRODUCT_SIGNAL_ALIASES = {
    "Colon Detox": {
        "digestion",
        "bloating_gas",
        "bloating",
        "gas",
        "digestive health",
        "colon",
        "gut",
        "constipation",
    },

    "Psyllium": {
        "constipation",
        "fiber_support",
        "fiber",
        "fibre" ,
        "bowel movement",
        "bowel regularity",
        "satiety",
        "appetite_control",
        "weight_loss",
        "weight management",
    },

    "Liver Detox": {
        "detox",
        "liver",
        "liver support",
    },

    "Slim Pack": {
        "weight_loss",
        "weight management",
        "slimming",
        "appetite",
        "metabolism",
    },

    "Blood Detox": {
        "blood_regulation",
        "heart_support",
        "circulation",
        "heart",
    },

    "Lung Detox": {
        "respiratory_support",
        "smoking_reduction_support",
        "lungs",
        "lung support",
        "breathing",
        "smoking",
        "respiratory",
    },

    "Berberine & Ceylon Cinnamon": {
        "glycemic_balance",
        "insulin_sensitivity",
        "sugar_cravings",
        "blood sugar",
        "glucose",
        "insulin",
   
    },
}



SUPABASE_EXERCISE_BASE_URL = (
    "https://fvelzzxktroqfyhyvuku.supabase.co/"
    "storage/v1/object/public/exercise%20gifs"
)


def exercise_video_url(filename: str) -> str:
    return (
        f"{SUPABASE_EXERCISE_BASE_URL}/"
        f"{quote(filename)}"
    )


EXERCISE_VIDEO_URLS = {
    # Filenames must match the Supabase bucket "exercise gifs" EXACTLY
    # (case, spaces and typos included).
    "male": {
        "bent_over_row_kettlebell": exercise_video_url(
            "man-bent-over-row-exercise-with-kettle-bell.mp4"
        ),
        "bent_over_row_dumbbells": exercise_video_url(
            "man-bent-over-row-with-dumbells.mp4"
        ),
        "bicep_curl": exercise_video_url(
            "man-bicep-curls.mp4"
        ),
        "bulgarian_split_squat": exercise_video_url(
            "man-bulgarian-split-squat.mp4"
        ),
        "burpee": exercise_video_url(
            "man-burpee-exercise.mp4"
        ),
        "butt_kicks": exercise_video_url(
            "man-butt-kicks.mp4"
        ),
        "calf_raise": exercise_video_url(
            "man-calf-raises.mp4"
        ),
        "concentration_curl": exercise_video_url(
            "man-concentration-curl.mp4"
        ),
        "cycling": exercise_video_url(
            "man-cycling.mp4"
        ),
        "elliptical": exercise_video_url(
            "man-elliptical.mp4"
        ),
        "front_raise": exercise_video_url(
            "man-front-raises.mp4"
        ),
        "glute_bridge": exercise_video_url(
            "man-glute-bridge.mp4"
        ),
        "hammer_curl": exercise_video_url(
            "man-hammer-curl.mp4"
        ),
        "hammer_curls": exercise_video_url(
            "man-hammer-curls.mp4"
        ),
        "high_stepping": exercise_video_url(
            "man-High Stepping.mp4"
        ),
        "hip_thrust": exercise_video_url(
            "man-hip-thrust.mp4"
        ),
        "inchworm": exercise_video_url(
            "man-Inchworm.mp4"
        ),
        "jogging": exercise_video_url(
            "man-jogging.mp4"
        ),
        "jumping_jacks": exercise_video_url(
            "man-jumping-jacks.mp4"
        ),
        "jumping_squat": exercise_video_url(
            "man-jumping-squat.mp4"
        ),
        "kettlebell_swing": exercise_video_url(
            "man-kettlebell-swing-.mp4"
        ),
        "knee_push_up": exercise_video_url(
            "man-knee-push-up.mp4"
        ),
        "lateral_raise": exercise_video_url(
            "man-literal-raises.mp4"
        ),
        "lunge": exercise_video_url(
            "man-lunges.mp4"
        ),
        "mountain_climbers": exercise_video_url(
            "man-mountain-climbers.mp4"
        ),
        "overhead_tricep_extension": exercise_video_url(
            "man-overhead-tricep-extension.mp4"
        ),
        "punches": exercise_video_url(
            "man-punches.mp4"
        ),
        "push_up": exercise_video_url(
            "man-push-up.mp4"
        ),
        "reverse_crunch": exercise_video_url(
            "man-Reverse-Crunches.mp4"
        ),
        "romanian_deadlift": exercise_video_url(
            "man-romanian-deadlift.mp4"
        ),
        "seated_hammer_curl": exercise_video_url(
            "man-seated-hammer-curl.mp4"
        ),
        "seated_lateral_raise": exercise_video_url(
            "man-seated-literal-raises.mp4"
        ),
        "seated_shoulder_press": exercise_video_url(
            "man-seated-shoulder-press.mp4"
        ),
        "seated_tricep_extension": exercise_video_url(
            "man-seated-tricep-extension.mp4"
        ),
        "shadow_boxing": exercise_video_url(
            "man-Standing Shadow Boxing.mp4"
        ),
        "shoulder_external_rotation": exercise_video_url(
            "man-shoulder-external-rotation.mp4"
        ),
        "shoulder_press": exercise_video_url(
            "man-shoulder-press.mp4"
        ),
        "shoulder_stretch": exercise_video_url(
            "man-Shoulder Stretch.mp4"
        ),
        "side_leg_deadlift": exercise_video_url(
            "man-side-leg-deadlift-exercise.mp4"
        ),
        "side_raise": exercise_video_url(
            "man-side-raises.mp4"
        ),
        "sit_up": exercise_video_url(
            "Man-Sit Up for ABS.mp4"
        ),
        "split_jump": exercise_video_url(
            "man-Split Jump.mp4"
        ),
        "squat": exercise_video_url(
            "man-squat.mp4"
        ),
        "t_plank": exercise_video_url(
            "man- T Plank.mp4"
        ),
        "upright_row": exercise_video_url(
            "man-upright-row.mp4"
        ),
        "walking": exercise_video_url(
            "walking-man.mp4"
        ),
    },

    "female": {
        "ball_pass": exercise_video_url(
            "woman-ball-pass.mp4"
        ),
        "bicycle_crunch": exercise_video_url(
            "woman-bicycle-crunches.mp4"
        ),
        "bird_dog": exercise_video_url(
            "woman-bird-dog.mp4"
        ),
        "bodyweight_good_morning": exercise_video_url(
            "woman-bodyweight-good-morning-exercise.mp4"
        ),
        "bulgarian_split_squat_jump": exercise_video_url(
            "woman-Bulgarian Split Squat Jump.mp4"
        ),
        "burpee": exercise_video_url(
            "woman-burpees.mp4"
        ),
        "calf_raise": exercise_video_url(
            "woman-calf-raises.mp4"
        ),
        "cobra_stretch": exercise_video_url(
            "woman-cobra stretch.mp4"
        ),
        "crunch": exercise_video_url(
            "woman-crunches.mp4"
        ),
        "cycling": exercise_video_url(
            "woman-cycling.mp4"
        ),
        "dead_bug": exercise_video_url(
            "woman-Deadbug.mp4"
        ),
        "dumbbell_rear_delt_row": exercise_video_url(
            "woman-dumbbell-rear-delt-row.mp4"
        ),
        "glute_kick_back": exercise_video_url(
            "woman-glute-kick-back.mp4"
        ),
        "glute_kickback_pulse": exercise_video_url(
            "woman-glute-kickback-pulse.mp4"
        ),
        "jogging": exercise_video_url(
            "woman-jogging.mp4"
        ),
        "jumping_jacks": exercise_video_url(
            "woman-jumping-jacks.mp4"
        ),
        "knee_push_up": exercise_video_url(
            "woman-knee-push-ups.mp4"
        ),
        "lunge": exercise_video_url(
            "woman-lunges-exercise.mp4"
        ),
        "lying_leg_raise_knee_tuck": exercise_video_url(
            "woman-Lying Leg Raise with Knee Tuck.mp4"
        ),
        "medicine_ball_slam": exercise_video_url(
            "woman-medicine-ball-slams.mp4"
        ),
        "mermaid_pose": exercise_video_url(
            "woman-mermaid-pose.mp4"
        ),
        "plank": exercise_video_url(
            "woman-plank-animation.mp4"
        ),
        "plie_squat": exercise_video_url(
            "woman-plie-squats-animation.mp4"
        ),
        "push_up": exercise_video_url(
            "woman-push-ups.mp4"
        ),
        "running_plank": exercise_video_url(
            "woman-running-plank.mp4"
        ),
        "shoulder_press": exercise_video_url(
            "woman-Shoulder Press.mp4"
        ),
        "side_lunge": exercise_video_url(
            "woman--side-lunges.mp4"
        ),
        "side_plank_hip_abduction": exercise_video_url(
            "woman-Side Plank Hip Abduction.mp4"
        ),
        "single_leg_deadlift": exercise_video_url(
            "woman-single-leg-deadlifts.mp4"
        ),
        "sit_up": exercise_video_url(
            "woman-sit-ups.mp4"
        ),
        "split_squat": exercise_video_url(
            "woman-split-squat.mp4"
        ),
        "squat_jump": exercise_video_url(
            "woman-squat-jumps.mp4"
        ),
        "squat": exercise_video_url(
            "woman-squats.mp4"
        ),
        "standing_side_bend": exercise_video_url(
            "woman-standing-side-bends.mp4"
        ),
        "step_up": exercise_video_url(
            "woman-step-ups.mp4"
        ),
        "three_legged_downward_dog": exercise_video_url(
            "woman-three-legged-downward-dog.mp4"
        ),
        "wall_sit": exercise_video_url(
            "woman-wall-sits.mp4"
        ),
    },
}


# =============================================================================
# Exercise library, medical safety rules and video attachment
# =============================================================================


# Catalog used when the user's sex is unknown (videos must come from somewhere).
# The female catalog is used because it holds the most low-risk mobility options.
DEFAULT_CATALOG_SEX = "female"

# Lowest-risk exercise per catalog: guarantees that every user gets a workout.
SAFE_FLOOR_EXERCISE_KEY = {
    "male": "walking",
    "female": "standing_side_bend",
}

# ---------------------------------------------------------------------------
# Safety tags
# ---------------------------------------------------------------------------
HIGH_IMPACT = "high_impact"
HIGH_INTENSITY = "high_intensity"
SUPINE = "supine"
SPINAL_FLEXION = "spinal_flexion"
ISOMETRIC_STRAIN = "isometric_strain"
EXTERNAL_LOAD = "external_load"
OVERHEAD = "overhead"
BALANCE = "balance_demanding"
KNEE_LOAD = "knee_load"
SPINE_LOAD = "spine_load"
UNVERIFIED = "unverified_content"
PRONE = "prone"            # lying face down
INVERSION = "inversion"    # head below the heart


# Exercise categories:
#   training: cardio | lower | upper | core | mobility
#   session phases: warmup | cooldown | stretch
# "category" is the main one; "categories" holds ALL categories the
# exercise belongs to (main one first). Extra ones are set in
# EXERCISE_EXTRA_CATEGORIES below.
EXERCISE_CATEGORIES = (
    "cardio", "lower", "upper", "core", "mobility",
    "warmup", "cooldown", "stretch",
)


def _exercise(en, fr, ar, category, level, dose, equipment=None, tags=()):
    return {
        "names": {"en": en, "fr": fr, "ar": ar},
        "category": category,      # main category (see EXERCISE_CATEGORIES)
        "categories": (category,), # completed from EXERCISE_EXTRA_CATEGORIES
        "level": level,            # 1 beginner, 2 intermediate, 3 advanced
        "dose": dose,              # reps | reps_side | seconds | minutes
        "equipment": equipment,    # None = bodyweight
        "tags": frozenset(tags),
    }


# One canonical entry per video key. The displayed name is ALWAYS taken from
# here, so it always describes the movement shown in the video.
EXERCISE_LIBRARY = {
    # ---------------- male catalog ----------------
    "bent_over_row_kettlebell": _exercise(
        "Bent-Over Row (Kettlebell)", "Rowing buste penché (kettlebell)",
        "تجديف منحني بالكيتل بل", "upper", 2, "reps", "kettlebell",
        (EXTERNAL_LOAD, SPINE_LOAD)),
    "bent_over_row_dumbbells": _exercise(
        "Bent-Over Row (Dumbbells)", "Rowing buste penché (haltères)",
        "تجديف منحني بالدمبل", "upper", 2, "reps", "dumbbells",
        (EXTERNAL_LOAD, SPINE_LOAD)),
    "bicep_curl": _exercise(
        "Bicep Curl", "Curl biceps", "كيرل البايسبس",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "bulgarian_split_squat": _exercise(
        "Bulgarian Split Squat", "Squat bulgare", "سكوات بلغاري",
        "lower", 3, "reps_side", None, (KNEE_LOAD, BALANCE)),
    "burpee": _exercise(
        "Burpee", "Burpee", "بيربي",
        "cardio", 3, "reps", None, (HIGH_IMPACT, HIGH_INTENSITY)),
    "butt_kicks": _exercise(
        "Butt Kicks", "Talons-fesses", "ركل الكعبين للخلف",
        "cardio", 2, "seconds", None, (HIGH_IMPACT,)),
    "calf_raise": _exercise(
        "Calf Raise", "Élévation des mollets", "رفع السمانة",
        "lower", 1, "reps"),
    "concentration_curl": _exercise(
        "Concentration Curl", "Curl concentré", "كيرل التركيز",
        "upper", 1, "reps_side", "dumbbells", (EXTERNAL_LOAD,)),
    "elliptical": _exercise(
        "Elliptical Trainer", "Vélo elliptique", "جهاز الإليبتيكال",
        "cardio", 1, "minutes", "elliptical machine"),
    "front_raise": _exercise(
        "Front Raise", "Élévation frontale", "رفع أمامي للذراعين",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "glute_bridge": _exercise(
        "Glute Bridge", "Pont fessier", "جسر الأرداف",
        "lower", 1, "reps", None, (SUPINE,)),
    "hammer_curl": _exercise(
        "Hammer Curl", "Curl marteau", "كيرل المطرقة",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "hammer_curls": _exercise(
        "Hammer Curls", "Curls marteau", "كيرل المطرقة المتكرر",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "hip_thrust": _exercise(
        "Hip Thrust", "Hip thrust", "دفع الورك (هيب ثرست)",
        "lower", 2, "reps", "bench", (EXTERNAL_LOAD,)),
    "jogging": _exercise(
        "Jogging", "Jogging", "الجري الخفيف",
        "cardio", 2, "minutes", None, (HIGH_IMPACT,)),
    "jumping_jacks": _exercise(
        "Jumping Jacks", "Jumping jacks", "القفز مع فتح الأطراف",
        "cardio", 2, "seconds", None, (HIGH_IMPACT,)),
    "jumping_squat": _exercise(
        "Jump Squat", "Squat sauté", "سكوات مع القفز",
        "cardio", 3, "reps", None, (HIGH_IMPACT, HIGH_INTENSITY, KNEE_LOAD)),
    "kettlebell_swing": _exercise(
        "Kettlebell Swing", "Swing kettlebell", "أرجحة الكيتل بل",
        "cardio", 3, "reps", "kettlebell",
        (EXTERNAL_LOAD, HIGH_INTENSITY, SPINE_LOAD)),
    "knee_push_up": _exercise(
        "Knee Push-Up", "Pompe sur les genoux", "ضغط على الركبتين",
        "upper", 1, "reps"),
    "lateral_raise": _exercise(
        "Lateral Raise", "Élévation latérale", "رفع جانبي للذراعين",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "lunge": _exercise(
        "Lunge", "Fente", "الطعنات (لانج)",
        "lower", 2, "reps_side", None, (KNEE_LOAD, BALANCE)),
    "mountain_climbers": _exercise(
        "Mountain Climbers", "Mountain climbers", "تسلق الجبل",
        "cardio", 3, "seconds", None, (HIGH_INTENSITY, ISOMETRIC_STRAIN)),
    "overhead_tricep_extension": _exercise(
        "Overhead Triceps Extension", "Extension triceps au-dessus de la tête",
        "تمديد الترايسبس فوق الرأس",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD, OVERHEAD)),
    "punches": _exercise(
        "Punches", "Coups de poing", "لكمات في الهواء",
        "cardio", 1, "seconds"),
    "push_up": _exercise(
        "Push-Up", "Pompe", "تمرين الضغط",
        "upper", 2, "reps", None, (ISOMETRIC_STRAIN,)),
    "seated_hammer_curl": _exercise(
        "Seated Hammer Curl", "Curl marteau assis", "كيرل المطرقة جالساً",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "seated_lateral_raise": _exercise(
        "Seated Lateral Raise", "Élévation latérale assise", "رفع جانبي جالساً",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "seated_shoulder_press": _exercise(
        "Seated Shoulder Press", "Développé épaules assis", "ضغط الكتفين جالساً",
        "upper", 2, "reps", "dumbbells", (EXTERNAL_LOAD, OVERHEAD)),
    "seated_tricep_extension": _exercise(
        "Seated Triceps Extension", "Extension triceps assis",
        "تمديد الترايسبس جالساً",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD, OVERHEAD)),
    "shoulder_external_rotation": _exercise(
        "Shoulder External Rotation", "Rotation externe de l'épaule",
        "التدوير الخارجي للكتف",
        "upper", 1, "reps_side", "resistance band"),
    "shoulder_press": _exercise(
        "Shoulder Press", "Développé épaules", "ضغط الكتفين",
        "upper", 2, "reps", "dumbbells", (EXTERNAL_LOAD, OVERHEAD)),
    "side_raise": _exercise(
        "Side Raise", "Élévation sur le côté", "رفع الذراعين للجانب",
        "upper", 1, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "squat": _exercise(
        "Squat", "Squat", "سكوات",
        "lower", 1, "reps", None, (KNEE_LOAD,)),
    "upright_row": _exercise(
        "Upright Row", "Rowing menton", "التجديف العمودي",
        "upper", 2, "reps", "dumbbells", (EXTERNAL_LOAD,)),
    "romanian_deadlift": _exercise(
        "Romanian Deadlift", "Soulevé de terre roumain", "الرفعة الرومانية",
        "lower", 2, "reps", "dumbbells", (EXTERNAL_LOAD, SPINE_LOAD)),
    "side_leg_deadlift": _exercise(
        "Side-Leg Deadlift", "Soulevé de terre jambe décalée",
        "رفعة مميتة بساق جانبية",
        "lower", 2, "reps_side", None, (BALANCE, SPINE_LOAD)),
    "walking": _exercise(
        "Walking", "Marche", "المشي",
        "cardio", 1, "minutes"),
    "cycling": _exercise(
        "Cycling", "Vélo", "ركوب الدراجة",
        "cardio", 1, "minutes", "bike"),
    "high_stepping": _exercise(
        "High Stepping", "Montées de genoux", "رفع الركبتين عالياً",
        "cardio", 2, "seconds", None, (HIGH_IMPACT,)),
    "inchworm": _exercise(
        "Inchworm", "Chenille (inchworm)", "تمرين الدودة",
        "mobility", 2, "reps", None, (SPINAL_FLEXION, INVERSION)),
    "reverse_crunch": _exercise(
        "Reverse Crunch", "Crunch inversé", "الكرانش العكسي",
        "core", 1, "reps", None, (SUPINE, SPINAL_FLEXION)),
    "shadow_boxing": _exercise(
        "Standing Shadow Boxing", "Shadow boxing debout",
        "الملاكمة الوهمية وقوفاً",
        "cardio", 1, "seconds"),
    "shoulder_stretch": _exercise(
        "Shoulder Stretch", "Étirement des épaules", "تمطيط الكتفين",
        "stretch", 1, "seconds"),
    "split_jump": _exercise(
        "Split Jump", "Fentes sautées", "القفز بالطعنات",
        "cardio", 3, "reps", None,
        (HIGH_IMPACT, HIGH_INTENSITY, KNEE_LOAD, BALANCE)),
    "t_plank": _exercise(
        "T Plank", "Planche en T", "بلانك على شكل T",
        "core", 2, "reps_side", None, (ISOMETRIC_STRAIN, BALANCE)),

    # ---------------- female catalog ----------------
    "ball_pass": _exercise(
        "Ball Pass", "Passe de ballon", "تمرير الكرة",
        "core", 2, "reps", "ball", (SUPINE, SPINAL_FLEXION)),
    "bicycle_crunch": _exercise(
        "Bicycle Crunch", "Crunch vélo", "كرانش الدراجة",
        "core", 2, "reps", None, (SUPINE, SPINAL_FLEXION)),
    "bird_dog": _exercise(
        "Bird Dog", "Bird dog", "تمرين بيرد دوغ",
        "core", 1, "reps_side"),
    "bodyweight_good_morning": _exercise(
        "Bodyweight Good Morning", "Good morning au poids du corps",
        "تمرين صباح الخير بوزن الجسم",
        "lower", 1, "reps", None, (SPINE_LOAD,)),
    "crunch": _exercise(
        "Crunch", "Crunch", "كرانش البطن",
        "core", 1, "reps", None, (SUPINE, SPINAL_FLEXION)),
    "glute_kick_back": _exercise(
        "Glute Kickback", "Kickback fessier", "ركلة الأرداف للخلف",
        "lower", 1, "reps_side"),
    "glute_kickback_pulse": _exercise(
        "Glute Kickback Pulse", "Kickback fessier pulsé", "ركلة الأرداف النبضية",
        "lower", 1, "reps_side"),
    "medicine_ball_slam": _exercise(
        "Medicine Ball Slam", "Slam ball", "رمي الكرة الطبية للأرض",
        "cardio", 3, "reps", "medicine ball",
        (HIGH_INTENSITY, OVERHEAD, SPINE_LOAD, EXTERNAL_LOAD)),
    "plank": _exercise(
        "Plank", "Gainage (planche)", "البلانك",
        "core", 2, "seconds", None, (ISOMETRIC_STRAIN,)),
    "plie_squat": _exercise(
        "Plié Squat", "Squat plié", "سكوات بليه",
        "lower", 1, "reps", None, (KNEE_LOAD,)),
    "running_plank": _exercise(
        "Running Plank", "Planche dynamique", "البلانك مع الجري",
        "cardio", 3, "seconds", None, (HIGH_INTENSITY, ISOMETRIC_STRAIN)),
    "side_lunge": _exercise(
        "Side Lunge", "Fente latérale", "الطعنة الجانبية",
        "lower", 2, "reps_side", None, (KNEE_LOAD, BALANCE)),
    "single_leg_deadlift": _exercise(
        "Single-Leg Deadlift", "Soulevé de terre sur une jambe",
        "الرفعة المميتة على ساق واحدة",
        "lower", 2, "reps_side", None, (BALANCE, SPINE_LOAD)),
    "sit_up": _exercise(
        "Sit-Up", "Redressement assis", "تمرين الجلوس",
        "core", 1, "reps", None, (SUPINE, SPINAL_FLEXION)),
    "split_squat": _exercise(
        "Split Squat", "Squat fendu", "سكوات مفتوح",
        "lower", 2, "reps_side", None, (KNEE_LOAD,)),
    "squat_jump": _exercise(
        "Squat Jump", "Squat sauté", "سكوات مع القفز",
        "cardio", 3, "reps", None, (HIGH_IMPACT, HIGH_INTENSITY, KNEE_LOAD)),
    "standing_side_bend": _exercise(
        "Standing Side Bend", "Inclinaison latérale debout",
        "الانحناء الجانبي وقوفاً",
        "mobility", 1, "reps_side"),
    "step_up": _exercise(
        "Step-Up", "Montée sur marche", "الصعود على الدرجة",
        "lower", 2, "reps_side", "step", (KNEE_LOAD, BALANCE)),
    "wall_sit": _exercise(
        "Wall Sit", "Chaise contre le mur", "الجلوس على الحائط",
        "lower", 2, "seconds", None, (ISOMETRIC_STRAIN, KNEE_LOAD)),
    "dumbbell_rear_delt_row": _exercise(
        "Dumbbell Rear Delt Row", "Rowing deltoïdes postérieurs (haltères)",
        "تجديف الكتف الخلفي بالدمبل",
        "upper", 2, "reps", "dumbbells", (EXTERNAL_LOAD, SPINE_LOAD)),
    "bulgarian_split_squat_jump": _exercise(
        "Bulgarian Split Squat Jump", "Squat bulgare sauté",
        "سكوات بلغاري مع القفز",
        "cardio", 3, "reps_side", None,
        (HIGH_IMPACT, HIGH_INTENSITY, KNEE_LOAD, BALANCE)),
    "cobra_stretch": _exercise(
        "Cobra Stretch", "Étirement du cobra", "تمطيط الكوبرا",
        "stretch", 1, "seconds", None, (PRONE,)),
    "dead_bug": _exercise(
        "Dead Bug", "Dead bug", "تمرين الحشرة الميتة",
        "core", 1, "reps_side", None, (SUPINE,)),
    "lying_leg_raise_knee_tuck": _exercise(
        "Lying Leg Raise with Knee Tuck",
        "Relevé de jambes allongé avec genoux rentrés",
        "رفع الساقين مستلقياً مع ثني الركبتين",
        "core", 2, "reps", None, (SUPINE, SPINAL_FLEXION, SPINE_LOAD)),
    "mermaid_pose": _exercise(
        "Mermaid Stretch", "Posture de la sirène", "وضعية حورية البحر",
        "stretch", 1, "seconds"),
    "side_plank_hip_abduction": _exercise(
        "Side Plank Hip Abduction", "Planche latérale avec abduction de hanche",
        "بلانك جانبي مع رفع الساق",
        "core", 3, "reps_side", None, (ISOMETRIC_STRAIN, BALANCE)),
    "three_legged_downward_dog": _exercise(
        "Three-Legged Downward Dog", "Chien tête en bas à trois pattes",
        "وضعية الكلب المقلوب على ثلاث نقاط",
        "stretch", 2, "seconds", None, (INVERSION, BALANCE)),
}

# Additional categories: an exercise can belong to several categories.
EXERCISE_EXTRA_CATEGORIES = {
    # --- cardio that also warms up / cools down ---
    "walking": ("warmup", "cooldown"),
    "cycling": ("warmup", "cooldown"),
    "elliptical": ("warmup", "cooldown"),
    "jogging": ("warmup",),
    "jumping_jacks": ("warmup",),
    "butt_kicks": ("warmup",),
    "high_stepping": ("warmup",),
    "punches": ("warmup",),
    "shadow_boxing": ("warmup",),
    # --- cardio that also trains strength ---
    "burpee": ("lower", "upper", "core"),
    "jumping_squat": ("lower",),
    "squat_jump": ("lower",),
    "split_jump": ("lower",),
    "bulgarian_split_squat_jump": ("lower",),
    "kettlebell_swing": ("lower", "core"),
    "mountain_climbers": ("core",),
    "running_plank": ("core",),
    "medicine_ball_slam": ("upper", "core"),
    # --- strength exercises with a second target ---
    "push_up": ("core",),
    "knee_push_up": ("core",),
    "glute_bridge": ("core", "warmup", "cooldown"),
    "step_up": ("cardio",),
    "squat": ("warmup",),
    "calf_raise": ("warmup",),
    "bodyweight_good_morning": ("warmup", "stretch"),
    "shoulder_external_rotation": ("warmup", "mobility"),
    # --- core exercises with a second target ---
    "t_plank": ("upper",),
    "side_plank_hip_abduction": ("lower",),
    "bird_dog": ("warmup", "mobility"),
    "dead_bug": ("warmup",),
    # --- mobility / stretching ---
    "inchworm": ("warmup", "stretch", "cooldown"),
    "standing_side_bend": ("warmup", "cooldown", "stretch"),
    "shoulder_stretch": ("mobility", "cooldown"),
    "cobra_stretch": ("mobility", "cooldown"),
    "mermaid_pose": ("mobility", "cooldown"),
    "three_legged_downward_dog": ("mobility", "cooldown"),
}

for _key, _extra in EXERCISE_EXTRA_CATEGORIES.items():
    if _key in EXERCISE_LIBRARY:
        _meta = EXERCISE_LIBRARY[_key]
        _meta["categories"] = tuple(dict.fromkeys(
            (_meta["category"],) + tuple(_extra)
        ))


def exercise_has_category(exercise_key: str, category: str) -> bool:
    meta = EXERCISE_LIBRARY.get(exercise_key) or {}
    return category in meta.get("categories", (meta.get("category"),))


# ---------------------------------------------------------------------------
# Medical rules (conservative, based on general exercise-safety guidance).
# Terms are matched as substrings of the user's medical_conditions.
# ---------------------------------------------------------------------------
EXERCISE_CONDITION_RULES = [
    {
        "note": "pregnancy",
        "terms": ("pregnan", "grossesse", "enceinte", "حامل", "الحمل"),
        "exclude": {HIGH_IMPACT, HIGH_INTENSITY, SUPINE, SPINAL_FLEXION,
                    ISOMETRIC_STRAIN, EXTERNAL_LOAD, BALANCE, OVERHEAD,
                    PRONE, INVERSION},
        "max_level": 1,
        "clearance": True,
    },
    {
        "note": "postpartum",
        "terms": ("breastfeed", "postpartum", "allaitement", "allaite",
                  "رضاعة", "مرضعة"),
        "exclude": {HIGH_IMPACT, HIGH_INTENSITY, SPINAL_FLEXION, EXTERNAL_LOAD},
        "max_level": 1,
        "clearance": True,
    },
    {
        "note": "chest_pain",
        "terms": ("chest pain", "douleur thoracique", "douleur à la poitrine",
                  "ألم في الصدر", "ألم الصدر"),
        "exclude": {HIGH_IMPACT, HIGH_INTENSITY, ISOMETRIC_STRAIN,
                    EXTERNAL_LOAD, OVERHEAD, SPINAL_FLEXION, INVERSION},
        "max_level": 1,
        "clearance": True,
    },
    {
        "note": "cardiac",
        "terms": ("heart", "cardiac", "cardiaque", "coeur", "cœur",
                  "القلب", "قلبي"),
        "exclude": {HIGH_IMPACT, HIGH_INTENSITY, ISOMETRIC_STRAIN,
                    EXTERNAL_LOAD, OVERHEAD, INVERSION},
        "max_level": 1,
        "clearance": True,
    },
    {
        "note": "hypertension",
        "terms": ("hypertension", "high blood pressure", "tension artérielle",
                  "ضغط الدم", "الضغط"),
        "exclude": {HIGH_INTENSITY, ISOMETRIC_STRAIN, EXTERNAL_LOAD, OVERHEAD,
                    INVERSION},
        "max_level": 2,
        "clearance": False,
    },
    {
        "note": "surgery",
        "terms": ("surgery", "surgical", "chirurgie", "opéré", "opération",
                  "عملية جراحية", "جراحة"),
        "exclude": {HIGH_IMPACT, HIGH_INTENSITY, ISOMETRIC_STRAIN,
                    EXTERNAL_LOAD, SPINAL_FLEXION, PRONE},
        "max_level": 1,
        "clearance": True,
    },
    {
        "note": "injury",
        "terms": ("injur", "blessure", "blessé", "إصابة"),
        "exclude": {HIGH_IMPACT, HIGH_INTENSITY, EXTERNAL_LOAD},
        "max_level": 1,
        "clearance": True,
    },
    {
        "note": "joint",
        "terms": ("knee", "arthritis", "arthrose", "genou", "الركبة", "المفاصل"),
        "exclude": {HIGH_IMPACT, KNEE_LOAD},
        "max_level": 2,
        "clearance": False,
    },
    {
        "note": "back",
        "terms": ("back pain", "lower back", "hernia", "sciatica", "mal de dos",
                  "lombalgie", "lombaire", "hernie", "sciatique",
                  "الظهر", "ديسك", "انزلاق غضروفي"),
        "exclude": {HIGH_IMPACT, EXTERNAL_LOAD, SPINE_LOAD, SPINAL_FLEXION},
        "max_level": 2,
        "clearance": False,
    },
    {
        "note": "bone",
        "terms": ("osteoporosis", "ostéoporose", "هشاشة العظام"),
        "exclude": {HIGH_IMPACT, SPINAL_FLEXION, EXTERNAL_LOAD},
        "max_level": 2,
        "clearance": False,
    },
    {
        "note": "asthma",
        "terms": ("asthma", "asthme", "الربو"),
        "exclude": {HIGH_INTENSITY},
        "max_level": 2,
        "clearance": False,
    },
    {
        "note": "diabetes",
        "terms": ("diabet", "diabète", "السكري"),
        "exclude": set(),
        "max_level": None,
        "clearance": False,
    },
]

EXERCISE_SAFETY_NOTES = {
    "en": {
        "clearance": "Get your doctor's approval before doing this session.",
        "general": "Stop immediately if you feel pain, dizziness, chest discomfort or unusual shortness of breath.",
        "pregnancy": "During pregnancy, avoid lying flat on your back, jumping and holding your breath; you should be able to talk while exercising.",
        "postpartum": "After childbirth, return to exercise gradually and avoid intense abdominal exercises until cleared.",
        "chest_pain": "Chest pain must be checked by a doctor before any exercise. Seek urgent care if it occurs during effort.",
        "cardiac": "With a heart condition, keep the effort light and avoid straining or holding your breath.",
        "hypertension": "With high blood pressure, breathe continuously and avoid holding your breath, heavy or overhead efforts.",
        "surgery": "After recent surgery, exercise only once your surgeon has approved it and avoid straining the operated area.",
        "injury": "Avoid any movement that loads or hurts the injured area.",
        "joint": "Keep knee movements pain-free and controlled; reduce the range if needed.",
        "back": "Keep your back neutral and avoid movements that trigger back pain.",
        "bone": "Avoid jumping, twisting and bending your spine forward.",
        "asthma": "Keep your inhaler nearby and warm up gradually.",
        "diabetes": "If you take glucose-lowering treatment, check your blood sugar and keep a quick source of sugar nearby.",
        "older_adult": "Use a chair or wall for support if your balance feels uncertain.",
    },
    "fr": {
        "clearance": "Demandez l'accord de votre médecin avant de faire cette séance.",
        "general": "Arrêtez immédiatement en cas de douleur, vertige, gêne thoracique ou essoufflement inhabituel.",
        "pregnancy": "Pendant la grossesse, évitez de vous allonger sur le dos, les sauts et de bloquer votre respiration ; vous devez pouvoir parler pendant l'effort.",
        "postpartum": "Après l'accouchement, reprenez progressivement et évitez les exercices abdominaux intenses sans accord médical.",
        "chest_pain": "Une douleur thoracique doit être examinée par un médecin avant toute activité. Consultez en urgence si elle survient à l'effort.",
        "cardiac": "En cas de problème cardiaque, gardez un effort léger et évitez de forcer ou de bloquer votre respiration.",
        "hypertension": "En cas d'hypertension, respirez en continu et évitez de bloquer votre respiration, les charges lourdes et les efforts au-dessus de la tête.",
        "surgery": "Après une opération récente, ne reprenez qu'avec l'accord de votre chirurgien et évitez de solliciter la zone opérée.",
        "injury": "Évitez tout mouvement qui sollicite ou fait mal à la zone blessée.",
        "joint": "Gardez les mouvements des genoux contrôlés et sans douleur ; réduisez l'amplitude si besoin.",
        "back": "Gardez le dos neutre et évitez les mouvements qui déclenchent une douleur.",
        "bone": "Évitez les sauts, les torsions et la flexion du dos vers l'avant.",
        "asthma": "Gardez votre inhalateur à portée de main et échauffez-vous progressivement.",
        "diabetes": "Si vous prenez un traitement hypoglycémiant, contrôlez votre glycémie et gardez une source de sucre rapide à portée de main.",
        "older_adult": "Appuyez-vous sur une chaise ou un mur si votre équilibre est incertain.",
    },
    "ar": {
        "clearance": "احصل على موافقة طبيبك قبل القيام بهذه الحصة.",
        "general": "توقف فوراً إذا شعرت بألم أو دوخة أو انزعاج في الصدر أو ضيق تنفس غير معتاد.",
        "pregnancy": "خلال الحمل، تجنبي الاستلقاء على الظهر والقفز وحبس النفس، ويجب أن تستطيعي الكلام أثناء التمرين.",
        "postpartum": "بعد الولادة، عودي إلى التمارين تدريجياً وتجنبي تمارين البطن القوية قبل موافقة الطبيب.",
        "chest_pain": "ألم الصدر يجب أن يفحصه الطبيب قبل أي نشاط بدني. اطلب المساعدة العاجلة إذا ظهر أثناء المجهود.",
        "cardiac": "مع وجود مشكلة في القلب، حافظ على مجهود خفيف وتجنب الضغط على نفسك أو حبس النفس.",
        "hypertension": "مع ارتفاع ضغط الدم، تنفس بشكل متواصل وتجنب حبس النفس والأوزان الثقيلة والتمارين فوق الرأس.",
        "surgery": "بعد عملية جراحية حديثة، لا تتمرن إلا بموافقة الجراح وتجنب إجهاد المنطقة التي أجريت فيها العملية.",
        "injury": "تجنب أي حركة تضغط على مكان الإصابة أو تسبب لك ألماً.",
        "joint": "حافظ على حركات الركبة بطيئة وبدون ألم، وقلل مدى الحركة إذا لزم الأمر.",
        "back": "حافظ على ظهرك مستقيماً وتجنب الحركات التي تسبب ألم الظهر.",
        "bone": "تجنب القفز والالتواء وثني الظهر إلى الأمام.",
        "asthma": "احتفظ ببخاخك قريباً منك وقم بالإحماء تدريجياً.",
        "diabetes": "إذا كنت تستعمل علاجاً لخفض السكر، راقب نسبة السكر واحتفظ بمصدر سكر سريع قريباً منك.",
        "older_adult": "استعن بكرسي أو حائط إذا لم تكن متأكداً من توازنك.",
    },
}

FALLBACK_WORKOUT_TEXTS = {
    "en": {
        "title": "Today's guided workout",
        "description": "A short video-guided session built from your goal, activity level and health profile.",
        "warmup": "3–5 minutes of easy marching on the spot, shoulder rolls and gentle joint circles.",
        "cooldown": "3–5 minutes of slow breathing and gentle stretching of the muscles you worked.",
        "reason_cold_start": "We don't have activity data for you yet, so this is a short, conservative session. Your daily check-ins will help adapt the next ones.",
        "reason_activity": "The exercises, volume and intensity are matched to your recent activity and today's focus.",
        "reason_safety": "Exercises that are not suitable for your health profile were excluded.",
    },
    "fr": {
        "title": "Séance guidée du jour",
        "description": "Une courte séance guidée en vidéo, construite selon votre objectif, votre niveau d'activité et votre profil de santé.",
        "warmup": "3 à 5 minutes de marche sur place, rotations des épaules et mobilisation douce des articulations.",
        "cooldown": "3 à 5 minutes de respiration lente et d'étirements doux des muscles travaillés.",
        "reason_cold_start": "Nous n'avons pas encore de données d'activité, cette séance est donc courte et prudente. Vos check-ins quotidiens permettront d'adapter les prochaines.",
        "reason_activity": "Les exercices, le volume et l'intensité sont adaptés à votre activité récente et à l'objectif du jour.",
        "reason_safety": "Les exercices non adaptés à votre profil de santé ont été exclus.",
    },
    "ar": {
        "title": "حصة التمارين الموجهة لليوم",
        "description": "حصة قصيرة بالفيديو حضّرناها حسب هدفك ومستوى نشاطك وحالتك الصحية.",
        "warmup": "3 إلى 5 دقائق من المشي في المكان وتدوير الكتفين وتحريك المفاصل بلطف.",
        "cooldown": "3 إلى 5 دقائق من التنفس البطيء والتمطيط الخفيف للعضلات التي اشتغلت عليها.",
        "reason_cold_start": "ليست لدينا بعد بيانات عن نشاطك، لذلك هذه الحصة قصيرة وحذرة. تسجيلاتك اليومية ستساعدنا على تكييف الحصص القادمة.",
        "reason_activity": "التمارين وعدد المجموعات والشدة مناسبة لنشاطك الأخير ولهدف اليوم.",
        "reason_safety": "تم استبعاد التمارين غير المناسبة لحالتك الصحية.",
    },
}

DOSE_TABLE = {
    "reps": {1: (2, 8), 2: (3, 10), 3: (3, 12)},
    "reps_side": {1: (2, 8), 2: (3, 10), 3: (3, 12)},
    "seconds": {1: (2, 20), 2: (3, 30), 3: (3, 40)},
    "minutes": {1: 5, 2: 8, 3: 10},
}

DOSE_FORMATS = {
    "en": {
        "reps": "{sets} × {count} reps",
        "reps_side": "{sets} × {count} reps per side",
        "seconds": "{sets} × {count} sec",
        "minutes": "{count} min",
    },
    "fr": {
        "reps": "{sets} × {count} répétitions",
        "reps_side": "{sets} × {count} répétitions par côté",
        "seconds": "{sets} × {count} s",
        "minutes": "{count} min",
    },
    "ar": {
        "reps": "{sets} × {count} تكرارات",
        "reps_side": "{sets} × {count} تكرارات لكل جهة",
        "seconds": "{sets} × {count} ثانية",
        "minutes": "{count} دقائق",
    },
}

INTENSITY_LABELS = {
    "fr": {
        "light": "légère",
        "light to moderate": "légère à modérée",
        "moderate": "modérée",
        "moderate to high": "modérée à élevée",
    },
    "ar": {
        "light": "خفيفة",
        "light to moderate": "خفيفة إلى متوسطة",
        "moderate": "متوسطة",
        "moderate to high": "متوسطة إلى مرتفعة",
    },
}

FREQUENCY_LABELS = {
    "fr": {
        "today": "Aujourd'hui",
        "3 times per week": "3 fois par semaine",
        "as approved by doctor": "selon l'avis du médecin",
        "most days of the week": "la plupart des jours de la semaine",
    },
    "ar": {
        "today": "اليوم",
        "3 times per week": "3 مرات في الأسبوع",
        "as approved by doctor": "حسب موافقة الطبيب",
        "most days of the week": "أغلب أيام الأسبوع",
    },
}

WORKOUT_LINE_SEPARATOR = " — "



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _to_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _conditions_text(merged_profile: dict) -> str:
    conditions = (merged_profile or {}).get("medical_conditions") or []
    if not isinstance(conditions, list):
        conditions = [conditions]
    return " ".join(str(item).lower() for item in conditions)


def _intensity_to_level(intensity) -> int:
    text = str(intensity or "").lower()
    if "high" in text:
        return 3
    if "moderate" in text:
        return 2
    return 1


def normalize_sex(sex: str | None) -> str | None:
    value = str(sex or "").strip().lower()

    if value == "male":
        return "male"

    if value == "female":
        return "female"

    return None


def resolve_catalog_sex(
    sex: str | None,
    merged_profile: dict | None = None,
) -> str:
    """Always returns a catalog, so every user can receive a workout."""
    normalized = normalize_sex(sex)
    if normalized:
        return normalized

    conditions_text = _conditions_text(merged_profile or {})
    for rule in EXERCISE_CONDITION_RULES:
        if rule["note"] in {"pregnancy", "postpartum"} and any(
            term in conditions_text for term in rule["terms"]
        ):
            return "female"

    return DEFAULT_CATALOG_SEX


def build_exercise_safety_profile(
    merged_profile: dict,
    exercise_strategy: dict,
) -> dict:
    merged_profile = merged_profile or {}
    exercise_strategy = exercise_strategy or {}
    today_program = exercise_strategy.get("today_program") or {}

    conditions_text = _conditions_text(merged_profile)
    excluded_tags: set[str] = set()
    notes: list[str] = []
    requires_clearance = False
    has_restrictions = False

    max_level = _intensity_to_level(
        today_program.get("intensity")
        or exercise_strategy.get("intensity")
    )

    for rule in EXERCISE_CONDITION_RULES:
        if any(term in conditions_text for term in rule["terms"]):
            has_restrictions = True
            excluded_tags |= rule["exclude"]
            if rule.get("max_level"):
                max_level = min(max_level, rule["max_level"])
            requires_clearance = requires_clearance or rule["clearance"]
            if rule["note"] not in notes:
                notes.append(rule["note"])

    age = _to_float(merged_profile.get("age"))
    if age is not None and age >= 75:
        has_restrictions = True
        excluded_tags |= {HIGH_IMPACT, HIGH_INTENSITY, BALANCE}
        max_level = min(max_level, 1)
        notes.append("older_adult")
    elif age is not None and age >= 60:
        has_restrictions = True
        excluded_tags |= {HIGH_IMPACT, HIGH_INTENSITY}
        max_level = min(max_level, 2)
        notes.append("older_adult")

    bmi = _to_float(merged_profile.get("bmi"))
    if bmi is not None and bmi >= 30:
        has_restrictions = True
        excluded_tags.add(HIGH_IMPACT)
        max_level = min(max_level, 2)

    if has_restrictions:
        excluded_tags.add(UNVERIFIED)

    return {
        "excluded_tags": excluded_tags,
        "max_level": max(1, max_level),
        "requires_medical_clearance": requires_clearance,
        "notes": list(dict.fromkeys(notes)),
        "has_restrictions": has_restrictions,
    }


def is_exercise_displayable(exercise_key: str, safety: dict) -> bool:
    """Exact rule used to decide whether an exercise video can be shown.

    Shared by the LLM catalog, attach_exercise_videos and the fallback, so
    every exercise offered can actually be displayed. Equipment exercises
    are included: users do not choose with/without equipment.
    """
    return is_exercise_allowed(
        exercise_key,
        safety,
        enforce_level=True,
        allow_unverified=False,
    )


def is_exercise_allowed(
    exercise_key: str,
    safety: dict,
    *,
    enforce_level: bool = False,
    bodyweight_only: bool = False,
    allow_unverified: bool = True,
) -> bool:
    meta = EXERCISE_LIBRARY.get(exercise_key)

    if meta is None:
        # Unknown video (added to storage but not to the library):
        # never used in the fallback, and blocked for restricted users.
        return allow_unverified and not safety.get("has_restrictions")

    if not allow_unverified and UNVERIFIED in meta["tags"]:
        return False

    if meta["tags"] & safety["excluded_tags"]:
        return False

    if enforce_level and meta["level"] > safety["max_level"]:
        return False

    if bodyweight_only and meta["equipment"]:
        return False

    return True


def exercise_display_name(exercise_key: str, language: str) -> str:
    """Canonical name of the movement shown in the video."""
    meta = EXERCISE_LIBRARY.get(exercise_key)
    if meta:
        return meta["names"].get(language) or meta["names"]["en"]
    return exercise_key.replace("_", " ").title()


def default_exercise_dose(exercise_key: str, level: int, language: str) -> str:
    meta = EXERCISE_LIBRARY.get(exercise_key)
    if not meta:
        return ""

    level = min(max(int(level), 1), 3)
    dose_type = meta["dose"]
    template = DOSE_FORMATS[language][dose_type]

    if dose_type == "minutes":
        return template.format(count=DOSE_TABLE["minutes"][level])

    sets, count = DOSE_TABLE[dose_type][level]
    return template.format(sets=sets, count=count)


def format_workout_line(name: str, dose: str) -> str:
    return f"{name}{WORKOUT_LINE_SEPARATOR}{dose}" if dose else name


def _clean_llm_dose(value) -> str:
    if not isinstance(value, str):
        return ""
    value = " ".join(value.split())
    # A dose is short ("3 × 10", "30 sec"); anything longer probably
    # contains an exercise name and is discarded.
    return value if 0 < len(value) <= 40 else ""


def _localize_intensity(value, language: str) -> str:
    text = str(value or "").strip()
    return INTENSITY_LABELS.get(language, {}).get(text.lower(), text)


def _localize_frequency(value, language: str) -> str:
    text = str(value or "").strip()
    return FREQUENCY_LABELS.get(language, {}).get(text.lower(), text)


def _localize_duration(value, language: str) -> str:
    text = str(value or "").strip()
    if language == "ar":
        return text.replace("minutes", "دقيقة")
    return text


def _apply_safety_fields(recommendation: dict, safety: dict, language: str) -> None:
    texts = EXERCISE_SAFETY_NOTES[language]
    notes = []

    if safety["requires_medical_clearance"]:
        notes.append(texts["clearance"])

    notes += [texts[note] for note in safety["notes"] if note in texts]
    notes.append(texts["general"])

    recommendation["requires_medical_clearance"] = safety[
        "requires_medical_clearance"
    ]
    recommendation["safety_notes"] = list(dict.fromkeys(notes))


def _has_activity_evidence(merged_profile: dict) -> bool:
    return bool(
        merged_profile.get("average_steps_last_7_days") is not None
        or merged_profile.get("recent_activities")
        or merged_profile.get("recurring_activity_patterns")
    )


def _recently_used_exercise_keys(merged_profile: dict) -> set[str]:
    name_index = {}
    for key, meta in EXERCISE_LIBRARY.items():
        for name in meta["names"].values():
            name_index.setdefault(name.lower(), set()).add(key)

    recent = (
        (merged_profile.get("recent_recommendations_14_days") or {})
        .get("exercise_recommendations")
        or []
    )

    used = set()
    for item in recent:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
        if not isinstance(item, dict):
            continue
        for line in item.get("main_workout") or []:
            prefix = str(line).split(WORKOUT_LINE_SEPARATOR)[0].strip().lower()
            used |= name_index.get(prefix, set())

    return used


def _pick_phase_exercise(
    phase: str,
    candidates: list[str],
    exclude: set[str],
    recently_used: set[str],
    seed: int,
    prefer: str | None = None,
) -> str | None:
    """Rotate suitable warm-up and cool-down exercises."""

    options = sorted(
        key for key in candidates
        if key not in exclude
        and exercise_has_category(key, phase)
    )

    if not options:
        return None

    size = len(options)

    ranked = sorted(
        options,
        key=lambda key: (
            key in recently_used,
            (options.index(key) + seed) % size,
            not (prefer and exercise_has_category(key, prefer)),
        ),
    )

    return ranked[0]


def attach_phase_media(
    recommendation: dict,
    video_catalog: dict,
    safety: dict,
    merged_profile: dict,
    language: str,
) -> None:
    """Add one warm-up and one cool-down video to a workout (additive fields)."""
    allowed = [
        key for key in video_catalog
        if key in EXERCISE_LIBRARY and is_exercise_displayable(key, safety)
    ]
    used = set(recommendation.get("exercise_keys") or [])
    recently_used = _recently_used_exercise_keys(merged_profile)
    seed = date.today().toordinal() + sum(
        ord(char) for char in str(merged_profile.get("user_id") or "")
    )

    for phase, prefer in (("warmup", None), ("cooldown", "stretch")):
        key = _pick_phase_exercise(
            phase, allowed, used, recently_used, seed, prefer=prefer
        )
        media = []
        if key:
            used.add(key)
            media.append({
                "exercise_key": key,
                "exercise_name": exercise_display_name(key, language),
                "dose": default_exercise_dose(key, 1, language),
                "equipment": EXERCISE_LIBRARY[key]["equipment"],
                "video_url": video_catalog[key],
                "has_video": True,
                "display_type": "video",
            })
        recommendation[f"{phase}_media"] = media


def _plan_categories(exercise_strategy: dict, merged_profile: dict) -> list[str]:
    today_program = (exercise_strategy or {}).get("today_program") or {}
    focus = " ".join([
        str(today_program.get("focus") or ""),
        str(today_program.get("activity") or ""),
    ]).lower()

    if "walking" in focus:
        categories = ["cardio", "lower", "mobility", "upper"]
    elif any(word in focus for word in (
        "stress", "mobility", "recovery", "safety", "balance", "relief",
    )):
        categories = ["mobility", "core", "lower", "mobility"]
    elif "lower" in focus:
        categories = ["cardio", "lower", "lower", "core"]
    elif "upper" in focus:
        categories = ["cardio", "upper", "upper", "core"]
    elif "cardio" in focus:
        categories = ["cardio", "lower", "upper", "core"]
    elif "strength" in focus or "full body" in focus:
        categories = ["lower", "upper", "core", "lower"]
    else:
        categories = ["cardio", "lower", "upper", "core"]

    bmi = _to_float(merged_profile.get("bmi"))
    if bmi is not None and bmi < 18.5:
        # Low BMI: avoid excessive cardio, support strength.
        categories = [
            "upper" if category == "cardio" else category
            for category in categories
        ]

    return categories


# ---------------------------------------------------------------------------
# Public functions (same names/signatures as before)
# ---------------------------------------------------------------------------
def get_available_exercise_keys(
    sex: str | None,
    merged_profile: dict | None = None,
    exercise_strategy: dict | None = None,
) -> list[str]:
    catalog_sex = resolve_catalog_sex(sex, merged_profile)
    keys = list(EXERCISE_VIDEO_URLS.get(catalog_sex, {}).keys())

    if merged_profile is None:
        return keys

    safety = build_exercise_safety_profile(
        merged_profile, exercise_strategy or {}
    )
    return [key for key in keys if is_exercise_allowed(key, safety)]


def get_llm_exercise_catalog(
    sex: str | None,
    merged_profile: dict,
    exercise_strategy: dict,
) -> list[dict]:
    """Exercises the LLM may choose from, with their metadata.

    Uses exactly the same filter as attach_exercise_videos, so every
    exercise offered to the LLM can actually be displayed.
    """
    merged_profile = merged_profile or {}
    language = normalize_language(merged_profile.get("language", "ar"))
    catalog_sex = resolve_catalog_sex(sex, merged_profile)
    safety = build_exercise_safety_profile(merged_profile, exercise_strategy)
    recently_used = _recently_used_exercise_keys(merged_profile)

    catalog = []
    for key in EXERCISE_VIDEO_URLS.get(catalog_sex, {}):
        meta = EXERCISE_LIBRARY.get(key)
        if not meta or not is_exercise_displayable(key, safety):
            continue
        catalog.append({
            "key": key,
            "name": exercise_display_name(key, language),
            "category": meta["category"],
            "categories": list(meta["categories"]),
            "level": meta["level"],
            "dose_type": meta["dose"],
            "equipment": meta["equipment"],
            "used_in_last_14_days": key in recently_used,
        })

    return catalog


def choose_catalog_fallback(
    sex: str | None,
    merged_profile: dict,
    exercise_strategy: dict,
) -> list[str]:
    """Personalized, medically filtered fallback. Never returns an empty list."""
    merged_profile = merged_profile or {}
    catalog_sex = resolve_catalog_sex(sex, merged_profile)
    catalog = EXERCISE_VIDEO_URLS.get(catalog_sex, {})
    safety = build_exercise_safety_profile(merged_profile, exercise_strategy)
    recently_used = _recently_used_exercise_keys(merged_profile)

    allowed = sorted(
        key for key in catalog
        if key in EXERCISE_LIBRARY
        and is_exercise_displayable(key, safety)
    )

    seed = date.today().toordinal() + sum(
        ord(char) for char in str(merged_profile.get("user_id") or "")
    )

    def ranked(candidates: list[str]) -> list[str]:
        ordered = sorted(candidates)
        size = len(ordered) or 1
        return sorted(
            ordered,
            key=lambda key: (
                key in recently_used,                                   # variety
                safety["max_level"] - EXERCISE_LIBRARY[key]["level"],   # fitness
                (ordered.index(key) + seed) % size,                     # rotation
            ),
        )

    count = (
        4
        if safety["max_level"] >= 2 and not safety["requires_medical_clearance"]
        else 3
    )

    selected: list[str] = []
    categories = _plan_categories(exercise_strategy, merged_profile)

    # When today's program is walking-based, use the walking video itself.
    today_program = (exercise_strategy or {}).get("today_program") or {}
    if (
        "walking" in str(today_program.get("focus") or "").lower()
        and "walking" in allowed
    ):
        selected.append("walking")
        if "cardio" in categories:
            categories.remove("cardio")

    for category in categories:
        if len(selected) >= count:
            break
        candidates = [
            key for key in allowed
            if key not in selected
            and exercise_has_category(key, category)
        ]
        if candidates:
            selected.append(ranked(candidates)[0])

    for key in ranked([key for key in allowed if key not in selected]):
        if len(selected) >= count:
            break
        selected.append(key)

    if not selected:
        return []

    return selected


def build_fallback_workout(
    sex: str | None,
    merged_profile: dict,
    exercise_strategy: dict,
) -> dict | None:
    merged_profile = merged_profile or {}
    exercise_strategy = exercise_strategy or {}
    language = normalize_language(merged_profile.get("language", "ar"))
    catalog = EXERCISE_VIDEO_URLS[resolve_catalog_sex(sex, merged_profile)]
    safety = build_exercise_safety_profile(merged_profile, exercise_strategy)
    keys = choose_catalog_fallback(sex, merged_profile, exercise_strategy)

    if not keys:
        return None

    texts = FALLBACK_WORKOUT_TEXTS[language]
    today_program = exercise_strategy.get("today_program") or {}

    main_workout = []
    exercise_media = []

    for key in keys:
        name = exercise_display_name(key, language)
        dose = default_exercise_dose(key, safety["max_level"], language)
        main_workout.append(format_workout_line(name, dose))
        exercise_media.append({
            "exercise_key": key,
            "exercise_name": name,
            "dose": dose,
            "equipment": EXERCISE_LIBRARY[key]["equipment"],
            "video_url": catalog[key],
            "has_video": True,
            "display_type": "video",
        })

    reason_parts = [
        texts["reason_activity"]
        if _has_activity_evidence(merged_profile)
        else texts["reason_cold_start"]
    ]
    if safety["has_restrictions"]:
        reason_parts.append(texts["reason_safety"])

    recommendation = {
        "title": texts["title"],
        "description": texts["description"],
        "duration": _localize_duration(
            today_program.get("duration") or exercise_strategy.get("duration"),
            language,
        ),
        "frequency": _localize_frequency(
            today_program.get("frequency") or exercise_strategy.get("frequency"),
            language,
        ),
        "intensity": _localize_intensity(
            today_program.get("intensity") or exercise_strategy.get("intensity"),
            language,
        ),
        "warmup": texts["warmup"],
        "main_workout": main_workout,
        "exercise_keys": keys,
        "exercise_media": exercise_media,
        "cooldown": texts["cooldown"],
        "reason": " ".join(reason_parts),
        "is_fallback": True,
    }

    attach_phase_media(recommendation, catalog, safety, merged_profile, language)
    _apply_safety_fields(recommendation, safety, language)
    return recommendation


def _minimal_safe_workout(
    sex: str | None,
    merged_profile: dict,
    exercise_strategy: dict,
) -> dict:
    """Last-resort workout: built without any optional logic so it cannot fail."""
    merged_profile = merged_profile or {}
    language = normalize_language(merged_profile.get("language", "ar"))

    try:
        catalog_sex = resolve_catalog_sex(sex, merged_profile)
    except Exception:
        catalog_sex = DEFAULT_CATALOG_SEX

    catalog = (
        EXERCISE_VIDEO_URLS.get(catalog_sex)
        or EXERCISE_VIDEO_URLS[DEFAULT_CATALOG_SEX]
    )
    key = SAFE_FLOOR_EXERCISE_KEY.get(catalog_sex)
    if key not in catalog:
        key = next(iter(catalog))

    name = exercise_display_name(key, language)
    dose = default_exercise_dose(key, 1, language)
    texts = FALLBACK_WORKOUT_TEXTS[language]

    recommendation = {
        "title": texts["title"],
        "description": texts["description"],
        "duration": _localize_duration("15-20 minutes", language),
        "frequency": _localize_frequency("Today", language),
        "intensity": _localize_intensity("light", language),
        "warmup": texts["warmup"],
        "main_workout": [format_workout_line(name, dose)],
        "exercise_keys": [key],
        "exercise_media": [{
            "exercise_key": key,
            "exercise_name": name,
            "dose": dose,
            "equipment": (EXERCISE_LIBRARY.get(key) or {}).get("equipment"),
            "video_url": catalog[key],
            "has_video": True,
            "display_type": "video",
        }],
        "cooldown": texts["cooldown"],
        "reason": texts["reason_cold_start"],
        "is_fallback": True,
    }

    try:
        safety = build_exercise_safety_profile(merged_profile, exercise_strategy)
        _apply_safety_fields(recommendation, safety, language)
    except Exception:
        recommendation["requires_medical_clearance"] = True
        recommendation["safety_notes"] = [
            EXERCISE_SAFETY_NOTES[language]["clearance"],
            EXERCISE_SAFETY_NOTES[language]["general"],
        ]

    return recommendation


def attach_exercise_videos(
    plan: dict,
    sex: str | None,
    merged_profile: dict,
    exercise_strategy: dict,
) -> dict:
    """Attach videos to the workout. Always returns at least one workout."""
    if not isinstance(plan, dict):
        plan = {}

    merged_profile = merged_profile or {}
    exercise_strategy = exercise_strategy or {}

    raw_recommendations = plan.get("exercise_recommendations")
    if isinstance(raw_recommendations, dict):
        raw_recommendations = [raw_recommendations]
    if not isinstance(raw_recommendations, list):
        raw_recommendations = []

    valid_recommendations = []

    try:
        language = normalize_language(merged_profile.get("language", "ar"))
        catalog_sex = resolve_catalog_sex(sex, merged_profile)
        video_catalog = EXERCISE_VIDEO_URLS.get(catalog_sex, {})
        safety = build_exercise_safety_profile(merged_profile, exercise_strategy)

        for recommendation in raw_recommendations:
            if not isinstance(recommendation, dict):
                continue

            # The key is the source of truth: the displayed name is derived
            # from it, so it always matches the video.
            exercise_keys = recommendation.get("exercise_keys") or []
            if not isinstance(exercise_keys, list):
                exercise_keys = [exercise_keys]

            exercise_doses = recommendation.pop("exercise_doses", None) or []
            if not isinstance(exercise_doses, list):
                exercise_doses = []

            valid_workout = []
            valid_keys = []
            exercise_media = []

            for index, raw_key in enumerate(exercise_keys):
                if not isinstance(raw_key, str):
                    continue

                exercise_key = raw_key.strip()

                if exercise_key in valid_keys:
                    continue

                video_url = video_catalog.get(exercise_key)

                if not video_url:
                    print(
                        "[WORKOUT] Removed exercise without video:",
                        exercise_key,
                    )
                    continue

                if not is_exercise_displayable(exercise_key, safety):
                    print(
                        "[WORKOUT] Removed medically unsuitable exercise:",
                        exercise_key,
                    )
                    continue

                exercise_name = exercise_display_name(exercise_key, language)

                dose = _clean_llm_dose(
                    exercise_doses[index] if index < len(exercise_doses) else None
                ) or default_exercise_dose(
                    exercise_key, safety["max_level"], language
                )

                valid_workout.append(format_workout_line(exercise_name, dose))
                valid_keys.append(exercise_key)

                exercise_media.append({
                    "exercise_key": exercise_key,
                    "exercise_name": exercise_name,
                    "dose": dose,
                    "equipment": EXERCISE_LIBRARY[exercise_key]["equipment"],
                    "video_url": video_url,
                    "has_video": True,
                    "display_type": "video",
                })

            if not exercise_media:
                continue

            recommendation["main_workout"] = valid_workout
            recommendation["exercise_keys"] = valid_keys
            recommendation["exercise_media"] = exercise_media
            recommendation["is_fallback"] = False
            attach_phase_media(
                recommendation, video_catalog, safety, merged_profile, language
            )
            _apply_safety_fields(recommendation, safety, language)
            valid_recommendations.append(recommendation)

    except Exception as exc:
        print("[WORKOUT] Error while attaching videos:", exc)
        valid_recommendations = []

    # 1st fallback: personalized, medically filtered workout.
    if not valid_recommendations:
        try:
            fallback = build_fallback_workout(
                sex,
                merged_profile,
                exercise_strategy,
            )
            if fallback and fallback.get("exercise_media"):
                valid_recommendations = [fallback]
        except Exception as exc:
            print("[WORKOUT] Personalized fallback failed:", exc)

    # 2nd fallback: minimal safe workout, so a workout is ALWAYS shown.
    if not valid_recommendations:
        plan["exercise_recommendations"] = []
        plan["exercise_safety_status"] = "no_suitable_video_workout"
        return plan

    plan["exercise_recommendations"] = valid_recommendations
    return plan


def normalize_language(language: str | None) -> str:
    language = str(language or "ar").lower().strip()
    return language if language in LANGUAGE_NAMES else "ar"


def translated_text(language: str, key: str) -> str:
    language = normalize_language(language)

    texts = {
        "ar": {
            "supplement_warning": (
                "منتجات شفاء مكملات غذائية وليست أدوية، ولا تعوّض استشارة الطبيب."
            ),
            "persistent_symptoms_warning": (
                "إذا كانت الأعراض متكررة أو قوية، من الأفضل استشارة مختص."
            ),
            "chronic_condition_warning": (
                "إذا كان لديك مرض مزمن أو تستعمل أدوية، استشر طبيباً أو صيدلياً "
                "قبل استعمال أي مكمل غذائي."
            ),
            "pregnancy_warning": (
                "خلال فترة الحمل أو الرضاعة، استشيري الطبيب قبل استعمال أي مكمل غذائي."
            ),
            "best_offer": "هذا أفضل عرض متوفر حالياً لهذا المنتج.",
            "small_habits_action": "ابدأ بعادات صغيرة وسهلة التطبيق.",
            "small_habits_reason": (
                "التغييرات التدريجية تساعدك على تحسين الاستمرارية على المدى الطويل."
            ),
            "movement_action": "زد مستوى الحركة تدريجياً.",
            "movement_reason": (
                "البدء تدريجياً يساعدك على تحسين نشاطك بطريقة واقعية وآمنة."
            ),
            "stress_action": "حاول تحسين النوم والتقليل من التوتر.",
            "stress_reason": (
                "إدارة التوتر والنوم الجيد يدعمان التعافي والصحة العامة."
            ),
            "colon_reason": (
                "تم اختياره لدعم الهضم والتخفيف من النفخة والغازات والإمساك."
            ),
            "liver_reason": (
                "تم اختياره لدعم وظائف الكبد وروتين التخلص الطبيعي من السموم."
            ),
            "slim_reason": (
                "تم اختياره ليتناسب مع هدف التحكم في الوزن."
            ),
            "blood_reason": (
                "تم اختياره لدعم الدورة الدموية وصحة القلب والراحة العامة."
            ),
            "fallback_reasoning": (
                "حضّرت لك هذه الخطة حسب هدفك وملفك وعاداتك الأخيرة "
                "حتى تساعدك على التقدم بطريقة صحية وتدريجية."
            ),
            "lung_reason": (
                "اخترنا هذا المنتج لدعم صحة الرئتين والراحة أثناء التنفس، "
                "خصوصاً ضمن خطة تدريجية للتقليل من التدخين."
            ),
            "berberine_reason": (
                "اخترنا هذا المنتج لدعم التوازن الطبيعي للسكر، "
                "وحساسية الإنسولين والتحكم في الرغبة في السكريات."
            ),
            "psyllium_reason": (
                "اخترنا هذا المنتج لدعم الهضم، وانتظام حركة الأمعاء، "
                "وزيادة الشعور بالشبع."
            ),

            "diabetes_warning": (
                "إذا كنت مصابًا بالسكري أو تستعمل أدوية لتنظيم السكر، "
                "استشر طبيبك قبل استعمال هذا المكمل. "
                    "هذا المنتج لا يُعتبر بديلاً عن العلاج الطبي."
                ),

            "hypertension_warning": (
                "إذا كنت تعاني من ارتفاع ضغط الدم أو تستعمل أدوية للضغط، "
                "استشر طبيبك قبل استعمال هذا المكمل. "
                "هذا المنتج لا يُعتبر بديلاً عن العلاج الطبي."
            ),
        },

        "fr": {
            "supplement_warning": (
                "Les produits Shifa sont des compléments alimentaires et ne remplacent "
                "pas un avis médical."
            ),
            "persistent_symptoms_warning": (
                "Si les symptômes sont fréquents ou importants, il est préférable "
                "de consulter un professionnel de santé."
            ),
            "chronic_condition_warning": (
                "Si vous souffrez d’une maladie chronique ou prenez des médicaments, "
                "consultez un médecin ou un pharmacien avant d’utiliser un complément."
            ),
            "pregnancy_warning": (
                "Pendant la grossesse ou l’allaitement, consultez votre médecin "
                "avant d’utiliser un complément alimentaire."
            ),
            "best_offer": "Voici la meilleure offre actuellement disponible pour ce produit.",
            "small_habits_action": "Commencez par de petites habitudes faciles à maintenir.",
            "small_habits_reason": (
                "Des changements progressifs favorisent une meilleure régularité "
                "sur le long terme."
            ),
            "movement_action": "Augmentez progressivement votre niveau d’activité.",
            "movement_reason": (
                "Une progression graduelle permet d’améliorer votre activité "
                "de manière réaliste et sûre."
            ),
            "stress_action": "Améliorez votre sommeil et réduisez votre stress.",
            "stress_reason": (
                "Une meilleure gestion du stress favorise la récupération "
                "et le bien-être général."
            ),
            "colon_reason": (
                "Sélectionné pour soutenir la digestion et aider en cas de ballonnements, "
                "gaz ou constipation."
            ),
            "liver_reason": (
                "Sélectionné pour soutenir le fonctionnement du foie "
                "et la détoxification naturelle."
            ),
            "slim_reason": (
                "Sélectionné pour accompagner votre objectif de gestion du poids."
            ),
            "blood_reason": (
                "Sélectionné pour soutenir la circulation sanguine, le cœur "
                "et le bien-être général."
            ),
            "fallback_reasoning": (
                "J’ai préparé ce plan selon votre objectif, votre profil et vos habitudes "
                "récentes afin de vous aider à progresser sainement."
            ),
            "lung_reason": (
                "Sélectionné pour soutenir le confort respiratoire et la santé des poumons, "
                "notamment lors d’une réduction progressive du tabac."
            ),
            "berberine_reason": (
                "Sélectionné pour soutenir l’équilibre glycémique normal, "
                "la sensibilité à l’insuline et le contrôle des envies de sucre."
            ),
            "psyllium_reason": (
                "Sélectionné pour soutenir le transit intestinal, "
                "le confort digestif et la satiété."
            ),

            "diabetes_warning": (
                "Si vous êtes diabétique ou sous traitement pour le diabète, "
                "consultez un professionnel de santé avant utilisation. "
                "Ce complément ne remplace pas votre traitement médical."
            ),

            "hypertension_warning": (
                "Si vous souffrez d'hypertension ou prenez un traitement antihypertenseur, "
                "consultez un professionnel de santé avant utilisation. "
                "Ce complément ne remplace pas votre traitement médical."
            ),
        },

        "en": {
            "supplement_warning": (
                "Shifa products are dietary supplements and do not replace medical advice."
            ),
            "persistent_symptoms_warning": (
                "If symptoms are frequent or severe, consult a healthcare professional."
            ),
            "chronic_condition_warning": (
                "If you have a chronic condition or take medication, consult a doctor "
                "or pharmacist before using any supplement."
            ),
            "pregnancy_warning": (
                "During pregnancy or breastfeeding, consult your doctor before using "
                "any dietary supplement."
            ),
            "best_offer": "This is the best currently available offer for this product.",
            "small_habits_action": "Start with small, achievable habits.",
            "small_habits_reason": (
                "Gradual changes improve long-term consistency."
            ),
            "movement_action": "Increase your movement progressively.",
            "movement_reason": (
                "A gradual approach helps improve activity safely and realistically."
            ),
            "stress_action": "Improve your sleep and reduce stress.",
            "stress_reason": (
                "Stress management and quality sleep support recovery and wellbeing."
            ),
            "colon_reason": (
                "Selected to support digestion and help with bloating, gas, "
                "and constipation."
            ),
            "liver_reason": (
                "Selected to support liver function and the body’s natural detox routine."
            ),
            "slim_reason": (
                "Selected to support your weight-management goal."
            ),
            "blood_reason": (
                "Selected to support circulation, heart health, and general wellbeing."
            ),
            "fallback_reasoning": (
                "I prepared this plan using your goal, profile, and recent habits "
                "to help you progress in a healthy and gradual way."
            ),
            "lung_reason": (
                "Selected to support lung wellness and comfortable breathing, "
                "including during gradual smoking reduction."
            ),
            "berberine_reason": (
                "Selected to support normal glucose balance, insulin sensitivity, "
                "and management of sugar cravings."
            ),
            "psyllium_reason": (
                "Selected to support digestion, bowel regularity, fiber intake, "
                "and satiety."
            ),

            "diabetes_warning": (
                "If you have diabetes or take medication for blood sugar control, "
                "consult your healthcare professional before use. "
                "This supplement does not replace medical treatment."
            ),

            "hypertension_warning": (
                "If you have high blood pressure or take medication for hypertension, "
                "consult your healthcare professional before use. "
                "This supplement does not replace medical treatment."
    ),
        },
    }

    return texts[language].get(key, "")

def calculate_bmi(weight, height_cm):
    if not weight or not height_cm:
        return None
    height_m = height_cm / 100
    if height_m <= 0:
        return None
    return round(weight / (height_m ** 2), 1)


def get_best_offer(
    product_name,
    quantity_offers_db,
    bundle_offers_db,
):
    offers = quantity_offers_db.get(product_name, [])

    active_offers = [
        offer
        for offer in offers
        if offer.get("new_price") is not None
    ]

    if active_offers:
        return max(
            active_offers,
            key=lambda offer: (
                offer.get("discount_percent", 0),
                -offer.get("quantity", 1),
            ),
        )

    for bundle in bundle_offers_db:
        if (
            bundle.get("active", True)
            and product_name in bundle.get("products", [])
        ):
            return bundle

    return None


def consolidate_recommendation_signals(merged_profile: dict) -> dict:
    """Consolidate signals already extracted by the other agents.

    This deliberately contains no LLM call: check-ins, memory and chat records
    are already structured before they reach the Recommendation Agent.
    """
    allowed_health = {
        "digestion", "bloating_gas", "constipation", "fiber_support",
        "appetite_control", "detox", "respiratory_support",
        "smoking_reduction_support", "glycemic_balance",
        "insulin_sensitivity", "sugar_cravings", "weight_loss",
        "muscle_gain", "blood_regulation", "heart_support",
        "stress_anxiety", "sleep",
    }
    allowed_food = {
        "heavy_meals", "high_sugar", "light_meals", "balanced_meals",
        "protein_intake", "vegetable_intake",
    }

    def append_unique(target: list, values, allowed: set | None = None):
        if values is None:
            return
        if not isinstance(values, list):
            values = [values]
        for value in values:
            normalized = str(value or "").lower().strip()
            if normalized and (allowed is None or normalized in allowed):
                if normalized not in target:
                    target.append(normalized)

    health_interests = []
    food_patterns = []

    # Highest priority: signals attached to recent check-ins.
    for checkin in merged_profile.get("recent_checkins", []) or []:
        append_unique(
            health_interests,
            checkin.get("health_interests"),
            allowed_health,
        )
        append_unique(
            food_patterns,
            checkin.get("food_patterns"),
            allowed_food,
        )

    # Structured profile goals and useful conversational records.
    goal_mapping = {
        "weight loss": "weight_loss",
        "weight_loss": "weight_loss",
        "weightloss": "weight_loss",
        "muscle gain": "muscle_gain",
        "muscle_gain": "muscle_gain",
    }
    goals = merged_profile.get("goals", []) or []
    if not isinstance(goals, list):
        goals = [goals]
    for goal in goals:
        mapped = goal_mapping.get(str(goal).lower().strip())
        if mapped:
            append_unique(health_interests, mapped, allowed_health)

    intent_mapping = {
        "weight_loss_advice": "weight_loss",
        "muscle_gain_advice": "muscle_gain",
        "meal_suggestion": None,
    }
    product_mapping = {
        "Colon Detox": "digestion",
        "Psyllium": "fiber_support",
        "Liver Detox": "detox",
        "Slim Pack": "weight_loss",
        "Blood Detox": "blood_regulation",
        "Lung Detox": "respiratory_support",
        "Berberine & Ceylon Cinnamon": "glycemic_balance",
    }
    for interaction in merged_profile.get("recent_chat_topics", []) or []:
        mapped_intent = intent_mapping.get(interaction.get("intent"))
        if mapped_intent:
            append_unique(health_interests, mapped_intent, allowed_health)
        product_name = (
            interaction.get("detected_product")
            or interaction.get("recommended_product")
        )
        mapped_product = product_mapping.get(product_name)
        if mapped_product:
            append_unique(health_interests, mapped_product, allowed_health)

    # Persistent memory completes the consolidated context.
    append_unique(
        health_interests,
        merged_profile.get("health_interests", []),
        allowed_health,
    )
    append_unique(
        food_patterns,
        merged_profile.get("recurring_food_patterns", []),
        allowed_food,
    )
    append_unique(
        health_interests,
        merged_profile.get("last_detected_issue"),
        allowed_health,
    )

    average_steps = merged_profile.get("average_steps_last_7_days")
    recent_activities = merged_profile.get("recent_activities", []) or []
    recurring_activity = merged_profile.get(
        "recurring_activity_patterns", []
    ) or []
    normalized_activity = [
        str(item).lower().strip() for item in recurring_activity
    ]

    if average_steps is not None:
        if average_steps >= 8000:
            activity_level = "high"
        elif average_steps >= 5000 or recent_activities:
            activity_level = "moderate"
        else:
            activity_level = "low"
    elif "high" in normalized_activity:
        activity_level = "high"
    elif "moderate" in normalized_activity:
        activity_level = "moderate"
    elif "low" in normalized_activity:
        activity_level = "low"
    elif recent_activities:
        activity_level = "moderate"
    else:
        activity_level = "unknown"

    priority_need = health_interests[0] if health_interests else None
    product_signals = list(health_interests)

    return {
        "health_interests": health_interests,
        "activity_level": activity_level,
        "food_patterns": food_patterns,
        "detected_priority_need": priority_need,
        "recommended_product_signals": product_signals,
        "meal_strategy": "",
        "exercise_strategy": "",
        "reasoning_summary": "Structured signals consolidated deterministically.",
    }


def compact_recent_recommendations(history: list[dict]) -> dict:
    """Keep only the content needed to prevent 14-day repetition."""
    meals = []
    exercises = []

    def as_items(value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else [parsed]
            except (TypeError, ValueError, json.JSONDecodeError):
                return [value]
        return [value]

    for row in history or []:
        for meal in as_items(row.get("meal_recommendations")):
            if isinstance(meal, dict):
                item = {
                    "title": meal.get("title"),
                    "recommendation": meal.get("recommendation"),
                }
            else:
                item = str(meal)
            if item and item not in meals:
                meals.append(item)

        for exercise in as_items(row.get("exercise_recommendations")):
            if isinstance(exercise, dict):
                item = {
                    "title": exercise.get("title"),
                    "description": exercise.get("description"),
                    "main_workout": exercise.get("main_workout"),
                }
            else:
                item = str(exercise)
            if item and item not in exercises:
                exercises.append(item)

    return {
        "meal_recommendations": meals,
        "exercise_recommendations": exercises,
    }

def normalize_recommendation_text(value) -> str:
    return " ".join(
        str(value or "").lower().strip().split()
    )


def exercise_is_duplicate(
    exercise: dict,
    recent_exercises: list
) -> bool:

    if not isinstance(exercise, dict):
        return False

    generated_title = normalize_recommendation_text(
        exercise.get("title")
    )

    generated_workout = [
        normalize_recommendation_text(item)
        for item in exercise.get("main_workout", [])
        if item
    ]

    for previous in recent_exercises:

        # Recommendations retrieved from Supabase may be JSON strings
        if isinstance(previous, str):
            try:
                previous = json.loads(previous)
            except (json.JSONDecodeError, TypeError):
                continue

        if not isinstance(previous, dict):
            continue

        previous_title = normalize_recommendation_text(
            previous.get("title")
        )

        previous_workout = [
            normalize_recommendation_text(item)
            for item in previous.get("main_workout", [])
            if item
        ]

        same_title = (
            generated_title
            and previous_title
            and generated_title == previous_title
        )

        same_workout = (
            generated_workout
            and previous_workout
            and generated_workout == previous_workout
        )

        if same_title or same_workout:
            return True

    return False
def extract_recommendation_signals_with_llm(merged_profile: dict) -> dict:
    fallback = {
        "health_interests": merged_profile.get("health_interests", []),
        "activity_level": "unknown",
        "food_patterns": merged_profile.get("recurring_food_patterns", []),
        "detected_priority_need": None,
        "recommended_product_signals": [],
        "meal_strategy": "",
        "exercise_strategy": "",
        "reasoning_summary": "Fallback extraction used."
    }

    if client is None:
        return fallback
    prompt = f"""
You are a wellness recommendation signal extractor for Shifa.

Analyze this user profile + memory + daily check-in data and return ONLY valid JSON.
Also use recent chatbot interactions from the last 90 days, but do not treat the full conversation as equally important.
Use only useful signals such as health concerns, product questions, repeated issues, preferences, and previous recommendations.
Ignore greetings, thanks, small talk, and unrelated messages.

Give importance in this order:
1. Last 7 days check-in/journal behavior
2. User profile and goals
3. Last 90 days useful chatbot interactions
4. Long-term memory

Allowed health_interests:
- digestion
- bloating_gas
- constipation
- fiber_support
- appetite_control
- detox
- respiratory_support
- smoking_reduction_support
- glycemic_balance
- insulin_sensitivity
- sugar_cravings
- weight_loss
- muscle_gain
- blood_regulation
- heart_support
- stress_anxiety
- sleep

Allowed activity_level:
- low
- moderate
- high
- unknown

Allowed food_patterns:
- heavy_meals
- high_sugar
- light_meals
- balanced_meals
- protein_intake
- vegetable_intake

Return this exact JSON schema:
{{
  "health_interests": [],
  "activity_level": "unknown",
  "food_patterns": [],
  "detected_priority_need": null,
  "recommended_product_signals": [],
  "meal_strategy": "",
  "exercise_strategy": "",
  "reasoning_summary": ""
}}

Product mapping signals:
- gas, bloating, general digestive discomfort -> Colon Detox
- constipation, low fiber, bowel regularity, satiety -> Psyllium
- liver or detox interest -> Liver Detox
- weight loss or high BMI -> Slim Pack
- lung wellness, breathing comfort, smoking reduction -> Lung Detox
- glucose balance, insulin sensitivity, sugar cravings -> Berberine & Ceylon Cinnamon
- blood circulation or heart support -> Blood Detox
- muscle gain -> no product unless the product database supports it

Safety:
- Do not describe any product as treating or curing disease.
- Berberine & Ceylon Cinnamon does not replace diabetes treatment.
- Lung Detox does not guarantee smoking cessation.
- Pregnancy, breastfeeding, chronic conditions, and medication use require professional advice.

Important:
- Do not invent products.
- Use only signals, not final long explanations.
- If anxiety or stress is mentioned, use stress_anxiety only.
- Use blood_regulation only when the user explicitly mentions circulation,
  heart health, blood pressure, or another cardiovascular concern.

User data:
{json.dumps(merged_profile, ensure_ascii=False, separators=(",", ":"))}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown. No explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception:
        return fallback


def add_product(recommended_products, product, reason, quantity_offers_db, bundle_offers_db):
    if product not in [p["product"] for p in recommended_products]:
        recommended_products.append({
            "product": product,
            "reason": reason,
            "offer": get_best_offer(product, quantity_offers_db, bundle_offers_db)
        })
def normalize_product_tags(product: dict) -> set[str]:
    tags = product.get("tags") or []

    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",")]

    return {
        str(tag).lower().strip()
        for tag in tags
        if str(tag).strip()
    }


def build_user_product_signals(
    signals: dict,
    merged_profile: dict,
    bmi: float | None,
) -> set[str]:
    user_signals = set()

    for item in signals.get("health_interests", []) or []:
        user_signals.add(str(item).lower().strip())

    for item in signals.get("food_patterns", []) or []:
        user_signals.add(str(item).lower().strip())

    priority = signals.get("detected_priority_need")
    if priority:
        user_signals.add(str(priority).lower().strip())

    for item in signals.get("recommended_product_signals", []) or []:
        user_signals.add(str(item).lower().strip())

    goals = merged_profile.get("goals") or []
    if not isinstance(goals, list):
        goals = [goals]

    for goal in goals:
        user_signals.add(str(goal).lower().strip())

    conditions = merged_profile.get("medical_conditions") or []
    if not isinstance(conditions, list):
        conditions = [conditions]

    conditions_text = " ".join(
        str(condition).lower()
        for condition in conditions
    )


    if "hypertension" in conditions_text:
        user_signals.update({
            "heart_support",
            "circulation",
        })
    
    if "diabetes" in conditions_text:
        user_signals.update({
            "glycemic_balance",
            "blood sugar",
            "insulin_sensitivity",
        })

    if bmi and bmi >= 25:
        user_signals.update({
            "weight_loss",
            "weight management",
        })

    if "diabetes" in conditions_text:
        user_signals.update({
            "glycemic_balance",
            "blood sugar",
        })

    return user_signals
def normalize_moods(recent_moods):
    moods_text = " ".join([str(m).lower() for m in recent_moods])

    mood_map = {
        "😔": "low_mood stress low_energy",
        "😐": "neutral",
        "🙂": "good relaxed",
        "😊": "motivated energetic",
        "🤩": "highly_motivated energetic"
    }

    for emoji, meaning in mood_map.items():
        if emoji in moods_text:
            moods_text += " " + meaning

    return moods_text
def build_nutrition_strategy(merged_profile, signals):
    strategy = {
        "calorie_approach": "balanced",
        "protein": "normal",
        "fiber": "normal",
        
        "step_goal": "",
        "avoid": [],
        "focus": []
    }

    goals = merged_profile.get("goals", [])
    bmi = merged_profile.get("bmi")
    food_patterns = signals.get("food_patterns", [])
    health = signals.get("health_interests", [])
    conditions = merged_profile.get("medical_conditions", [])
    conditions_text = " ".join(conditions).lower() if isinstance(conditions, list) else str(conditions).lower()
    sex = merged_profile.get("sex")
    age = merged_profile.get("age")
   
    recent_moods = merged_profile.get("recent_moods", [])
    avg_steps = merged_profile.get("average_steps_last_7_days")
    activity_level = signals.get("activity_level", "unknown")
   
    # Weight loss
    if "weight_loss" in goals or (bmi and bmi >= 25):
        strategy["calorie_approach"] = "moderate calorie deficit"
        strategy["protein"] = "high"
        strategy["fiber"] = "high"
        strategy["focus"] += [
            "vegetables",
            "lean proteins",
            "whole foods"
        ]

    # Muscle gain
    if "muscle_gain" in goals:
        strategy["calorie_approach"] = "small calorie surplus"
        strategy["protein"] = "very high"
        strategy["focus"] += [
            "protein-rich foods",
            "complex carbohydrates"
        ]


    # Bad food habits from check-ins
    if "heavy_meals" in food_patterns:
        strategy["avoid"].append("fried and very fatty foods")


    if "high_sugar" in food_patterns:
        strategy["avoid"].append("sugary drinks and sweets")


    # Digestion
    if "digestion" in health:
        strategy["focus"] += [
            "fiber",
            "water",
            "probiotic foods"
        ]
        strategy["avoid"].append("ultra-processed foods")
    
    if (
        "constipation" in health
        or "fiber_support" in health
    ):
        strategy["fiber"] = "high"
        strategy["focus"] += [
            "gradually increased fiber",
            "adequate water",
            "vegetables",
            "whole grains",
        ]

    if "appetite_control" in health:
        strategy["focus"] += [
            "high-satiety meals",
            "protein-rich foods",
            "fiber-rich foods",
        ]

    if (
        "glycemic_balance" in health
        or "insulin_sensitivity" in health
        or "sugar_cravings" in health
    ):
        strategy["avoid"] += [
            "sugary drinks",
            "large sweet portions",
            "refined carbohydrates",
        ]
        strategy["focus"] += [
            "non-starchy vegetables",
            "lean proteins",
            "high-fiber carbohydrates",
            "balanced meal timing",
        ]
    # Medical conditions




    strategy["avoid"] = list(dict.fromkeys(strategy["avoid"]))
    strategy["focus"] = list(dict.fromkeys(strategy["focus"]))
    # Age-based nutrition
    if age and age >= 60:
        strategy["protein"] = "high"
        strategy["focus"] += [
            "adequate protein",
            "calcium-rich foods",
            "vitamin D sources",
            "hydration"
        ]

    # Sex-based nutrition
    if sex == "female":
        strategy["focus"] += [
            "iron-rich foods",
            "calcium-rich foods"
        ]

    if sex == "male":
        strategy["focus"] += [
            "adequate portions based on activity level"
        ]

# BMI-based nutrition
    if bmi and bmi < 18.5:
        strategy["calorie_approach"] = "healthy calorie surplus"
        strategy["protein"] = "high"
        strategy["focus"] += [
            "energy-dense healthy foods",
            "protein-rich meals",
            "complex carbohydrates"
        ]

    elif bmi and 18.5 <= bmi < 25:
        strategy["calorie_approach"] = "maintenance"
        strategy["focus"] += [
            "balanced meals",
            "vegetables",
            "whole grains"
        ]

    elif bmi and bmi >= 30:
        strategy["calorie_approach"] = "gradual calorie deficit"
        strategy["focus"] += [
            "high-satiety meals",
            "lean proteins",
            "fiber-rich foods"
        ]
    
    
    # Activity/steps influence nutrition
    if (
        avg_steps is not None
        and avg_steps < 5000
        and ("weight_loss" in goals or (bmi and bmi >= 25))
    ):
        strategy["focus"] += [
            "high-satiety meals",
            "lean proteins",
            "vegetables"
        ]
        strategy["avoid"] += [
            "large portions of bread and fried foods"
        ]

    if (
        (avg_steps is not None and avg_steps >= 7500)
        or activity_level == "high"
    ):
        strategy["focus"] += [
            "recovery meals",
            "adequate carbohydrates",
            "hydration"
        ]

    if (
        "muscle_gain" in goals
        and (
            (avg_steps is not None and avg_steps >= 5000)
            or activity_level in ["moderate", "high"]
        )
    ):
        strategy["focus"] += [
            "post-workout protein",
            "complex carbohydrates after training"
        ]

    # Mood influence nutrition
    moods_text = normalize_moods(recent_moods)
    if "low_energy" in moods_text:
        strategy["focus"] += [
            "iron-rich foods",
            "regular meal timing",
            "adequate hydration"
        ]

    if "stress" in moods_text or "anxious" in moods_text or "قلق" in moods_text:
        strategy["focus"] += [
            "regular meals",
            "magnesium-rich foods",
            "omega-3 sources"
        ]

    strategy["avoid"] = list(dict.fromkeys(strategy["avoid"]))
    strategy["focus"] = list(dict.fromkeys(strategy["focus"]))
    
    # Final nutrition safety override
    if "cholesterol" in conditions_text:
        strategy["avoid"] += [
            "fried foods",
            "high saturated fat foods"
        ]
        strategy["focus"] += [
            "fiber",
            "lean proteins",
            "healthy fats"
        ]


    if "pregnancy" in conditions_text or "breastfeeding" in conditions_text:
        strategy["calorie_approach"] = "doctor-approved balanced nutrition"
        strategy["avoid"] += ["supplements without medical advice", "extreme dieting"]
        strategy["focus"] += ["balanced meals", "hydration", "doctor-approved nutrition"]

    if "diabetes" in conditions_text:
        strategy["avoid"] += ["sugary drinks", "large sweet portions"]
        strategy["focus"] += ["non-starchy vegetables", "lean protein", "quality carbohydrates"]

    if "hypertension" in conditions_text or "high blood pressure" in conditions_text:
        strategy["avoid"] += ["high sodium foods", "processed foods"]
        strategy["focus"] += ["DASH-style meals", "vegetables", "fruits", "whole grains"]

    strategy["avoid"] = list(dict.fromkeys(strategy["avoid"]))
    strategy["focus"] = list(dict.fromkeys(strategy["focus"]))

    return strategy
def find_best_bundle_for_recommendations(
    recommended_products: list[dict],
    bundle_offers_db: list,
) -> dict | None:
    recommended_names = {
        item.get("product")
        for item in recommended_products
        if item.get("product")
    }

    matching_bundles = []

    for bundle in bundle_offers_db:
        if not bundle.get("active", True):
            continue

        bundle_products = set(
            bundle.get("products") or []
        )

        overlap = recommended_names.intersection(
            bundle_products
        )

        if len(overlap) >= 2:
            matching_bundles.append({
                **bundle,
                "_overlap_count": len(overlap),
            })

    if not matching_bundles:
        return None

    matching_bundles.sort(
        key=lambda bundle: (
            bundle.get("_overlap_count", 0),
            (
                bundle.get("old_price", 0)
                - bundle.get("new_price", 0)
            ),
        ),
        reverse=True,
    )

    best = matching_bundles[0]
    best.pop("_overlap_count", None)

    return best
def rerank_products_with_llm(
    ranked_products: list[dict],
    signals: dict,
    merged_profile: dict,
) -> list[dict]:
    if client is None or not ranked_products:
        return ranked_products

    candidates = []

    for item in ranked_products[:5]:
        product = item["product"]

        candidates.append({
            "name": item["name"],
            "score": item["score"],
            "matched_signals": item["matched_signals"],
            "tags": list(
                normalize_product_tags(product)
            ),
            "benefits": (
                product.get("benefits")
                or []
            )[:3],
            "precautions": (
                product.get("precautions")
                or []
            )[:3],
        })

    prompt = f"""
You are reranking already eligible Shifa products.

Do not add products.
Do not remove medical precautions.
Do not recommend products as treatments or cures.

Return ONLY JSON:
{{
  "ordered_product_names": []
}}

User profile:
{json.dumps(merged_profile, ensure_ascii=False, separators=(",", ":"))}

Detected signals:
{json.dumps(signals, ensure_ascii=False)}

Eligible candidates:
{json.dumps(candidates, ensure_ascii=False)}

Rank the candidates from best to least relevant.
Only use product names present in eligible candidates.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return valid JSON only. "
                        "Never invent a product."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        data = json.loads(
            response.choices[0].message.content.strip()
        )

        ordered_names = data.get(
            "ordered_product_names",
            [],
        )

        by_name = {
            item["name"]: item
            for item in ranked_products
        }

        ordered = [
            by_name[name]
            for name in ordered_names
            if name in by_name
        ]

        remaining = [
            item
            for item in ranked_products
            if item["name"] not in ordered_names
        ]

        return ordered + remaining

    except Exception as exc:
        print("Product reranking failed:", exc)
        return ranked_products
def apply_digestive_product_priority(
    ranked_products: list[dict],
    signals: dict,
) -> list[dict]:
    health = set(signals.get("health_interests", []) or [])

    psyllium_priority = bool(
        health.intersection({
            "constipation",
            "fiber_support",
            "appetite_control",
        })
    )

    colon_priority = bool(
        health.intersection({
            "digestion",
            "bloating_gas",
        })
    )

    if psyllium_priority and not colon_priority:
        ranked_products = sorted(
            ranked_products,
            key=lambda item: (
                item["name"] != "Psyllium",
                -item["score"],
            ),
        )

    elif colon_priority and not psyllium_priority:
        ranked_products = sorted(
            ranked_products,
            key=lambda item: (
                item["name"] != "Colon Detox",
                -item["score"],
            ),
        )

    return ranked_products

def apply_product_goal_priority(
    ranked_products: list[dict],
    signals: dict,
    merged_profile: dict,
    bmi: float | None,
) -> list[dict]:
    """
    Apply deterministic business priorities after scoring.

    Rules:
    - General weight-loss goal -> Slim Pack
    - Glycemic/insulin/sugar signals -> Berberine
    - Berberine must not replace Slim Pack for weight loss alone
    """

    health = {
        str(item).lower().strip()
        for item in (
            signals.get("health_interests", [])
            or []
        )
    }

    recommended_signals = {
        str(item).lower().strip()
        for item in (
            signals.get(
                "recommended_product_signals",
                [],
            )
            or []
        )
    }

    goals = merged_profile.get("goals") or []

    if not isinstance(goals, list):
        goals = [goals]

    goals = {
        str(goal).lower().strip()
        for goal in goals
        if str(goal).strip()
    }

    all_signals = (
        health
        | recommended_signals
        | goals
    )

    glycemic_signals = {
        "glycemic_balance",
        "insulin_sensitivity",
        "sugar_cravings",
        "blood sugar",
        "glucose",
        "insulin",
        "diabetes",
    }

    weight_signals = {
        "weight_loss",
        "weight loss",
        "weight_management",
        "weight management",
        "slimming",
    }

    has_glycemic_need = bool(
        all_signals.intersection(
            glycemic_signals
        )
    )

    has_weight_goal = (
        bool(
            all_signals.intersection(
                weight_signals
            )
        )
        or (
            bmi is not None
            and bmi >= 25
        )
    )

    # Explicit glycemic need:
    # Berberine can be prioritized.
    if has_glycemic_need:
        return sorted(
            ranked_products,
            key=lambda item: (
                item["name"]
                != "Berberine & Ceylon Cinnamon",
                -item["score"],
            ),
        )

    # General weight-loss need without
    # glycemic signals:
    # Slim Pack must be prioritized.
    if has_weight_goal:
        return sorted(
            ranked_products,
            key=lambda item: (
                item["name"] != "Slim Pack",
                -item["score"],
            ),
        )

    return ranked_products

def build_product_reason(
    product_name: str,
    product: dict,
    matched_signals: list[str],
    language: str,
) -> str:
    fixed_reason_key = {
        "Colon Detox": "colon_reason",
        "Liver Detox": "liver_reason",
        "Slim Pack": "slim_reason",
        "Blood Detox": "blood_reason",
        "Lung Detox": "lung_reason",
        "Berberine & Ceylon Cinnamon": "berberine_reason",
        "Psyllium": "psyllium_reason",
    }.get(product_name)

    if not fixed_reason_key:
        return ""

    return translated_text(
        language,
        fixed_reason_key,
    )
def score_products(
    product_db: dict,
    signals: dict,
    merged_profile: dict,
    bmi: float | None,
) -> list[dict]:
    user_signals = build_user_product_signals(
        signals=signals,
        merged_profile=merged_profile,
        bmi=bmi,
    )

    direct_product_signals = {
        str(item).lower().strip()
        for item in (
            signals.get("recommended_product_signals", [])
            or []
        )
        if str(item).strip()
    }

    scored_products = []

    for product_name, product in product_db.items():
        product_tags = normalize_product_tags(product)

        aliases = {
            alias.lower().strip()
            for alias in PRODUCT_SIGNAL_ALIASES.get(
                product_name,
                set(),
            )
        }

        searchable_terms = product_tags | aliases

        matches = sorted({
            signal
            for signal in user_signals
            if any(
                signal == term
                or signal in term
                or term in signal
                for term in searchable_terms
            )
        })

        score = len(matches) * 3

        health = {
            str(item).lower().strip()
            for item in (
                signals.get("health_interests", [])
                or []
            )
        }

        goals = merged_profile.get("goals") or []

        if not isinstance(goals, list):
            goals = [goals]

        goals = {
            str(goal).lower().strip()
            for goal in goals
            if str(goal).strip()
        }

        glycemic_signals = {
            "glycemic_balance",
            "insulin_sensitivity",
            "sugar_cravings",
            "blood sugar",
            "glucose",
            "insulin",
            "diabetes",
        }

        weight_signals = {
            "weight_loss",
            "weight loss",
            "weight_management",
            "weight management",
            "slimming",
        }

        has_glycemic_need = bool(
            health.intersection(glycemic_signals)
        )

        has_weight_goal = (
            bool(goals.intersection(weight_signals))
            or (
                bmi is not None
                and bmi >= 25
            )
        )

        if (
            product_name == "Slim Pack"
            and has_weight_goal
        ):
            score += 8

        if (
            product_name
            == "Berberine & Ceylon Cinnamon"
        ):
            if has_glycemic_need:
                score += 8

            elif has_weight_goal:
        # Weight loss alone is not enough
        # to prioritize Berberine.
                score -= 4




        # Psyllium can support a weight-loss plan through fiber and satiety.
        if (
            product_name == "Psyllium"
            and "weight_loss" in user_signals
        ):
            score += 3

            if "satiety support for weight loss" not in matches:
                matches.append(
                    "satiety support for weight loss"
                )
        normalized_product_name = product_name.lower().strip()

        if normalized_product_name in direct_product_signals:
            score += 6

            if normalized_product_name not in matches:
                matches.append(normalized_product_name)

        if score > 0:
            scored_products.append({
                "name": product_name,
                "product": product,
                "score": score,
                "matched_signals": matches,
            })

    return sorted(
        scored_products,
        key=lambda item: item["score"],
        reverse=True,
    )
def build_exercise_strategy(merged_profile, signals):

    strategy = {
        "main_activity": "general movement",
        "duration": "30 minutes",
        "frequency": "3 times per week",
        "intensity": "moderate",
        "exercise_type": "general",
        "focus": "",
        "step_goal": "",
        "sex_context": "unspecified",
        "today_program": {},
        "body_focus": [],
        "exercise_examples": [],
        "limitations": [],
        "reasoning": []
    }

    avg_steps = merged_profile.get("average_steps_last_7_days")
    activity = signals.get("activity_level")
    age = merged_profile.get("age")
    goals = merged_profile.get("goals", [])
    conditions = merged_profile.get("medical_conditions", [])
    conditions_text = " ".join(conditions).lower() if isinstance(conditions, list) else str(conditions).lower()
    bmi = merged_profile.get("bmi")
    sex = merged_profile.get("sex")
    normalized_sex = str(sex or "").strip().lower()

    if normalized_sex in {"female", "male"}:
        strategy["sex_context"] = normalized_sex
    else:
        strategy["sex_context"] = "unspecified"
    food_patterns = signals.get("food_patterns", [])
    health = signals.get("health_interests", [])
   
    recent_moods = merged_profile.get("recent_moods", [])
    consistency = merged_profile.get("consistency_score")
    recurring_activity_patterns = (
        merged_profile.get("recurring_activity_patterns", []) or []
    )
    recent_activities = merged_profile.get("recent_activities", []) or []

    low_activity_count = recurring_activity_patterns.count("low")
    moderate_activity_count = recurring_activity_patterns.count("moderate")
    high_activity_count = recurring_activity_patterns.count("high")

    has_activity_evidence = bool(
        avg_steps is not None
        or activity in {"low", "moderate", "high"}
        or recent_activities
        or recurring_activity_patterns
    )
    
    

    
    moods_text = normalize_moods(recent_moods)

# Step-based base level

    if not has_activity_evidence:
        strategy["focus"] = "activity level not yet measured"
        strategy["step_goal"] = ""

    elif avg_steps is None:
        strategy["focus"] = "activity pattern available without step history"
        strategy["step_goal"] = ""
        strategy["reasoning"].append(
            "No step history is available. Use the activity pattern detected "
            "from check-ins or memory."
        )
    
    elif avg_steps < 5000:
        strategy["focus"] = "increase daily movement"
        strategy["step_goal"] = "start with 5000–7000 steps/day"
        strategy["duration"] = "20-30 minutes"
        strategy["intensity"] = "light"
    elif avg_steps < 7500:
        strategy["focus"] = "progressive improvement"
        strategy["step_goal"] = "reach 7000–10000 steps/day"
        strategy["intensity"] = "light to moderate"
    elif avg_steps < 10000:
        strategy["focus"] = "maintain good activity level"
        strategy["step_goal"] = "maintain 8000–10000 steps/day"
    else:
        strategy["focus"] = "maintain excellent activity level"
        strategy["step_goal"] = "maintain current activity"

# Activity-level signal from check-ins / LLM signals
    if activity == "low":
        strategy["intensity"] = "light"
        strategy["duration"] = "20-30 minutes"
        strategy["reasoning"].append("Low activity level: start progressively")

    elif activity == "moderate":
        strategy["intensity"] = "light to moderate"
        strategy["reasoning"].append("Moderate activity level: maintain and progress gradually")

    elif activity == "high":
        strategy["intensity"] = "moderate to high"
        strategy["reasoning"].append("High activity level: allow more advanced session if safe")
    
    # Long-term activity behavior from memory
    if low_activity_count >= 2:
        strategy["duration"] = "10-20 minutes"
        strategy["intensity"] = "light"
        strategy["exercise_examples"].append("short walking breaks")
        strategy["reasoning"].append("Recurring low activity pattern: build habit gradually")

    elif high_activity_count >= 2:
        strategy["reasoning"].append("Recurring high activity pattern: allow progression and recovery balance")

    elif moderate_activity_count >= 2:
        strategy["reasoning"].append("Recurring moderate activity pattern: maintain consistency and progress slowly")
# Goal-based exercise type
    if "muscle_gain" in goals:
        strategy["exercise_type"] = "strength training"
        strategy["main_activity"] = "resistance training"
        strategy["duration"] = "40-60 minutes"

    elif "weight_loss" in goals or (bmi and bmi >= 25):
        strategy["exercise_type"] = "cardio + light strength"
        strategy["main_activity"] = "cardio and full-body movement"

    else:
        strategy["exercise_type"] = "wellness movement"
        strategy["main_activity"] = "walking and mobility"
    # BMI adaptation
    if bmi and bmi >= 30:
        strategy["intensity"] = "light to moderate"
        strategy["duration"] = "20-30 minutes"
        strategy["exercise_examples"].append("low-impact cardio")
        strategy["reasoning"].append("High BMI: prefer low-impact progressive movement")

    elif bmi and bmi < 18.5:
        strategy["exercise_type"] = "strength + mobility"
        strategy["exercise_examples"].append("light resistance training")
        strategy["reasoning"].append("Low BMI: avoid excessive cardio and support strength")
# Health / behavior adaptation
    if "heavy_meals" in food_patterns:
        strategy["exercise_examples"].append("walking after meals")
        strategy["reasoning"].append("Heavy meal pattern detected")

    if "high_sugar" in food_patterns:
        strategy["exercise_examples"].append("light cardio")
        strategy["reasoning"].append("High sugar pattern detected")

    if "digestion" in health:
        strategy["exercise_examples"].append("gentle walking after meals")
        strategy["reasoning"].append("Digestive concern detected")

    if "stress_anxiety" in health or "sleep" in health or "low_mood" in moods_text:
        strategy["exercise_examples"] += ["pilates", "stretching", "breathing exercises", "relaxing walk"]
        strategy["intensity"] = "light to moderate"
        strategy["reasoning"].append("Mood/stress/sleep adaptation")

    if "energetic" in moods_text and not ("pregnancy" in conditions_text or "breastfeeding" in conditions_text):
        strategy["reasoning"].append("Good energy detected: allow slightly more progressive session")

# Consistency adaptation
    if consistency is not None and consistency < 50:
        strategy["duration"] = "10-20 minutes"
        strategy["intensity"] = "light"
        strategy["reasoning"].append("Low consistency: start with simple achievable activity")
    elif consistency is not None and consistency >= 75:
        strategy["reasoning"].append("High consistency: user can progress gradually")


    # Final cold-start override
# This must remain after goal, BMI, mood and consistency adaptations.
    if not has_activity_evidence:
        strategy["duration"] = "15-20 minutes"
        strategy["frequency"] = "Today"
        strategy["intensity"] = "light"
        strategy["step_goal"] = ""

        if "muscle_gain" in goals:
            strategy["focus"] = "beginner full-body strength and mobility"
            strategy["exercise_type"] = "beginner strength and mobility"
            strategy["main_activity"] = (
                "introductory full-body resistance and mobility"
            )
            strategy["exercise_examples"] = [
                "wall push-ups",
                "assisted squats",
                "light resistance exercises",
                "gentle mobility exercises",
            ]

        elif "weight_loss" in goals or (bmi and bmi >= 25):
            strategy["focus"] = "beginner walking and mobility"
            strategy["exercise_type"] = "beginner walking and mobility"
            strategy["main_activity"] = (
                "gentle walking and basic mobility"
            )
            strategy["exercise_examples"] = [
                "comfortable walking",
                "gentle mobility exercises",
            ]

        else:
            strategy["focus"] = "beginner wellness movement"
            strategy["exercise_type"] = "beginner wellness movement"
            strategy["main_activity"] = (
                "gentle walking, mobility, and breathing exercises"
            )
            strategy["exercise_examples"] = [
                "comfortable walking",
                "gentle mobility exercises",
                "breathing exercises",
            ]

        strategy["reasoning"].append(
            "No recent steps or activity check-ins are available. "
            "Use a short and conservative introductory session."
        )
# Daily body/type rotation
    body_rotation = ["cardio", "lower body", "upper body + core", "mobility", "full body"]
    rotation_index = date.today().weekday() % len(body_rotation)
    rotated_focus = body_rotation[rotation_index]

# Today's program selector
    if not has_activity_evidence:
        if "muscle_gain" in goals:
            today_focus = "beginner full-body strength and mobility"
            today_activity = (
                "introductory full-body resistance and mobility exercises"
            )

        elif "weight_loss" in goals or (bmi and bmi >= 25):
            today_focus = "beginner walking and mobility"
            today_activity = (
                "gentle walking and basic mobility exercises"
            )

        else:
            today_focus = "beginner wellness movement"
            today_activity = (
                "gentle walking, mobility, and breathing exercises"
            )

    elif "stress_anxiety" in health or "sleep" in health or "low_mood" in moods_text:
        today_focus = "stress relief / mobility"
        today_activity = (
            "pilates, stretching, breathing exercises, or a relaxing walk"
        )
    elif "muscle_gain" in goals:
        today_focus = rotated_focus if rotated_focus != "cardio" else "full body"
        today_activity = f"{today_focus} strength exercises adapted to your level"
    elif "weight_loss" in goals or (bmi and bmi >= 25):
        if not has_activity_evidence:
            today_focus = "beginner walking and mobility"
            today_activity = "gentle walking and basic mobility"
        else:
            today_focus = rotated_focus
            today_activity = (
                f"{today_focus} session with cardio and light strength"
            )
    else:
        today_focus = rotated_focus
        today_activity = f"{today_focus} wellness movement"

    strategy["today_program"] = {
        "focus": today_focus,
        "activity": today_activity,
        "duration": strategy.get("duration"),
        "intensity": strategy.get("intensity"),
        "step_goal": strategy.get("step_goal"),
        "extra": list(dict.fromkeys(strategy.get("exercise_examples", [])))[:3],
        
        "sex_context": strategy.get("sex_context"),
        "frequency": strategy.get("frequency"),
    
    }



    # Final safety override: medical conditions have highest priority
    if "pregnancy" in conditions_text or "breastfeeding" in conditions_text:
        strategy["main_activity"] = "doctor-approved gentle movement"
        strategy["duration"] = "15-30 minutes"
        strategy["frequency"] = "as approved by doctor"
        strategy["intensity"] = "light"
        strategy["step_goal"] = "gentle daily movement only if approved"
        strategy["exercise_examples"] = ["doctor-approved walking", "gentle mobility"]
        strategy["reasoning"].append("Pregnancy/breastfeeding safety override")
        strategy["today_program"] = {
            "focus": "safety and gentle movement",
            "activity": "doctor-approved walking or gentle mobility",
            "duration": "15-30 minutes",
            "intensity": "light",
            "step_goal": "gentle movement only if approved",
            "extra": ["avoid intense exercise", "rest if tired"],
            "sex_context": strategy.get("sex_context"),
            "frequency": strategy["frequency"]
        }



    elif "hypertension" in conditions_text or "high blood pressure" in conditions_text:
        strategy["main_activity"] = "walking and low-impact cardio"
        strategy["intensity"] = "light to moderate"
        strategy["reasoning"].append("Hypertension safety adaptation")
        strategy["today_program"] = {
            "focus": "low-impact cardio",
            "activity": "walking or low-impact cardio",
            "duration": strategy.get("duration"),
            "intensity": "light to moderate",
            "step_goal": strategy.get("step_goal"),
            "extra": ["avoid sudden intense effort"],
            "sex_context": strategy.get("sex_context"),
            "frequency": strategy.get("frequency")

        }

    elif age and age >= 60:
        strategy["main_activity"] = (
            "walking, mobility, balance, and light resistance training"
        )
        strategy["duration"] = "20-30 minutes"
        strategy["intensity"] = "light to moderate"
        strategy["frequency"] = "most days of the week"
        strategy["reasoning"].append(
            "Older adult safety adaptation"
        )

        strategy["today_program"] = {
            "focus": "balance, mobility, and gentle strength",
            "activity": (
                "walking, balance exercises, mobility, "
                "and light resistance training"
            ),
            "duration": strategy["duration"],
            "frequency": strategy["frequency"],
            "intensity": strategy["intensity"],
            "step_goal": strategy.get("step_goal"),
            "sex_context": strategy.get("sex_context"),
            "extra": [
                "use support if balance is uncertain",
                "avoid sudden high-impact effort",
                "stop if pain or dizziness occurs",
            ],
        }
    return strategy
def build_daily_variation_context() -> dict:
    today = date.today()

    meal_themes = [
        "fresh salad and grilled protein",
        "healthy Tunisian soup and protein",
        "balanced rice or whole-grain meal",
        "egg-based meal with vegetables",
        "legume-based meal",
        "grilled fish and vegetables",
        "healthy Tunisian traditional meal",
    ]

    exercise_themes = [
        "cardio",
        "lower body",
        "upper body and core",
        "mobility and recovery",
        "full body",
        "walking and light strength",
        "stretching and active recovery",
    ]

    index = today.toordinal()

    return {
        "date": str(today),
        "meal_theme": (
            meal_themes[
                index % len(meal_themes)
            ]
        ),
        "exercise_theme": (
            exercise_themes[
                index % len(exercise_themes)
            ]
        ),
        "variation_number": index,
    }
def generate_dynamic_plan_with_llm(
    merged_profile: dict,
    signals: dict,
    decision: dict,
    nutrition_strategy: dict,
    exercise_strategy: dict,
    additional_instruction: str = "",
    
):
    fallback = {
        "meal_recommendations": [],
        "exercise_recommendations": [],
        "daily_actions": [],
        "warnings": []
    }
    daily_variation = (
        build_daily_variation_context()
    )
    language = normalize_language(
        merged_profile.get("language", "ar")
    )

    language_name = LANGUAGE_NAMES[language]
    exercise_sex = normalize_sex(
        merged_profile.get("sex")
    )

    # Only exercises that have a video for this user, are medically allowed
    # and pass the display filter — with their metadata.
    exercise_catalog = get_llm_exercise_catalog(
        exercise_sex,
        merged_profile,
        exercise_strategy,
    )
    available_exercise_keys = [item["key"] for item in exercise_catalog]
    exercise_max_level = build_exercise_safety_profile(
        merged_profile, exercise_strategy
    )["max_level"]
    recent_recommendations = merged_profile.get(
        "recent_recommendations_14_days", []
    ) or []

    language_instruction = f"""
    STRICT OUTPUT LANGUAGE: {language_name}

    Every user-visible JSON value must be written only in {language_name}:
    - behavioral_insight
    - meal titles
    - meal recommendations
    - meal reasons
    - exercise titles
    - exercise recommendations
    - exercise reasons
    - daily actions
    - daily-action reasons
    - motivation_message

    Do not mix Arabic, French, and English.
    Product names such as Slim Pack, Colon Detox, Liver Detox, Blood Detox,
    Lung Detox, Psyllium, and Berberine & Ceylon Cinnamon may remain unchanged.
    """
    

    if client is None:
        return fallback

    prompt = f"""
You are a wellness recommendation assistant for Shifa.
{language_instruction}


Today's daily variation context:
{json.dumps(
    daily_variation,
    ensure_ascii=False,
)}

Daily variation rules:
- Keep the same health, nutrition and exercise strategy.
- Change the concrete meal examples according to today's meal theme.
- Change the concrete workout examples according to today's exercise theme.
- Do not change medical safety rules.
- Do not change the main user goal.
- Do not change product recommendations only for variety.
- Recommendations generated on the same date should follow the same daily theme.
- Do not generate exactly the same meal titles on consecutive days unless medically necessary.
- Do not generate exactly the same exercise session on consecutive days unless medically necessary.
- Avoid repeating the exact same meal titles and workout title every day.
- Do not repeat any meal recommendation or exercise session generated during
  the previous 14 days. Use the history below to choose genuinely different
  titles and concrete meal/workout content while preserving the same strategy,
  safety constraints, duration, intensity, and user goal.

Recommendations generated during the previous 14 days:
{json.dumps(recent_recommendations, ensure_ascii=False, separators=(",", ":"))}

Generate personalized:
1. meal recommendations
2. exercise recommendations
3. daily wellness actions

The recommendations MUST consider ALL available information:

1. User profile:
- age
- sex
- weight
- height
- BMI
- goals
- medical conditions

2. Recent 7-day behavior:
- detected food patterns from recent check-ins
- detected activity level
- consistency and behavioral trends
- mood patterns
- average daily steps

3. Long-term personalization:
- last 90 days useful chatbot interactions
- user memory and recurring patterns

4. Rule-based strategies:
- nutrition_strategy generated from scientific rules
- exercise_strategy generated from scientific rules

Do not ignore any important factor.

User profile:
{json.dumps(merged_profile, ensure_ascii=False, separators=(",", ":"))}

Extracted signals:
{json.dumps(signals, ensure_ascii=False)}

Decision layer:
{json.dumps(decision, ensure_ascii=False)}
Nutrition strategy:
{json.dumps(nutrition_strategy, ensure_ascii=False)}

Exercise strategy:
{json.dumps(exercise_strategy, ensure_ascii=False)}
The exercise recommendation MUST follow these constraints:
- Main activity: {exercise_strategy.get("main_activity")}
- Exercise type: {exercise_strategy.get("exercise_type")}
- Suggested activity context (not mandatory exercise names): {exercise_strategy.get("exercise_examples")}
- Duration: {exercise_strategy.get("duration")}
- Intensity: {exercise_strategy.get("intensity")}
- Do not replace the requested exercise type with another workout category.
Additional generation instruction:
{additional_instruction or "No additional instruction."}
Available exercise video catalog for this user (already filtered for
sex, medical conditions and level; bodyweight and equipment exercises
are both allowed):
{json.dumps(exercise_catalog, ensure_ascii=False, separators=(",", ":"))}

Maximum exercise level allowed today: {exercise_max_level}
(1 = beginner, 2 = intermediate, 3 = advanced)





Video-selection rules:
- Select every main_workout exercise exclusively from
  the available exercise video catalog.
- exercise_keys must contain only "key" values from the catalog.
- Each exercise has a main "category" and a list of "categories"
  (an exercise can belong to several). Match today's focus using ANY of
  its categories (cardio, lower, upper, core, mobility), and use its
  "level" to match the user's fitness and today's intensity.
- Categories "warmup", "cooldown" and "stretch" describe session phases.
  Choose main_workout exercises for the training part; matching warm-up
  and cool-down videos are attached automatically, so describe them in
  the "warmup" and "cooldown" text.
- Use "dose_type" for the dose format: reps, reps_side (reps per side),
  seconds (timed sets) or minutes (continuous).
- Prefer exercises with "used_in_last_14_days": false to keep variety.
- Every exercise must have a valid exercise_key.
- The exercise name must accurately describe the
  movement demonstrated in its video.
- Never invent exercises or video keys.
- Personalize exercises, sets, repetitions, duration,
  and order using the user's goals, age, BMI, recent
  activity, average steps, consistency, and exercise strategy.
- Respect known medical conditions and safety limitations.
- Do not assume unknown fitness abilities.
- Exercises with "equipment" (dumbbells, kettlebell, bike, etc.) may be
  chosen; mix them with bodyweight exercises when it fits today's focus.
- Do not generate exercises outside the video catalog.
- Return at least 3 suitable catalog exercises whenever
  at least 3 safe options are available.
- If fewer than 3 safe exercises exist, use fewer.
- exercise_doses[i] must contain ONLY the sets/repetitions or duration
  for exercise_keys[i] (for example "3 × 10", "3 × 30 sec", "8 min"),
  written in {language_name}. Never put an exercise name in exercise_doses.
- The displayed name of each exercise is taken from its video, so
  main_workout[i] must describe exactly the movement of exercise_keys[i].



Rules:
Output language: {language}

Language rules:
- If language = "fr", write everything in French.
- If language = "ar", write everything in Arabic or Tunisian Arabic.
- Do not mix French and Arabic in the same recommendation.
- Be practical and personalized.
- Avoid generic robotic recommendations.
- Adapt meals to detected food patterns.
- Adapt exercise intensity to the available activity evidence.
- Infer the current fitness level only from recent steps, activity check-ins,
  and recurring activity patterns.
- When sufficient activity evidence is available, use the inferred fitness
  level to adapt exercise type, duration, intensity, and progression.
- When no activity evidence is available, follow
  exercise_strategy.today_program exactly.
- For a cold-start user, use a light introductory session lasting
  15-20 minutes.
- Never claim that the workout matches the user's current fitness level
  when that level is unknown.
- Keep recommendations realistic.
Advanced reasoning rules:
- Use recent_chat_topics from the last 90 days only as long-term personalization signals.
- If there are no recent check-ins, meals, activities, chats, or recurring
  patterns, treat the user as a cold-start user.
- For a cold-start user, do not claim that the user already follows healthy
  meals, exercises regularly, or has made progress.
- Explain that the initial recommendations rely on profile information and
  that daily check-ins will improve future personalization.
- Do not repeat or summarize the whole chatbot conversation.
- Use chat history only to detect recurring concerns, preferences, products discussed, and repeated difficulties.
- If recent check-ins show improvement after previous poor habits, encourage progress and suggest maintaining the new habit.
- If behavior is consistently good, suggest maintenance and small optimizations.
- If behavior is worsening, give more corrective but supportive recommendations.
- Do not recommend extreme diets, unrealistic exercises, or medical claims. Prefer realistic habits adapted to the user profile and recent behavior.
- Use age to adapt exercise intensity and recovery advice.
- The exercise title and description must accurately match the main workout.
- If the workout includes strength exercises, do not describe it as only stretching or recovery.
- Younger users can tolerate more progressive activity suggestions.
- Older users should receive more gradual and recovery-focused advice.
- Use food_patterns, activity_level, average steps, mood, consistency, health interests, and today_program to personalize recommendations.
- Use BMI to adapt calorie-balance recommendations.
- High BMI -> focus on sustainable habits and progressive movement.
- Low BMI -> avoid aggressive calorie restriction.
- If medical_conditions exist, adapt meals and exercise safely.
- Do not give diagnosis or treatment.
- For diabetes: avoid high-sugar recommendations.
- For hypertension: avoid high-salt recommendations.
- For pregnancy, breastfeeding, chronic disease, or medication use: recommend medical advice before supplements.
- Do not always choose the same body focus. Use exercise_strategy.today_program.focus as today’s target and vary body focus across days when medically safe.
- Generate ONLY today’s exercise program, not a weekly plan.
- Use exercise_strategy.today_program as the main exercise recommendation.
- Today’s program must vary the exercise type/body focus depending on all available data: goal, BMI, age, sex, medical conditions, moods, average steps, activity_level, food patterns, health interests, recurring behaviors, chat history, and consistency.
- Mention body focus when available: upper body, lower body, core, cardio, mobility, recovery.
- Respect intensity, duration, frequency, step_goal, limitations and medical safety rules.
Generate ONE structured workout for today.

Return:

- title
- description
- duration
- frequency
- intensity
- warmup
- 3 to 5 main exercises
- cooldown
- reason

Example:

{{
"title":"Today's Walking Session",
"description":"A beginner-friendly cardio session.",
"duration":"15-20 minutes",
"frequency":"Today",
"intensity":"Light",
"warmup":"5 minutes easy walking",
"main_workout":[
"15 min brisk walking",
"10 squats",
"10 wall push-ups"
],
"cooldown":"5 minutes stretching",
"reason":"A conservative starting session while recent activity data is not yet available."
}}

Use exercise_strategy.today_program as the main guidance.

The session must include:
- A warm-up adapted to the user's condition (3–10 minutes)
- 3–5 exercises with precise sets/repetitions or duration
- A cool-down with stretching, breathing, or mobility exercises

Adapt the exercises according to:
- Age
- Sex (only for physiological context, never limit body parts based on sex)
- Do not assume that women require easier exercises or that men require
  harder exercises.
- Never select body focus, workout duration, or intensity based on sex alone.
- Use sex only when it is relevant to an explicitly recorded physiological
  condition, such as pregnancy and breastfeeding.
- Activity history, steps, age, BMI, goals, consistency, and medical
  conditions must determine workout difficulty.
- BMI and current fitness level when it can be inferred from recent steps,
  activity check-ins, or recurring activity patterns
- Goal (weight loss, muscle gain, general wellness)
- Medical conditions and safety limitations (highest priority)
- Average steps and activity level from the last 7 days
- Mood and consistency level
- Health interests and long-term behavior

If the user has low energy, low consistency, or low activity, propose simpler exercises.

If the user is energetic and has no medical restrictions, propose more challenging exercises.
The deterministic rule engine has already selected today's focus, duration,
intensity, step goal, medical limitations, and suitable activity category.

You must generate the exact warm-up, exercises, sets/repetitions, and cooldown
within these constraints.

Never change:
- exercise_strategy.today_program.focus
- exercise_strategy.today_program.duration
- exercise_strategy.today_program.intensity
- exercise_strategy.today_program.step_goal
- medical safety overrides

Do not generate an exercise that conflicts with the user's medical conditions,
age, BMI, activity level, consistency, or today's selected focus.
Do not recommend unsafe exercises. Medical conditions always override fitness goals.
Cultural adaptation rules:
- Adapt meal recommendations to Tunisian food culture when appropriate.
- Meal recommendations generated in the same response must be meaningfully
  different from each other.
- Do not generate two meals from the same category, such as two soups,
  two salads, or two sandwiches, in the same response.
- Vary the main ingredients, preparation method, and meal type.
- Prefer realistic Tunisian healthy meals instead of only international meals.
- Keep the recommendations compatible with the nutrition_strategy.
- You may suggest traditional Tunisian dishes with healthier adaptations.

Examples:
- Couscous with vegetables and lean chicken instead of high-fat couscous.
- Lablabi with moderate bread portions and good protein sources.
- Ojja with vegetables and controlled oil.
- Slata mechouia with tuna or eggs.
- Grilled fish with vegetables.
- Chorba with balanced portions.
- Frik soup.
- Healthy Tunisian salads.
- Fruits, nuts, yogurt, and dates can be suggested only when compatible with medical conditions. For diabetes, prefer unsweetened yogurt, nuts, and low-glycemic fruits, and avoid adding honey or excessive dates.

For weight loss:
- Reduce portions of bread, sweets, fried foods, and sugary drinks.
- Prefer grilled, steamed, and home-cooked meals.

For muscle gain:
- Increase protein sources such as eggs, chicken, fish, dairy, legumes, and Tunisian dishes rich in protein.

For diabetes or blood sugar concerns:
- Prefer low glycemic and high-fiber choices.
- Control bread, pastries, and sugary dessert portions.

Do not criticize traditional Tunisian food. Adapt it to make it healthier.

IMPORTANT:
Do not decide nutrition or exercise strategy by yourself.

The nutrition_strategy and exercise_strategy are generated by a deterministic rule engine based on BMI, goals, age, activity level, health concerns and recent behavior.

Your role is only to transform these strategies into:
- realistic meals
- suitable exercises
- practical daily actions
The behavioral_insight must speak directly to the user.
Do not say "the user".
Use a friendly coaching tone.
For French, address the person with "vous".
For Arabic, speak directly and naturally to the person.
For English, use "you".
Keep it to 1–3 short sentences.
Always follow the provided strategies.
Do not recommend extreme diets or unrealistic workouts.

- Use consistency_score:
  - low consistency -> suggest small achievable actions.
  - medium consistency -> encourage stabilization.
  - high consistency -> suggest progression and stronger discipline.
  - If consistency is low:
      be supportive and avoid harsh recommendations.

  - If consistency is high:
      use more motivating/progressive tone.
- Detect repeated unhealthy habits from recurring_food_patterns.
- Detect sedentary lifestyle from recurring_activity_patterns.

Do NOT generate supplement safety warnings.
Do NOT generate medical-condition warnings.
These warnings are already handled by the rule engine.
- If user repeatedly reports heavy meals or high sugar:
  recommendations should directly adapt to these habits.

- Avoid repeating identical recommendations every day.
- Recommendations should feel contextual, progressive, human, and realistic.
- Return ONLY valid JSON.
- For a cold-start user, do not refer to previous effort, progress,
  improvement, consistency, or achieved results.
- Encourage the user to begin with simple actions and complete daily
  check-ins for better personalization.
JSON schema:
{{
  "behavioral_insight": "",
  "meal_recommendations": [
    {{
      "title": "",
      "recommendation": "",
      "reason": ""
    }}
  ],
  
  "exercise_recommendations":[
    {{
      "title":"",
      "description":"",
      "duration":"",
      "frequency":"",
      "intensity":"",
      "warmup":"",
      "main_workout":[
          "",
          "",
          ""
      ],
      "exercise_keys":[
          "",
          "",
          ""
      ],
      "exercise_doses":[
          "",
          "",
          ""
      ],
      "cooldown":"",
      "reason":""
    }}
  ],

  "daily_actions": [
    {{
      "action": "",
      "reason": ""
    }}
  ],
  "motivation_message": "",
  "warnings": []
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)

    except Exception:
        return fallback
    
def build_recommendation_decision(
    signals: dict,
    merged_profile: dict,
    bmi: float | None,
    quantity_offers_db: dict,
    bundle_offers_db: list,
    product_db: dict | None = None,
) -> dict:
    health_interests = signals.get("health_interests", [])
    activity_level = signals.get("activity_level", "unknown")
    food_patterns = signals.get("food_patterns", [])
    priority_need = signals.get("detected_priority_need")
    goals = merged_profile.get("goals", [])
    goals_text = " ".join(goals).lower() if isinstance(goals, list) else str(goals).lower() 
    age = merged_profile.get("age")
    consistency = merged_profile.get("consistency_score")
    conditions = merged_profile.get("medical_conditions", [])
    language = normalize_language(
        merged_profile.get("language", "ar")
    )
    decision = {
        "priority_focus": None,
        "recommended_products": [],
        "meal_plan": {
            "breakfast": None,
            "lunch": None,
            "dinner": None,
            "snack": None,
        },
        "exercise_plan": {
            "main_activity": None,
            "duration": None,
            "intensity": None,
            "frequency": None,
        },
        "daily_actions": [],
        "warnings": [],
        "upsell_strategy": None,
        "confidence_score": 0,
        "used_signals": {
            "memory": False,
            "profile": False,
            "daily_checkin": False,
            "bmi": False,
            "activity": False,
        }
    }

    decision["used_signals"]["memory"] = bool(
        merged_profile.get("past_recommended_products")
        or merged_profile.get("recurring_food_patterns")
        or merged_profile.get("recurring_activity_patterns")
        or merged_profile.get("last_detected_issue")
    )
    if goals:
        decision["used_signals"]["profile"] = True

    if bmi:
        decision["used_signals"]["bmi"] = True

    if activity_level != "unknown":
        decision["used_signals"]["activity"] = True


    # -------------------------
    # 1. Decide priority focus
    # -------------------------
    if health_interests:
        decision["priority_focus"] = health_interests[0]

        decision["used_signals"]["daily_checkin"] = bool(
            merged_profile.get("recent_checkins")
        )

    elif priority_need:
        decision["priority_focus"] = priority_need

        decision["used_signals"]["daily_checkin"] = bool(
            merged_profile.get("recent_checkins")
        )

    elif (
        "weight_loss" in goals_text
        or "weight loss" in goals_text
        or "weightloss" in goals_text
    ):
        decision["priority_focus"] = "weight_loss"
        decision["used_signals"]["profile"] = True

    elif "muscle_gain" in goals_text:
        decision["priority_focus"] = "muscle_gain"
        decision["used_signals"]["profile"] = True

    elif "general_wellness" in goals_text:
        decision["priority_focus"] = "general_wellness"

    elif bmi and bmi >= 25:
        decision["priority_focus"] = "weight_management"
        decision["used_signals"]["bmi"] = True

    else:
        decision["priority_focus"] = "general_wellness"
# Advanced behavioral logic
# -------------------------

    if (
        age
        and age >= 50
        and activity_level == "low"
    ):
        decision["daily_actions"].append({
            "action": translated_text(language, "movement_action"),
            "reason": translated_text(language, "movement_reason"),
        })
    if (
        bmi and bmi >= 28
        and "high_sugar" in food_patterns
        and consistency < 50
    ):
        decision["priority_focus"] = "weight_management"

    if "stress_anxiety" in health_interests:
        decision["daily_actions"].append({
            "action": translated_text(language, "stress_action"),
            "reason": translated_text(language, "stress_reason"),
        })
    if consistency is not None and consistency < 40:
        decision["daily_actions"].append({
            "action": translated_text(language, "small_habits_action"),
            "reason": translated_text(language, "small_habits_reason"),
        })
    conditions_text = " ".join(conditions).lower() if isinstance(conditions, list) else str(conditions).lower()
    
    if "pregnancy" in conditions_text or "breastfeeding" in conditions_text:
        decision["priority_focus"] = "pregnancy_safe_wellness"
        decision["warnings"].append(
            translated_text(language, "pregnancy_warning")
        )
        decision["confidence_score"] = 70
        return decision
    # -------------------------
    # 2. Product decision
    # -------------------------
    language = normalize_language(
        merged_profile.get("language", "ar")
    )

    # OPTIMIZATION: product_db is now an optional parameter. The caller
    # (build_recommendation_agent_output) fetches it once, in parallel
    # with the other independent reads, and passes it in here. This
    # function still falls back to fetching it itself when called
    # directly without a pre-fetched product_db, so no other call site
    # or behavior changes.
    product_db = product_db or get_product_knowledge_dict()

    ranked_products = score_products(
        product_db=product_db,
        signals=signals,
        merged_profile=merged_profile,
        bmi=bmi,
    )

    ranked_products = apply_digestive_product_priority(
        ranked_products,
        signals,
    )

    ranked_products = apply_product_goal_priority(
        ranked_products=ranked_products,
        signals=signals,
        merged_profile=merged_profile,
        bmi=bmi,
    )

    # Optional AI reranking:
    # It can only reorder products already approved by the deterministic scorer.
    if ranked_products:
        # Keep the deterministic top product locked.
        locked_top_product = ranked_products[0]

        other_products = ranked_products[1:]

        if other_products:
            best_other_score = other_products[0]["score"]

            eligible_for_reranking = [
                item
                for item in other_products
                if item["score"]
                >= best_other_score - 3
            ]

            remaining_products = [
                item
                for item in other_products
                if item["score"]
                < best_other_score - 3
            ]

            # Reranking is useful only when at least two products
            # can actually exchange positions.
            if len(eligible_for_reranking) >= 2:
                eligible_for_reranking = (
                    rerank_products_with_llm(
                        ranked_products=eligible_for_reranking,
                        signals=signals,
                        merged_profile=merged_profile,
                    )
                )

            ranked_products = [
                locked_top_product,
                *eligible_for_reranking,
                *remaining_products,
            ]
    MIN_PRODUCT_SCORE = 6

    for ranked in ranked_products:
        if ranked["score"] < MIN_PRODUCT_SCORE:
            continue

        product_name = ranked["name"]
        product = ranked["product"]

        reason = build_product_reason(
            product_name=product_name,
            product=product,
            matched_signals=ranked["matched_signals"],
            language=language,
        )

        offer = get_best_offer(
            product_name,
            quantity_offers_db,
            bundle_offers_db,
        )
        loyalty_info = build_product_loyalty_message(
            user_code=(
                merged_profile.get("user_code")
                or merged_profile.get("user_id")
            ),
            product_name=product_name,
            language=merged_profile.get("language", "ar"),
        )
        decision["recommended_products"].append({
            "product": product_name,
            "reason": reason,
            "offer": offer,
            "price": product.get("price"),
            "currency": product.get("currency", "TND"),
            "image_emoji": product.get("image_emoji") or "🌿",
            "category": product.get("category"),
            "benefits": (product.get("benefits") or [])[:3],
            "matched_signals": ranked["matched_signals"],
            "score": ranked["score"],
            "loyalty_recommendation": loyalty_info,
        })
 


    # -------------------------
    if decision["recommended_products"]:
        decision["warnings"].append(
            translated_text(language, "supplement_warning")
        )
    
    selected_product_names = {
        item.get("product")
        for item in decision["recommended_products"]
    }

    if "Berberine & Ceylon Cinnamon" in selected_product_names:
        decision["warnings"].append(
            translated_text(
                language,
                "chronic_condition_warning",
            )
        )

    if "Lung Detox" in selected_product_names:
        decision["warnings"].append(
            translated_text(
                language,
                "persistent_symptoms_warning",
            )
        )
    
    conditions_text = " ".join(
        str(condition).lower()
        for condition in conditions
    )

    if (
        "diabetes" in conditions_text
        and "Berberine & Ceylon Cinnamon" in selected_product_names
    ):
        decision["warnings"].append(
            translated_text(language, "diabetes_warning")
        )

    if (
        "hypertension" in conditions_text
        and "Blood Detox" in selected_product_names
    ):
        decision["warnings"].append(
            translated_text(language, "hypertension_warning")
        )

    if priority_need in [
        "digestion",
        "bloating_gas",
        "constipation",
        "detox",
        "respiratory_support",
        "smoking_reduction_support",
        "glycemic_balance",
        "insulin_sensitivity",
        "blood_regulation",
        "heart_support",
        "stress_anxiety",
    ]:
        decision["warnings"].append(
            translated_text(
                language,
                "persistent_symptoms_warning",
            )
        )

    # -------------------------
    # 6. Upsell strategy
    # -------------------------
    best_bundle = find_best_bundle_for_recommendations(
        decision["recommended_products"],
        bundle_offers_db,
    )

    if best_bundle:

        decision["upsell_strategy"] = {
            "products": best_bundle.get("products", []),
            "offer": best_bundle,
            "message": translated_text(
                language,
                "best_offer",
            ),
        }

    elif decision["recommended_products"]:

        first_product = (
            decision["recommended_products"][0]["product"]
        )

        offer = get_best_offer(
            first_product,
            quantity_offers_db,
            bundle_offers_db,
        )

        if offer:

            decision["upsell_strategy"] = {
                "product": first_product,
                "offer": offer,
                "message": translated_text(
                    language,
                    "best_offer",
                ),
            }

    # -------------------------
    # 7. Confidence score
    # -------------------------
    confidence = 20

    if goals:
        confidence += 15

    if bmi:
        confidence += 10

    if conditions:
        confidence += 10

    if health_interests:
        confidence += 15

    if merged_profile.get("recent_checkins"):
        confidence += 15

    if merged_profile.get("recent_chat_history"):
        confidence += 5

    memory_has_useful_patterns = bool(
        merged_profile.get("past_recommended_products")
        or merged_profile.get("recurring_food_patterns")
        or merged_profile.get("recurring_activity_patterns")
        or merged_profile.get("last_detected_issue")
    )

    if memory_has_useful_patterns:
        confidence += 10

    decision["confidence_score"] = min(confidence, 95)

    return decision

def build_recommendation_agent_output(user_profile: dict):
    import time
    start_time = time.time()
    user_profile = user_profile or {}
    user_id = user_profile.get("user_id", "demo_user")

    # -------------------------------------------------------------
  
    # (none of them needs the result of another one to run), but were
    # previously executed one after another, paying the full network
    # round-trip of each call in sequence. Running them concurrently
    # in a small thread pool reduces the wall-clock time of this
    # phase to roughly that of the single slowest call instead of
    # the sum of all seven -- with the exact same inputs, outputs,
    # and downstream logic as before.
    # -------------------------------------------------------------
# Retrieve user data sequentially.
# The Supabase synchronous client is shared and should not be used
# concurrently by multiple threads.

    memory = get_user_memory(user_id) or {}
    profile = get_user_profile(user_id) or {}
    recent_checkins = get_recent_checkins(user_id, limit=14) or []

    recent_chat_history = get_recent_chat_history(
        user_id,
        days=90,
        limit=30,
    ) or []

    quantity_offers_db = get_quantity_offers_dict() or {}
    bundle_offers_db = get_bundle_offers() or []
    product_db = get_product_knowledge_dict() or {}

    recommendation_history = get_recent_recommendation_history(
        user_id,
        days=14,
        limit=20,
    ) or []

    recent_recommendations = compact_recent_recommendations(
        recommendation_history
    )


    recent_steps = [
        c.get("daily_steps", 0)
        for c in recent_checkins
        if c.get("daily_steps") is not None
    ]

    average_steps_last_7_days = (
        sum(recent_steps) / len(recent_steps)
        if recent_steps
        else None
    )
    merged_profile = {
        "user_id": user_id,
        "age": user_profile.get("age") or profile.get("age"),
        "weight": user_profile.get("weight") or profile.get("weight"),
        "height": user_profile.get("height") or profile.get("height"),
        "goals": user_profile.get("goals") or profile.get("goals", []),
        "average_steps_last_7_days": average_steps_last_7_days,
        "medical_conditions": user_profile.get("medical_conditions") or profile.get("medical_conditions", []),
        "language": normalize_language(
            profile.get("language")
            or user_profile.get("language")
            or "ar"
        ),
        "sex": user_profile.get("sex") or profile.get("sex"),
   
        "trend_analysis": memory.get("trend_analysis"),
        "health_interests": memory.get("health_interests", []),
        "past_recommended_products": memory.get("past_recommended_products", []),
        "last_recommended_product": memory.get("last_recommended_product"),
        "recurring_food_patterns": memory.get("recurring_food_patterns", []),
        "recurring_activity_patterns": memory.get("recurring_activity_patterns", []),
        "last_meal_summary": memory.get("last_meal_summary"),
        "last_activity_summary": memory.get("last_activity_summary"),
        "last_detected_issue": memory.get("last_detected_issue"),
        "consistency_score": memory.get("consistency_score"),
        "notes": memory.get("notes", []),
        "recent_checkins": recent_checkins,
        "recent_chat_history": recent_chat_history,
        "recent_recommendations_14_days": recent_recommendations,
        "recent_chat_topics": [
            {
                "question": c.get("question"),
                "intent": c.get("intent"),
                "detected_product": c.get("detected_product"),
                "recommended_product": c.get("recommended_product"),
            }
            for c in recent_chat_history
            if c.get("intent") not in ["greeting", "thanks", "small_talk", None]
        ],
        "recent_meals": [
            meal.get("description")
            for c in recent_checkins
            for meal in c.get("daily_meal_logs", [])
            if meal.get("description")
        ],
        "recent_activities": [
            activity.get("activity_type")
            for c in recent_checkins
            for activity in c.get("daily_activity_logs", [])
            if activity.get("activity_type")
        ],
        "recent_moods": [c.get("mood") for c in recent_checkins if c.get("mood")],
    }

    bmi = calculate_bmi(merged_profile.get("weight"), merged_profile.get("height"))
    merged_profile["bmi"] = bmi

    signals = consolidate_recommendation_signals(merged_profile)
    decision = build_recommendation_decision(
        signals,
        merged_profile,
        bmi,
        quantity_offers_db,
        bundle_offers_db,
        product_db=product_db,
    )
    nutrition_strategy = build_nutrition_strategy(
        merged_profile,
        signals
    )

    exercise_strategy = build_exercise_strategy(
        merged_profile,
        signals
    )
    dynamic_plan = generate_dynamic_plan_with_llm(
        merged_profile,
        signals,
        decision,
        nutrition_strategy,
        exercise_strategy
    )


    # Guard: the LLM may return null or a non-list here; the workout is
    # rebuilt by attach_exercise_videos below, so it is always shown.
    if not isinstance(dynamic_plan, dict):
        dynamic_plan = {}
    if not isinstance(dynamic_plan.get("exercise_recommendations"), list):
        dynamic_plan["exercise_recommendations"] = []

    recent_exercises = recent_recommendations.get(
        "exercise_recommendations",
        [],
    )

    generated_exercises = dynamic_plan.get(
        "exercise_recommendations",
        [],
    )

    has_duplicate_exercise = any(
        exercise_is_duplicate(
            exercise,
            recent_exercises,
        )
        for exercise in generated_exercises
    )

    if False and has_duplicate_exercise:

        today_focus = str(
            exercise_strategy["today_program"].get("focus", "")
        ).lower()

        today_activity = str(
            exercise_strategy["today_program"].get("activity", "")
        ).lower()

        if "walking" in today_focus or "walking" in today_activity:
            category_instruction = (
                "Walking must appear in main_workout. "
                "Include gentle mobility and do not replace the session "
                "with strength-focused training."
            )           
            variation_options = [
                {
                    "variation": "walking with standing mobility",
                    "required_exercises": [
                        "comfortable walking",
                        "ankle circles",
                        "gentle knee raises"
                    ]
                },
                {
                    "variation": "interval walking with joint mobility",
                    "required_exercises": [
                        "alternating easy and moderate walking",
                        "shoulder rolls",
                        "gentle hip circles"
                    ]
                },
                {
                    "variation": "indoor walking and balance",
                    "required_exercises": [
                        "walking in place",
                        "heel-to-toe walking",
                        "supported balance exercise"
                    ]
                }
            ]

        elif (
            "strength" in today_focus
            or "strength" in today_activity
        ):
            category_instruction = (
                "Use beginner strength and mobility exercises. "
                "Do not replace the session with walking-only cardio."
            )           
            variation_options = [
                {
                    "variation": "beginner full-body resistance",
                    "required_exercises": [
                        "assisted squats",
                        "wall push-ups",
                        "standing calf raises"
                    ]
                },
                {
                    "variation": "beginner resistance and mobility",
                    "required_exercises": [
                        "chair squats",
                        "light resistance rows",
                        "gentle hip mobility"
                    ]
                },
                {
                    "variation": "beginner strength and balance",
                    "required_exercises": [
                        "supported reverse lunges",
                        "wall presses",
                        "supported balance holds"
                    ]
                }
            ]

        else:
            category_instruction = (
                "Use gentle general-wellness movement consistent with "
                "the selected focus and activity."
            )
            variation_options = [
                {
                    "variation": "gentle mobility",
                    "required_exercises": [
                        "shoulder rolls",
                        "gentle torso rotations",
                        "ankle circles"
                    ]
                },
                {
                    "variation": "wellness movement and balance",
                    "required_exercises": [
                        "walking in place",
                        "supported balance holds",
                        "gentle side stretches"
                    ]
                },
                {
                    "variation": "light full-body movement",
                    "required_exercises": [
                        "gentle knee raises",
                        "arm circles",
                        "standing side steps"
                    ]
                }
            ]

        variation_index = (
            len(recent_exercises) % len(variation_options)
        )
        selected_variation = variation_options[variation_index]
        retry_plan = generate_dynamic_plan_with_llm(
            merged_profile,
            signals,
            decision,
            nutrition_strategy,
            exercise_strategy,
            additional_instruction=f"""
            Mandatory new variation:
            {json.dumps(selected_variation, ensure_ascii=False)}

            Recent exercises that must not be repeated:
            {json.dumps(recent_exercises, ensure_ascii=False)}
            The exercise generated in the previous attempt duplicated an exercise
            from the user's recent 14-day history.

            Generate a genuinely different exercise session, but strictly preserve
            the deterministic exercise strategy.

            Required focus:
            {exercise_strategy["today_program"].get("focus")}

            Required activity:
            {exercise_strategy["today_program"].get("activity")}

            Required duration:
            {exercise_strategy["today_program"].get("duration")}

            Required intensity:
            {exercise_strategy["today_program"].get("intensity")}

            Use different exercises from the recent history while remaining inside
            the required activity category.

            Category-specific requirement:
            {category_instruction}
            """
        )

        retry_exercises = retry_plan.get(
            "exercise_recommendations",
            [],
        )

        retry_has_duplicate = any(
            exercise_is_duplicate(
                exercise,
                recent_exercises,
            )
            for exercise in retry_exercises
        )

        if retry_exercises and not retry_has_duplicate:
            dynamic_plan["exercise_recommendations"] = (
                retry_exercises
            )
        else:
            print(
                "[RECOMMENDATION] Exercise remained duplicated "
                "after one retry."
            )
    
    dynamic_plan = attach_exercise_videos(
        plan=dynamic_plan,
        sex=merged_profile.get("sex"),
        merged_profile=merged_profile,
        exercise_strategy=exercise_strategy,
    )
    output = {
        "profile_summary": {
            "goals": merged_profile.get("goals"),
            "weight": merged_profile.get("weight"),
            "height": merged_profile.get("height"),
            "bmi": bmi,
            "age": merged_profile.get("age"),
            "medical_conditions": merged_profile.get("medical_conditions"),
            "sex": merged_profile.get("sex"),
            "average_steps_last_7_days": average_steps_last_7_days,
            "activity_level": signals.get("activity_level", "unknown"),
            "health_interests": signals.get("health_interests", []),
            "food_patterns": signals.get("food_patterns", []),
            "past_recommended_products": merged_profile.get("past_recommended_products", []),
            "last_recommended_product": merged_profile.get("last_recommended_product"),
            "last_meal_summary": merged_profile.get("last_meal_summary"),
            "last_activity_summary": merged_profile.get("last_activity_summary"),
            "last_detected_issue": merged_profile.get("last_detected_issue"),
            "consistency_score": merged_profile.get("consistency_score"),
            "recent_checkins_count": len(recent_checkins),
            "recent_meals": merged_profile.get("recent_meals"),
            "recent_activities": merged_profile.get("recent_activities"),
            "recent_chat_count": len(recent_chat_history),
            "recent_chat_topics": merged_profile.get("recent_chat_topics"),
        },

        "priority_focus": decision["priority_focus"],
        "recommended_products": decision["recommended_products"],

        "meal_recommendations": dynamic_plan.get("meal_recommendations", []),
        "exercise_recommendations": dynamic_plan.get("exercise_recommendations", []),
        "daily_actions": list({
            (
                item.get("action", ""),
                item.get("reason", ""),
            ): item
            for item in (
                decision.get("daily_actions", [])
                + dynamic_plan.get("daily_actions", [])
            )
        }.values()),
        "behavioral_insight": dynamic_plan.get("behavioral_insight", ""),
        "motivation_message": dynamic_plan.get("motivation_message", ""),
        "warnings": dynamic_plan.get("warnings", []) + decision.get("warnings", []),

        "upsell_strategy": decision["upsell_strategy"],
        "confidence_score": decision["confidence_score"],

        "reasoning_summary": (
            dynamic_plan.get("behavioral_insight")
            or translated_text(
                merged_profile.get("language", "ar"),
                "fallback_reasoning"
            )
        ),

        "llm_signals": signals,
        "decision_layer": decision
    }


    response_time = round(time.time() - start_time, 3)

    log_recommendation(user_id, {
        "recommended_products": [p.get("product") for p in output.get("recommended_products", [])],
        "meal_recommendations": output.get("meal_recommendations", []),
        "exercise_recommendations": output.get("exercise_recommendations", []),
        "reasoning_summary": output.get("reasoning_summary"),

        "used_memory": bool(memory.get("health_interests") or memory.get("past_recommended_products")),
        "used_goal": bool(merged_profile.get("goals")),
        "used_activity": (
            len(recent_checkins) > 0
        ),
        "used_bmi": bool(bmi),
        "used_daily_checkin": len(recent_checkins) > 0,
        "response_time_sec": response_time,
    })
    output["warnings"] = list(dict.fromkeys(output.get("warnings", [])))
    return output
