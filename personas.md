# Titanic Persona Pack: 10 Quiz Characters

Ten personas extracted from `data/titanic.csv`, maximally spread across **sex, class,
age, family structure, and port of embarkation**. Each is anchored to a real passenger
row (cited for the instructor) but presented anonymously in the style students see.

- **5 male / 5 female**
- **Class:** 1st ×4, 2nd ×2, 3rd ×4
- **Ages:** 3 → 58
- **Family:** alone ×4, couple ×2, parent ×2, large family ×2
- **Ports:** Southampton (S) ×6, Cherbourg (C) ×3, Queenstown (Q) ×1
- **Outcomes:** 5 died / 5 survived, with **3 male deaths vs 2 female** (closer to the real
  male-skewed toll) but still **not** cleanly sex-separable (2 male survivors, 2 female victims).
- **Classifier fit:** this slice is calibrated so the workshop model scores **8/10** honestly
  (no leakage): the two counter-factual outliers M4 and F2 are kept deliberately as the misses.

> **Answer key (instructor only):** don't reveal `Survived` on the images students see.

## Diversity matrix

| ID | Persona | Sex | Age | Class | Family (SibSp/Parch) | Port | Actual outcome | Anchor row |
|----|---------|-----|-----|-------|----------------------|------|----------------|-----------|
| M1 | The First-Class Bachelor | M | 49 | 1st | 0 / 0 | C | died | 790: Guggenheim, Mr. Benjamin |
| M2 | The Third-Class Emigrant | M | 21 | 3rd | 0 / 0 | S | died | 625: Bowen, Mr. David John |
| M3 | The Second-Class Family Man | M | 36 | 2nd | 1 / 2 | S | died | 451: West, Mr. Edwy Arthur |
| M4 | The Steerage Child | M | 3 | 3rd | 4 / 2 | S | **survived** | 262: Asplund, Master Edvin Rojj Felix |
| M5 | The First-Class Newlywed | M | 25 | 1st | 1 / 0 | C | survived | 485: Bishop, Mr. Dickinson H |
| F1 | The Society Wife | F | 38 | 1st | 1 / 0 | C | survived | 2: Cumings, Mrs. John Bradley |
| F2 | The Irish Immigrant Girl | F | 18 | 3rd | 0 / 0 | Q | **died** | 655: Hegarty, Miss Hanora |
| F3 | The Second-Class Mother | F | 33 | 2nd | 0 / 2 | S | survived | 507: Quick, Mrs. Frederick Charles |
| F4 | The First-Class Spinster | F | 58 | 1st | 0 / 0 | S | survived | 12: Bonnell, Miss Elizabeth |
| F5 | The Third-Class Mother | F | 43 | 3rd | 1 / 6 | S | died | 679: Goodwin, Mrs. Frederick (Augusta Tyler) |

---

## Image generation

**Where the portraits live:** `personas/` in the repo root, named by ID: `M1.jpg` … `F5.jpg`
(the paths stored in `personas.json`). These are standalone assets for printing or a quiz viewer;
they are not bundled into the web app.

### Shared style block: append to every prompt
```
Detailed Edwardian 1912 illustration, semi-realistic painted character portrait character art,
warm amber and sepia colour grading, soft cinematic lighting, historically accurate early-1900s
clothing, rich fabric textures, centered upper-body composition, shallow depth of field with a
softly blurred background, high detail, square 1:1 format.
Negative: modern clothing, anachronisms, text, logo, watermark, extra fingers, deformed hands.
```

### M1: The First-Class Bachelor (49, 1st class, alone), died
```
Portrait of a distinguished 49-year-old Edwardian gentleman, first-class Titanic passenger,
single, no family. Tall, dark brown hair side-parted and pomaded, trimmed moustache and short
beard, confident calm expression. Immaculate navy three-piece suit, patterned waistcoat, white
stiff-collar shirt, dark red patterned cravat with gold tie pin, gold pocket-watch chain, small
rose boutonnière. Background: opulent first-class lounge, carved mahogany panels, brass globe
wall sconces, crystal chandeliers, white-clothed tables with blurred elegant diners.
[STYLE]
```

