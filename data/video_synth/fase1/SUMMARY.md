# Fase 1 video_synth SUMMARY

- **Layout:** ONE street · THREE traffic lights in a line
- sequences: **50** × 16 frames
- GT: objects, trajectories, light R/Y/G timelines, relations, motion prediction, reference summary
- Adapter target: `data/lora_adapter_video_f1/` (never `data/lora_adapter/`)

| seq | street | frames | cars | peds | density | near_miss |
|-----|--------|--------|------|------|---------|-----------|
| `f1_000_oak_ave` | Oak Ave | 16 | 3 | 2 | low | False |
| `f1_001_pine_st` | Pine St | 16 | 5 | 3 | med | False |
| `f1_002_maple_blvd` | Maple Blvd | 16 | 7 | 4 | high | False |
| `f1_003_cedar_rd` | Cedar Rd | 16 | 3 | 2 | low | False |
| `f1_004_elm_way` | Elm Way | 16 | 5 | 3 | med | False |
| `f1_005_birch_ln` | Birch Ln | 16 | 7 | 4 | high | False |
| `f1_006_willow_dr` | Willow Dr | 16 | 3 | 2 | low | False |
| `f1_007_ash_ct` | Ash Ct | 16 | 5 | 3 | med | True |
| `f1_008_oak_ave` | Oak Ave | 16 | 7 | 4 | high | False |
| `f1_009_pine_st` | Pine St | 16 | 3 | 2 | low | False |
| `f1_010_maple_blvd` | Maple Blvd | 16 | 5 | 3 | med | False |
| `f1_011_cedar_rd` | Cedar Rd | 16 | 7 | 4 | high | False |
| `f1_012_elm_way` | Elm Way | 16 | 3 | 2 | low | False |
| `f1_013_birch_ln` | Birch Ln | 16 | 5 | 3 | med | False |
| `f1_014_willow_dr` | Willow Dr | 16 | 7 | 4 | high | False |
| `f1_015_ash_ct` | Ash Ct | 16 | 3 | 2 | low | False |
| `f1_016_oak_ave` | Oak Ave | 16 | 5 | 3 | med | False |
| `f1_017_pine_st` | Pine St | 16 | 7 | 4 | high | True |
| `f1_018_maple_blvd` | Maple Blvd | 16 | 3 | 2 | low | False |
| `f1_019_cedar_rd` | Cedar Rd | 16 | 5 | 3 | med | False |
| `f1_020_elm_way` | Elm Way | 16 | 7 | 4 | high | False |
| `f1_021_birch_ln` | Birch Ln | 16 | 3 | 2 | low | False |
| `f1_022_willow_dr` | Willow Dr | 16 | 5 | 3 | med | False |
| `f1_023_ash_ct` | Ash Ct | 16 | 7 | 4 | high | False |
| `f1_024_oak_ave` | Oak Ave | 16 | 3 | 2 | low | False |
| `f1_025_pine_st` | Pine St | 16 | 5 | 3 | med | False |
| `f1_026_maple_blvd` | Maple Blvd | 16 | 7 | 4 | high | False |
| `f1_027_cedar_rd` | Cedar Rd | 16 | 3 | 2 | low | True |
| `f1_028_elm_way` | Elm Way | 16 | 5 | 3 | med | False |
| `f1_029_birch_ln` | Birch Ln | 16 | 7 | 4 | high | False |
| `f1_030_willow_dr` | Willow Dr | 16 | 3 | 2 | low | False |
| `f1_031_ash_ct` | Ash Ct | 16 | 5 | 3 | med | False |
| `f1_032_oak_ave` | Oak Ave | 16 | 7 | 4 | high | False |
| `f1_033_pine_st` | Pine St | 16 | 3 | 2 | low | False |
| `f1_034_maple_blvd` | Maple Blvd | 16 | 5 | 3 | med | False |
| `f1_035_cedar_rd` | Cedar Rd | 16 | 7 | 4 | high | False |
| `f1_036_elm_way` | Elm Way | 16 | 3 | 2 | low | False |
| `f1_037_birch_ln` | Birch Ln | 16 | 5 | 3 | med | True |
| `f1_038_willow_dr` | Willow Dr | 16 | 7 | 4 | high | False |
| `f1_039_ash_ct` | Ash Ct | 16 | 3 | 2 | low | False |
| `f1_040_oak_ave` | Oak Ave | 16 | 5 | 3 | med | False |
| `f1_041_pine_st` | Pine St | 16 | 7 | 4 | high | False |
| `f1_042_maple_blvd` | Maple Blvd | 16 | 3 | 2 | low | False |
| `f1_043_cedar_rd` | Cedar Rd | 16 | 5 | 3 | med | False |
| `f1_044_elm_way` | Elm Way | 16 | 7 | 4 | high | False |
| `f1_045_birch_ln` | Birch Ln | 16 | 3 | 2 | low | False |
| `f1_046_willow_dr` | Willow Dr | 16 | 5 | 3 | med | False |
| `f1_047_ash_ct` | Ash Ct | 16 | 7 | 4 | high | True |
| `f1_048_oak_ave` | Oak Ave | 16 | 3 | 2 | low | False |
| `f1_049_pine_st` | Pine St | 16 | 5 | 3 | med | False |
