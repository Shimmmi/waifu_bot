# New Image Structure: Race + Nationality + Profession

## 📊 **Overview**

New hierarchical image system with 3 levels of specificity:
1. **Race** (1st priority) - 8 races
2. **Nationality** (2nd priority) - 12 nationalities  
3. **Profession** (3rd priority) - 7 professions

**Total images needed:** 8 × 12 × 7 = **672 images** (for 1 variant each)

---

## 🗂️ **Folder Structure**

```
waifu-images/
└── {race}/
    └── {nationality}/
        └── {profession}.jpeg
```

### **Example Paths:**
```
waifu-images/Angel/Japanese/Warrior.jpeg
waifu-images/Angel/Japanese/Mage.jpeg
waifu-images/Angel/Japanese/Assassin.jpeg
waifu-images/Angel/Japanese/Knight.jpeg
waifu-images/Angel/Japanese/Archer.jpeg
waifu-images/Angel/Japanese/Healer.jpeg
waifu-images/Angel/Japanese/Merchant.jpeg

waifu-images/Angel/Chinese/Warrior.jpeg
waifu-images/Angel/Chinese/Mage.jpeg
... (and so on)

waifu-images/Demon/Japanese/Warrior.jpeg
waifu-images/Demon/Japanese/Mage.jpeg
... (and so on)
```

---

## 📋 **Complete Structure Breakdown**

### **8 Races:**
1. Human
2. Elf
3. Demon
4. Angel
5. Vampire
6. Dragon
7. Beast
8. Fairy

### **12 Nationalities:**
1. Japanese (JP)
2. Chinese (CN)
3. Korean (KR)
4. American (US)
5. British (GB)
6. French (FR)
7. German (DE)
8. Italian (IT)
9. Russian (RU)
10. Brazilian (BR)
11. Indian (IN)
12. Canadian (CA)

### **7 Professions:**
1. Warrior
2. Mage
3. Assassin
4. Knight
5. Archer
6. Healer
7. Merchant

---

## 🔢 **Image Count Per Category**

| Category | Count | Images Needed |
|----------|-------|---------------|
| Race | 8 | 8 × 84 = 672 |
| Nationality per Race | 12 | 12 × 7 = 84 |
| Profession per Nationality | 7 | 7 × 1 = 7 |
| **TOTAL** | | **672 images** |

---

## 📁 **Complete Folder List**

<details>
<summary>Click to expand full folder structure</summary>

```
waifu-images/
├── Angel/
│   ├── Japanese/
│   │   ├── Warrior.jpeg
│   │   ├── Mage.jpeg
│   │   ├── Assassin.jpeg
│   │   ├── Knight.jpeg
│   │   ├── Archer.jpeg
│   │   ├── Healer.jpeg
│   │   └── Merchant.jpeg
│   ├── Chinese/ (same 7 professions)
│   ├── Korean/ (same 7 professions)
│   ├── American/ (same 7 professions)
│   ├── British/ (same 7 professions)
│   ├── French/ (same 7 professions)
│   ├── German/ (same 7 professions)
│   ├── Italian/ (same 7 professions)
│   ├── Russian/ (same 7 professions)
│   ├── Brazilian/ (same 7 professions)
│   ├── Indian/ (same 7 professions)
│   └── Canadian/ (same 7 professions)
├── Beast/ (12 nationalities × 7 professions)
├── Demon/ (12 nationalities × 7 professions)
├── Dragon/ (12 nationalities × 7 professions)
├── Elf/ (12 nationalities × 7 professions)
├── Fairy/ (12 nationalities × 7 professions)
├── Human/ (12 nationalities × 7 professions)
└── Vampire/ (12 nationalities × 7 professions)
```

</details>

---

## 🎯 **Image Selection Logic**

When generating a waifu:
1. **Race** is selected → determines base folder
2. **Nationality** is selected → determines subfolder
3. **Profession** is selected → determines exact file

**Example:**
- Race: Angel
- Nationality: Japanese  
- Profession: Warrior
- **Image:** `waifu-images/Angel/Japanese/Warrior.jpeg`

---

## 💻 **Implementation Steps**

### **Step 1: Create Folder Structure**

Run this script to create all folders:

```bash
# Will create script: create_image_folders.py
```

### **Step 2: Update `data_tables.py`**

No changes needed! The structure is determined by:
- `RACES` dictionary (8 races)
- `NATIONALITIES` dictionary (12 nationalities)
- `PROFESSIONS` dictionary (7 professions)

### **Step 3: Update `waifu_generator.py`**

Modify `get_waifu_image()` to use new structure:
```python
def get_waifu_image(race, profession, nationality):
    # Build path: waifu-images/{Race}/{Nationality}/{Profession}.jpeg
    image_url = f"https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/{race}/{nationality}/{profession}.jpeg"
    return image_url
```

### **Step 4: Add Images**

1. Generate/collect 672 images
2. Name them according to profession
3. Place in correct race/nationality folders
4. Commit and push to GitHub

---

## 🖼️ **Image Requirements**

### **Format:**
- **.jpeg** or **.jpg** (consistent naming)
- Recommended resolution: **512×512** or **800×800**
- Max file size: **500KB** per image

### **Naming Convention:**
- Exact match with profession names (case-sensitive)
- Examples: `Warrior.jpeg`, `Mage.jpeg`, `Healer.jpeg`

### **Content Guidelines:**
- Match race theme (Angel: wings/halo, Demon: horns, etc.)
- Match nationality theme (Japanese: kimono/samurai, Chinese: traditional attire, etc.)
- Match profession theme (Warrior: armor, Mage: robes, etc.)

---

## 🎨 **Image Generation Tips**

### **Option 1: AI Generation (Recommended)**
Use tools like:
- **Stable Diffusion** (local/free)
- **Midjourney** (paid, high quality)
- **DALL-E** (paid)
- **Leonardo.ai** (free tier available)

### **Sample Prompts:**
```
"Japanese Angel Warrior woman, wings, halo, samurai armor, anime style, detailed"
"Chinese Demon Mage woman, horns, traditional robes, casting spell, anime style"
"Russian Vampire Assassin woman, fangs, dark cloak, stealthy, anime style"
```

### **Option 2: Commission Artists**
- Hire artists on Fiverr/Upwork
- Provide detailed specifications
- Bulk discounts for 672 images

### **Option 3: Mix & Match**
- Start with fewer variations
- Use fallback logic for missing images
- Gradually add more images

---

## 🔄 **Fallback Strategy**

If a specific combination doesn't exist, the system will:
1. Try: `race/nationality/profession.jpeg`
2. Fallback to: `race/nationality/default.jpeg` (if exists)
3. Fallback to: `race/default.jpeg` (if exists)
4. Fallback to: Generic placeholder

---

## 📊 **Phased Implementation**

Don't need all 672 images immediately! Start small:

### **Phase 1: Basic (56 images)**
- 8 races × 7 professions = 56 images
- Use same image for all nationalities initially

### **Phase 2: Popular Combinations (168 images)**
- Focus on most common nationalities (JP, CN, KR, US)
- 8 races × 4 nationalities × 7 professions = 224 images

### **Phase 3: Full Coverage (672 images)**
- All combinations
- Maximum variety

---

## 🚀 **Next Steps**

1. **Create folder structure** (automated script)
2. **Update image selection logic** in code
3. **Start with Phase 1** (basic 56 images)
4. **Gradually expand** to more nationality variants
5. **Test and deploy**

---

**Ready to implement? I'll create the scripts and update the code!** 🎨

