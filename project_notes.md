# CASA0025 Group Project Notes
## The Local Earth Authority — London Thermal Exposure & Shelter Access

**Deadline:** 28 April 2026  
**Assessment weight:** 70% of the module  
**Repo:** `CASA0025_The_Local_Earth_Authority_Group_Project-main`  
**Website stack:** Quarto website, rendered to `/docs`, deployed via GitHub Pages

---

## 1. What We Are Building

An interactive Google Earth Engine application that maps **thermal vulnerability** across London. The core idea is to find where people are most exposed to dangerous heat in summer and dangerous cold in winter, and then overlay where public shelters (cool spaces and warm spaces) are or are not present, combined with demographic vulnerability from ONS census data.

The output is a GEE web app embedded in a Quarto website (same structure as the Nepal Landslides example project).

---

## 2. Project Summary (agreed wording from `index.qmd`)

> This project aims to identify spatial inequalities in thermal exposure across London by mapping areas that experience the highest temperatures during heat events and the lowest temperatures during cold periods. These environmental patterns are analysed alongside the distribution of publicly accessible shelters (cool spaces and warm spaces) and demographic vulnerability indicators derived from census data.
>
> By integrating climate, accessibility, and socio-demographic data, the project highlights where vulnerable populations may be disproportionately exposed to extreme temperatures and where gaps in shelter provision exist.

---

## 3. Problem Statement (needs writing)