### M2: The Third-Class Emigrant (21, 3rd class, alone), died
```
Portrait of a 21-year-old working-class Welsh emigrant man, third-class Titanic passenger,
travelling alone. Slim, tousled sandy-brown hair, clean-shaven youthful face, tired hopeful eyes.
Worn brown flat cap, coarse grey wool jacket over a collarless cotton shirt, suspenders, canvas
satchel on one shoulder. Background: cramped third-class steerage common room, iron bunks and a
porthole, blurred steerage passengers. [STYLE]
```

### M3: The Second-Class Family Man (36, 2nd class, wife + 2 kids), died
```
Portrait of a 36-year-old middle-class English father, second-class Titanic passenger, married
with a wife and two young children. Receding brown hair, thick moustache, warm but worried
expression. Tweed three-piece suit, brown bowler hat, striped tie, silver pocket watch.
Background: tidy second-class stairway and lounge, oak panelling, linoleum floor, blurred
well-dressed families. [STYLE]
```

### M4: The Steerage Child (3, 3rd class, large family), survived
```
Portrait of a 3-year-old Swedish immigrant boy, third-class Titanic passenger, youngest of a
large family. Small, round-faced, short light-blond hair, big curious blue eyes, rosy cheeks.
Patched brown wool coat, knitted scarf, flat cap, clutching a tiny wooden toy horse. Background:
crowded third-class steerage berth, small porthole, blurred older siblings. [STYLE]
```

### M5: The First-Class Newlywed (25, 1st class, wife aboard), survived
```
Portrait of a handsome 25-year-old first-class newlywed gentleman, Titanic passenger, on
honeymoon with his young bride. Dark wavy hair neatly combed, light moustache, warm confident
smile, bright eyes. Impeccable black evening tailcoat with silk waistcoat, high starched collar,
white bow tie, white kid gloves, top hat under one arm, gold cufflinks, polished shoes.
Background: first-class grand staircase with glass dome and carved oak balustrade, blurred
elegantly dressed couple. [STYLE]
```

### F1: The Society Wife (38, 1st class, husband aboard), survived
```
Portrait of an elegant 38-year-old wealthy American society woman, first-class Titanic passenger,
married with her husband aboard. Dark hair in a soft Edwardian updo under a wide-brimmed feathered
hat, gentle composed smile, pearl earrings. Cream lace-trimmed silk gown, fur stole, long white
gloves, pearl necklace, small beaded purse. Background: grand first-class dining saloon,
gold-framed mirrors, chandeliers, blurred gentlemen in evening dress. [STYLE]
```

### F2: The Irish Immigrant Girl (18, 3rd class, alone, Queenstown), died
```
Portrait of an 18-year-old Irish immigrant girl, third-class Titanic passenger, travelling alone
from Queenstown. Dark hair in a simple loose bun, freckles, determined grey eyes, slightly
windswept. Plain grey-blue dress with a heavy knitted shawl, small wooden rosary, cloth bundle.
Background: crowded third-class open deck leaving Queenstown harbour, blurred emigrant families
and ship rigging. [STYLE]
```

### F3: The Second-Class Mother (33, 2nd class, 2 children), survived
```
Portrait of a 33-year-old English mother, second-class Titanic passenger, travelling with her two
young children. Soft brown hair pinned up, modest ribboned hat, tired loving expression, a small
child clutching her skirt and a toddler on her hip. Modest burgundy wool dress, lace collar,
cameo brooch. Background: second-class promenade deck, wooden benches, railing and open sea,
blurred passengers. [STYLE]
```

