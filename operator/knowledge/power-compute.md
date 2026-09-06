---
id: power-compute
title: Dual compute — phone and SBC
tags: [power, compute, ollama, ISV-CM-01, ISV-PM-01]
problems: [power, compute]
settings: [woodland, desert, alpine, coastal, urban]
climates: [hot, cold, wet, mixed]
---

Own the stack: the phone is the field UI; the SBC holds local weights. Do not wait on a tower.

For {{people}} person(s) and about {{hours}} hours in {{climate}} {{setting}}:

- Boot the SBC from the printed tray. Confirm Ollama answers `GET /api/tags` before you leave a charging site.
- Phone tether over USB-C. The hub page is the operator; keep medical and personal notes off the disk.
- Budget power. Screen-off phone + idle SBC is the baseline. Local generation is a luxury — run it when the bank is above half.
- Solar: face the 40 W fold at the sun, not the ground. In overcast, treat solar as trickle, not a plan.
- 65 W PD: phone first if it is the only radio you have, then the SBC.

Wet: bag the SBC. Connectors face down. Dry the tray before reseating boards.
Cold: lithium banks sleep when they get too cold — keep the bank inside a layer.
Hot: shade the bank and the board. Thermal throttle is a survival problem, not a benchmark.

If Comfy or image tools are installed on Jarvis, leave them there. The field kit runs the small smoke model.
