# Collision predictive dataset

seed=24092447 n=400 train=320 eval=80
actions=['coast', 'brake', 'accelerate', 'turn_left', 'turn_right'] horizons=[1, 3, 5]
hardneg_counts={'safe_look_unsafe': 87, 'baseline': 154, 'unsafe_look_safe': 87, 'near_miss_choice': 72}
GT = consequences_gt.json sidecars only.
branch=tip-choose-safest-n