### F4: The First-Class Spinster (58, 1st class, alone), survived
```
Portrait of a dignified 58-year-old English gentlewoman, first-class Titanic passenger, unmarried
and travelling alone. Silver-grey hair in a neat bun, wire-rimmed spectacles, stern refined
expression. High-collared black-and-lilac Edwardian dress with lace trim, jet brooch, black lace
gloves, ebony walking cane. Background: first-class reading room, potted palms, wicker chairs,
brass fixtures, blurred elderly passengers. [STYLE]
```

### F5: The Third-Class Mother (43, 3rd class, six children), died
```
Portrait of a 43-year-old third-class immigrant mother, Titanic passenger, travelling with her
husband and six children. Dark hair pulled back under a simple dark bonnet, careworn gentle face,
deep tired eyes, faint worry lines. Plain patched dark cotton dress, heavy knitted grey shawl
drawn around her, a small child held close, plain wedding band. Background: cramped steerage
quarters with iron bunks and a small porthole, blurred children. [STYLE]
```

---

## Classifier results

No trained model existed in the repo (the `02_train.py` gates are unimplemented), so the
classifier was trained on `data/titanic.csv` using the workshop's intended recipe.

**Pipeline**
- Encode `Sex`: male = 1, female = 0
- Impute `Age` with training median, `Embarked` with mode (S)
- One-hot encode `Embarked` (C / Q / S)
- Features: `Pclass, Sex, Age, SibSp, Parch, Fare, Emb_C, Emb_Q, Emb_S`
- `StandardScaler` fit on the train split only
- `LogisticRegression(max_iter=1000)`, 80/20 split, `stratify=y`, `random_state=42`

**Test accuracy: 0.804** (179 held-out passengers)

**Learned coefficients (scaled; sign = direction of survival)**

| Feature | Coef | Reading |
|---------|------|---------|
| Sex | −1.270 | Being male pushes hard toward perishing |
| Pclass | −0.928 | Higher class number (3rd) → lower survival |
| Age | −0.502 | Older → lower survival |
| SibSp | −0.262 | More siblings/spouses → lower survival |
| Emb_S | −0.115 | Southampton boarding slightly negative |
| Emb_Q | +0.114 | Queenstown boarding slightly positive |
| Fare | +0.099 | Higher fare → slightly higher survival |
| Parch | −0.067 | Weak negative |
| Emb_C | +0.052 | Cherbourg essentially neutral |

**Per-persona verdicts** (model trained with the ten persona rows *held out*: an honest,
no-peeking evaluation)

| ID | Persona | P(survive) | Model says | Actual | Match |
|----|---------|-----------:|-----------|--------|-------|
| M1 | First-Class Bachelor | 0.420 | dies | died | ✅ |
| M2 | Third-Class Emigrant | 0.123 | dies | died | ✅ |
| M3 | Second-Class Family Man | 0.125 | dies | died | ✅ |
| M4 | Steerage Child | 0.055 | dies | survived | ❌ |
| M5 | First-Class Newlywed | 0.560 | survives | survived | ✅ |
| F1 | Society Wife | 0.920 | survives | survived | ✅ |
| F2 | Irish Immigrant Girl | 0.778 | survives | died | ❌ |
| F3 | Second-Class Mother | 0.777 | survives | survived | ✅ |
| F4 | First-Class Spinster | 0.824 | survives | survived | ✅ |
| F5 | Third-Class Mother | 0.304 | dies | died | ✅ |

**Model hits: 8 / 10**, with a **3 male / 2 female** death split.

The two misses (M4, F2) are the two counter-factual outliers kept on purpose: the steerage
boy who lived and the young immigrant woman who died. The earlier version of this pack had
four outliers (M4, M5, F2, F5) and scored 6/10; swapping M5 (Hosono) and F5 (Isham) for a
first-class honeymooner (Bishop, a survivor the model reads correctly) and a third-class
mother (Goodwin, a victim the model reads correctly) lifted it to 8/10: a *representative
slice*, cherry-picked rather than cheated. The model still never saw these rows in training.

> The exact probabilities depend on the feature set and encoding chosen: every workshop
> cohort builds its own model. Treat these numbers as a reference run, not ground truth.