Key points to include:
- London has no statutory minimum or maximum indoor temperature requirement — the policy gap is real.
- Studies on cold risk are far fewer than those on heat (noted in team chat).
- Most cooling/warming space research focuses on indoor temperatures and fuel poverty, not spatial access.
- Relevant legislation to cite: **Health & Social Care Act 2012**, **Climate Change Act 2008**.
- Key references already gathered:
  - [BBC article on London heat](https://www.bbc.co.uk/news/uk-england-london-67579161)
  - [GLA heat vulnerability report Jan 2024](https://www.london.gov.uk/sites/default/files/2024-01/24-01-16%20GLA%20Properties%20Vulnerable%20to%20Heat%20Impacts%20in%20London.pdf)
  - [KCL Londoners experiences of heat Mar 2026](https://www.kcl.ac.uk/sfg/assets/londoners-experiences-of-heat-and-priorities-for-action.pdf)
  - [Tandfonline paper Oct 2024](https://www.tandfonline.com/doi/full/10.1080/23748834.2025.2489854)
  - [Lambeth cooling spaces Oct 2025](https://lambethclimatepartnership.org/live-project/cooling-fiveways)

---

## 4. End User (needs writing)

Target audiences to define clearly for the mark scheme:
- **London Borough officers** responsible for public health or climate resilience planning (e.g. deciding where to open new cooling rooms).
- **GLA analysts** monitoring compliance with heat action plans.
- **Voluntary and community organisations** distributing cooling or warming pack resources.
- **Academic researchers** studying urban heat islands and social vulnerability.

The application must not just look good — the mark scheme explicitly asks: *"Who is the intended end-user?"* and *"How effectively does the application leverage geospatial data to solve this problem?"* You need a clear answer for the presentation too.

---

## 5. Data Sources

### Already decided and partially in `index.qmd`

| Dataset | What we calculate | Bands / fields | GEE / Source link |
|---|---|---|---|
| **Landsat 8** (Collection 2, Tier 1, Level 2) | Mean Land Surface Temperature (LST) — summer & winter | Band 10 (thermal) | [GEE catalogue](https://developers.google.com/earth-engine/datasets/catalog/landsat-8) |
| Landsat 8 | NDVI | B5 (NIR) & B4 (Red) | Same |
| Landsat 8 | NDBI | B6 (SWIR1) & B5 (NIR) | Same |
| **ONS Census 2021** | % young (0-19) and % old (65+) per Output Area | Age by 5-year age bands | [ONS link](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/adhocs/15432ts007acensus2021agebyfiveyearagebands) |

### Additional data sources to add

| Dataset | Purpose | Source |
|---|---|---|
| **Warm Welcome / Warm Banks** | Warm space locations (winter) | [warmwelcome.uk/find-a-space](https://www.warmwelcome.uk/find-a-space) |
| **GLA Cool Spaces** | Cool space locations (summer) | [apps.london.gov.uk/cool-spaces](https://apps.london.gov.uk/cool-spaces/) |
| London Borough boundaries | Aggregation geography | GADM / GEE `FAO/GAUL` or upload shapefile |
| LSOA / OA boundaries | Granular spatial unit | Upload from ONS / geoportal.statistics.gov.uk |

---

## 6. Methodology

### 6.1 Heat Vulnerability Index (HVI) — Summer

**Step 1: Pre-process Landsat 8**
- Filter to summer months (June-August) for multiple years (suggest 2017-2023 to avoid cloud issues).
- Apply cloud masking using `QA_PIXEL` band.
- Take median composite.

**Step 2: Calculate LST**
Landsat Collection 2 Level-2 provides `ST_B10` already as surface temperature in Kelvin. Convert to Celsius:
```javascript
var lst = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15);
```

**Step 3: Calculate NDVI and NDBI**
```javascript
var ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
var ndbi = image.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
```

**Step 4: Build composite heat exposure score**
- Normalise LST, NDVI (inverted — low veg = high risk), NDBI to 0-1.
- Combine into a weighted score (weights to be agreed by group).

### 6.2 Cold Vulnerability Index — Winter

Repeat the same approach but:
- Filter to winter months (December-February).
- Lower LST in winter = higher exposure/risk.
- NDBI still relevant (built-up surfaces retain less heat at night).

### 6.3 Demographic Vulnerability Layer

From ONS Census OA data:
- % aged 0-19 and % aged 65+ are the two flags we have.
- Consider also adding a deprivation index (e.g. Index of Multiple Deprivation, IMD) as an additional layer — this is available per LSOA and can be uploaded to GEE as a FeatureCollection asset.

**Composite vulnerability score per OA/LSOA:**
```
vulnerability = (norm_pct_young + norm_pct_old + norm_deprivation) / 3
```
(or weighted)

### 6.4 Shelter Access Gap

- Upload cool space and warm space point data as GEE FeatureCollection assets.
- Calculate distance from each OA centroid to nearest shelter (using `ee.Geometry.distance` or `fastDistanceTransform`).
- Areas with high thermal risk + high vulnerability + high distance to nearest shelter = worst-case areas, the ones the application should highlight.

### 6.5 Final Combined Index

A combined index per OA/LSOA that flags areas where all three conditions coincide:
- High LST (summer) or low LST (winter)
- High demographic vulnerability
- Poor shelter access

The team chat mentions a **pie chart of LSOAs at different risk levels per borough** and a **borough search tool**, which implies the final output should aggregate to borough level for the UI but allow exploration at LSOA level.

---

## 7. Interface Design (from team chat)

The team has already discussed UI elements. The Nepal project gives a strong template. Suggested UI features:

| Feature | Detail |
|---|---|
| **Borough search tool** | Dropdown or text search, zooms and returns stats for that borough |
| **Pie chart of LSOAs at different risk levels per borough** | Triggered on borough selection |
| **Heat / cold toggle or slider** | Switch between the summer heat view and winter cold view |
| **Layer toggle panel** | Toggle between: LST map, demographic vulnerability, shelter locations, combined risk |
| **Click popup on shelter points** | Shows shelter name, type (cool/warm), opening hours if available |
| **Draw polygon / rectangle** | User draws their own AOI and gets summary stats back |
| **Legend** | Colour scale for risk, icons for shelters |

### Reference UI to draw from:
- [Tree Equity Score UK](https://uk.treeequityscore.org/map) — mentioned in team chat as a design reference.
- Nepal app split-panel for comparing models.
- Ship Detection app (W10) for the control panel + chart pattern.

---

## 8. Quarto Website Structure

The repo uses the same template structure as the Nepal example. Current `_quarto.yml` is set up as a book (not a website) — the Nepal example uses `website` type. This needs correcting.

### Recommended sections for `index.qmd` (modelled on Nepal example)

1. **Project Summary** (draft exists)
2. **Problem Statement** (empty — needs writing)
3. **End User** (empty — needs writing)
4. **Data** (partially done, needs completing with shelter data)
5. **Methodology** (mostly empty — needs writing + code blocks)
   - LST pre-processing
   - NDVI / NDBI calculations
   - Demographic vulnerability composite
   - Shelter distance analysis
   - Combined risk index
6. **Interface** (empty — add screenshots once app is built)
7. **The Application** (needs iframe embed of the live GEE app)
8. **How It Works** (code walkthrough section, like Nepal)
9. **Limitations and Opportunities**
10. **References**

---

## 9. Mark Scheme — What Gets You Marks

### Group Application (50% of module)

| Criterion | Weight | What is needed |
|---|---|---|
| **Advanced data analysis methods** | 30% | Correct pre-processing (cloud masking, scale factors applied), appropriate method for LST + vulnerability index, critical reflection on method choices |
| **Quality of interactive UI** | 30% | User-friendly design, all interactive elements must work, results returned quickly (precompute heavy layers!) |
| **Clarity of purpose** | 30% | Clear problem statement, obvious end user, application clearly solves the stated problem |
| **Design and aesthetics** | 10% | Colour palette appropriate (diverging for risk — not just red/green), attention to detail, logical vis choices |

### Group Presentation (20% of module)

| Criterion | Weight |
|---|---|
| Execution: present problem + solution + data/methods | 30% |
| Live demonstration | 30% |
| Technical code walkthrough | 30% |
| Clarity | 10% |

The mark scheme at A+ level requires showing you understand **why** your method choices are the best for the task, and discussing their shortcomings. Build the limitations section seriously.

---

## 10. GitHub Commit Strategy

The assessment guidelines explicitly state:

> *"The number and nature of commits to the GitHub repository should demonstrate that each member of the group has contributed to the technical aspect of the project."*

Each member should pick a category:
- **Pre-processing** — Landsat cloud masking, LST calculation, NDVI/NDBI
- **Analysis** — vulnerability index, shelter distance, combined risk score
- **Visualisation** — GEE UI code, Quarto `index.qmd` write-up, styling

Commit early and often. Each person's commits should be substantial and traceable to their category.

---

## 11. Technical Tasks — Priority Order

### Immediate (now)

- [ ] Fix `_quarto.yml` — switch from `book` to `website` type to match Nepal example structure.
- [ ] Add a `website:` block with `site-url`, `repo-url`, `page-footer` (same as Nepal).
- [ ] Add table of contents (`toc: true`, `toc-depth: 3`) to the format block.
- [ ] Add `casa_logo.png` — the `_quarto.yml` references it but the file is missing from the repo.

### GEE App — Build Order

1. **Set up London boundary** — either upload GADM boundary or use a GEE FeatureCollection asset.
2. **Landsat 8 LST summer composite** — cloud mask, scale factor, Band 10 to Celsius.
3. **Landsat 8 LST winter composite** — same pipeline.
4. **NDVI and NDBI** — from same Landsat composite.
5. **Upload ONS OA census data** — as a GEE FeatureCollection asset with % young and % old fields.
6. **Upload shelter point data** — cool spaces and warm spaces as a FeatureCollection asset.
7. **Build vulnerability composite** — normalise and combine.
8. **Build combined risk map** — identify highest-risk OAs.
9. **Build UI** — control panel, borough selector, toggleable layers, charts.
10. **Pre-compute heavy layers as assets** — export normalised LST and risk rasters as GEE assets so the app loads fast (the Nepal team did this and it made a huge difference to load time).

### Quarto site

- [ ] Write Problem Statement section.
- [ ] Write End User section.
- [ ] Complete Data section (add shelter sources).
- [ ] Add Methodology section with code blocks (same scroll-container style as Nepal).
- [ ] Add interface screenshots once UI is done.
- [ ] Embed GEE app iframe.
- [ ] Add Limitations and References sections.

---

## 12. Key Lessons from the Nepal Example

These are the things that clearly got the Nepal team a high mark — worth replicating:

1. **Precomputed assets** — they exported the susceptibility raster and RF probability raster as named GEE assets and imported them back in the app. This removed expensive compute from the interactive layer. We should do the same for our LST composites.
2. **District-level aggregation script (separate from app)** — they ran a dedicated JS script to pre-aggregate all statistics per district and saved the results as enriched FeatureCollections. We should do this for boroughs/LSOAs.
3. **Two separate views compared** — they showed both a knowledge-based model and an RF model side by side. We have a natural equivalent: summer heat risk vs. winter cold risk, displayed with a draggable split-panel divider.
4. **Statistical validation** — they used a chi-square test and binary confusion matrix to validate their predictions. We should validate our LST classification (e.g. compare our high-risk OAs against known heat-related hospital admissions data or IMD health domain scores).
5. **Full code in `index.qmd`** — every significant code block is reproduced in the write-up with a `scroll-container` div. The marker can read the code without going to GitHub.
6. **Clear limitations section** — they called out static models, lack of dynamic data, no export feature. We should similarly flag the temporal mismatch of census data (2021) vs. current shelter provision.

---

## 13. Open Questions for the Group

1. **Who is doing what?** We need to decide pre-processing / analysis / visualisation splits and ensure commits reflect this.
2. **Which years do we use for Landsat?** Suggest 2017-2023 summer and winter. Do we want a single year or a multi-year mean? A mean is more robust and defensible.
3. **Do we include IMD deprivation data?** It adds a third vulnerability axis. Availability: per LSOA from MHCLG. Can be uploaded as a GEE asset.
4. **Do we define "shelter access" as distance to nearest shelter or as shelters per OA population?** Distance is simpler. Both would be stronger.
5. **What specifically do we show in the borough-level pie chart?** Suggested: % LSOAs in low / medium / high combined risk category.
6. **GEE account for the shared project?** Do we have a shared GEE Cloud Project set up that all team members can access? (Nepal used `projects/ee-testing-casa-25/assets/...`)
7. **Is NDBI needed?** The data table lists it but the project summary does not mention it in the methodology. Decide if it contributes to the final index or if it is exploratory only.

---

## 14. Useful Reference Links

| Resource | Link |
|---|---|
| GEE Landsat 8 C2 L2 | https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2 |
| GEE awesome apps list | https://github.com/philippgaertner/awesome-earth-engine-apps |
| Nepal previous project | https://maheer-maps.github.io/CASA25_Rasternauts/ |
| Warm Welcome spaces | https://www.warmwelcome.uk/find-a-space |
| GLA Cool Spaces | https://apps.london.gov.uk/cool-spaces/ |
| Tree Equity Score (UI reference) | https://uk.treeequityscore.org/map |
| ONS Census 2021 Age data | https://www.ons.gov.uk/... |
| GLA Heat Vulnerability report | https://www.london.gov.uk/sites/default/files/2024-01/24-01-16%20GLA%20Properties%20Vulnerable%20to%20Heat%20Impacts%20in%20London.pdf |
| KCL heat priorities report | https://www.kcl.ac.uk/sfg/assets/londoners-experiences-of-heat-and-priorities-for-action.pdf |
| GEE UI widgets reference (W10) | Course W10_ships.qmd in full course materials folder |
| EFAB Book (GEE textbook) | https://www.eefabook.org/ |
