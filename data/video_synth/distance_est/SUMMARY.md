# Distance estimation — synthetic set SUMMARY

- **Scale lock:** FLOOR-SCALE (building floors 2.4–3.0 m) — **NO fixed object heights**
- Lights true height varies **3–5 m** by intersection (derive via floor-span)
- Priority distances: cars, intersections, stop signs, pedestrians (+ lights)
- **Family:** video_synth temporal — NOT inverse_planning corridor
- sequences: **56** × 12 frames
- split: train **45** / eval **11**
- bands: [5.0, 50.0, 100.0, 200.0] m (jittered)
- Adapter: `data/lora_adapter_distance/` (never `data/lora_adapter/`)
- GT: `distances_gt.json` sidecar only

## Priority-class band counts

| band | count |
|------|-------|
| ~5m | 2818 |
| ~50m | 2781 |
| ~100m | 2671 |
| ~200m | 1342 |

| seq | street | frames | objs | bands_t0 | buildings |
|-----|--------|--------|------|----------|-----------|
| `de_000_oak_ave` | Oak Ave | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.632m,bld_1:5fl@2.439m |
| `de_001_pine_st` | Pine St | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.753m,bld_1:3fl@2.507m |
| `de_002_maple_blvd` | Maple Blvd | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.688m,bld_1:7fl@2.448m |
| `de_003_cedar_rd` | Cedar Rd | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.772m,bld_1:3fl@2.651m |
| `de_004_elm_way` | Elm Way | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.902m,bld_1:8fl@2.919m |
| `de_005_birch_ln` | Birch Ln | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.633m,bld_1:5fl@2.755m |
| `de_006_willow_dr` | Willow Dr | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.799m,bld_1:3fl@2.657m |
| `de_007_ash_ct` | Ash Ct | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.505m,bld_1:4fl@2.427m |
| `de_008_oak_ave` | Oak Ave | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.643m,bld_1:5fl@2.532m |
| `de_009_pine_st` | Pine St | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.95m,bld_1:3fl@2.614m |
| `de_010_maple_blvd` | Maple Blvd | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:5fl@2.663m,bld_1:4fl@2.817m |
| `de_011_cedar_rd` | Cedar Rd | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.738m,bld_1:4fl@2.534m |
| `de_012_elm_way` | Elm Way | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.414m,bld_1:6fl@2.737m |
| `de_013_birch_ln` | Birch Ln | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.782m,bld_1:6fl@2.647m |
| `de_014_willow_dr` | Willow Dr | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.618m,bld_1:8fl@2.483m |
| `de_015_ash_ct` | Ash Ct | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.471m,bld_1:6fl@2.432m |
| `de_016_oak_ave` | Oak Ave | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.487m,bld_1:6fl@2.9m |
| `de_017_pine_st` | Pine St | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.593m,bld_1:4fl@2.432m |
| `de_018_maple_blvd` | Maple Blvd | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.792m,bld_1:7fl@2.529m |
| `de_019_cedar_rd` | Cedar Rd | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.781m,bld_1:4fl@2.912m |
| `de_020_elm_way` | Elm Way | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.55m,bld_1:3fl@2.804m |
| `de_021_birch_ln` | Birch Ln | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.41m,bld_1:7fl@2.75m |
| `de_022_willow_dr` | Willow Dr | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.448m,bld_1:8fl@2.835m |
| `de_023_ash_ct` | Ash Ct | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.909m,bld_1:7fl@2.619m |
| `de_024_oak_ave` | Oak Ave | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.904m,bld_1:5fl@2.61m |
| `de_025_pine_st` | Pine St | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.441m,bld_1:7fl@2.901m |
| `de_026_maple_blvd` | Maple Blvd | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.594m,bld_1:8fl@2.906m |
| `de_027_cedar_rd` | Cedar Rd | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:5fl@2.441m,bld_1:4fl@2.912m |
| `de_028_elm_way` | Elm Way | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.961m,bld_1:4fl@2.98m |
| `de_029_birch_ln` | Birch Ln | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.769m,bld_1:5fl@2.424m |
| `de_030_willow_dr` | Willow Dr | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.971m,bld_1:8fl@2.509m |
| `de_031_ash_ct` | Ash Ct | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.683m,bld_1:4fl@2.767m |
| `de_032_oak_ave` | Oak Ave | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.45m,bld_1:7fl@2.855m |
| `de_033_pine_st` | Pine St | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.914m,bld_1:5fl@2.985m |
| `de_034_maple_blvd` | Maple Blvd | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.446m,bld_1:3fl@2.826m |
| `de_035_cedar_rd` | Cedar Rd | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.624m,bld_1:3fl@2.973m |
| `de_036_elm_way` | Elm Way | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.465m,bld_1:8fl@2.644m |
| `de_037_birch_ln` | Birch Ln | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.762m,bld_1:6fl@2.531m |
| `de_038_willow_dr` | Willow Dr | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.54m,bld_1:6fl@2.445m |
| `de_039_ash_ct` | Ash Ct | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.898m,bld_1:4fl@2.816m |
| `de_040_oak_ave` | Oak Ave | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.629m,bld_1:3fl@2.529m |
| `de_041_pine_st` | Pine St | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.575m,bld_1:5fl@2.436m |
| `de_042_maple_blvd` | Maple Blvd | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.51m,bld_1:6fl@2.959m |
| `de_043_cedar_rd` | Cedar Rd | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.698m,bld_1:6fl@2.886m |
| `de_044_elm_way` | Elm Way | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.839m,bld_1:6fl@2.882m |
| `de_045_birch_ln` | Birch Ln | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.555m,bld_1:5fl@2.921m |
| `de_046_willow_dr` | Willow Dr | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.448m,bld_1:5fl@2.884m |
| `de_047_ash_ct` | Ash Ct | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.669m,bld_1:3fl@2.993m |
| `de_048_oak_ave` | Oak Ave | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:5fl@2.712m,bld_1:5fl@2.706m |
| `de_049_pine_st` | Pine St | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:3fl@2.667m,bld_1:3fl@2.539m |
| `de_050_maple_blvd` | Maple Blvd | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:6fl@2.873m,bld_1:7fl@2.552m |
| `de_051_cedar_rd` | Cedar Rd | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:8fl@2.645m,bld_1:4fl@2.624m |
| `de_052_elm_way` | Elm Way | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.539m,bld_1:7fl@2.688m |
| `de_053_birch_ln` | Birch Ln | 12 | 18 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.903m,bld_1:5fl@2.497m |
| `de_054_willow_dr` | Willow Dr | 12 | 14 | ~100m,~200m,~50m,~5m | bld_0:4fl@2.423m,bld_1:8fl@2.638m |
| `de_055_ash_ct` | Ash Ct | 12 | 17 | ~100m,~200m,~50m,~5m | bld_0:7fl@2.788m,bld_1:4fl@2.653m |
