# Image Naming Quick Reference 📝

## ✅ **CORRECT Naming Format**

### **Format:**
```
{Profession}_{VariantNumber}.jpeg
```

### **Examples:**
```
✅ Warrior_1.jpeg
✅ Warrior_2.jpeg
✅ Warrior_3.jpeg
✅ Mage_1.jpeg
✅ Mage_2.jpeg
✅ Assassin_1.jpeg
✅ Knight_1.jpeg
✅ Archer_1.jpeg
✅ Healer_1.jpeg
✅ Merchant_1.jpeg
```

---

## ❌ **INCORRECT Formats (Don't Use)**

```
❌ Warrior.jpeg          (Missing variant number)
❌ warrior_1.jpeg        (Wrong case - should be Warrior)
❌ Warrior-1.jpeg        (Hyphen instead of underscore)
❌ Warrior1.jpeg         (No underscore)
```

---

## 📁 **Complete Example**

For an **Angel** with **Japanese** nationality and **Warrior** profession, you need:

```
waifu-images/
└── Angel/
    └── Japanese/
        ├── Warrior_1.jpeg  ✅
        ├── Warrior_2.jpeg  ✅ (optional variant)
        ├── Warrior_3.jpeg  ✅ (optional variant)
        ├── Warrior_4.jpeg  ✅ (optional variant)
        ├── Warrior_5.jpeg  ✅ (optional variant)
        │
        ├── Mage_1.jpeg     ✅
        ├── Mage_2.jpeg     ✅ (optional)
        │
        ├── Assassin_1.jpeg ✅
        ├── Assassin_2.jpeg ✅ (optional)
        │
        ├── Knight_1.jpeg   ✅
        ├── Knight_2.jpeg   ✅ (optional)
        │
        ├── Archer_1.jpeg   ✅
        ├── Archer_2.jpeg   ✅ (optional)
        │
        ├── Healer_1.jpeg   ✅
        ├── Healer_2.jpeg   ✅ (optional)
        │
        ├── Merchant_1.jpeg ✅
        └── Merchant_2.jpeg ✅ (optional)
```

---

## 🎯 **Rules**

### **Mandatory:**
1. Always include `_1` variant (minimum required)
2. Use exact profession name (case-sensitive):
   - ✅ `Warrior` (capital W)
   - ❌ `warrior`, `WARRIOR`, `warrior-1`

### **Optional (But Recommended):**
3. Add up to 10 variants (`_2`, `_3`, `_4`, `_5`, etc.) - easily expandable!
4. More variants = more visual variety
5. To change max variants, edit `MAX_IMAGE_VARIANTS` in `waifu_generator.py`

---

## 🎲 **How It Works**

When generating a waifu:
1. System tries variants 1-10 in **random order**
2. For each variant, checks if the image exists via HTTP request
3. If image exists → uses it immediately ✅
4. If no variants exist → falls back to default images
5. **Result:** Only selects images that actually exist!

**Smart Selection:** The system won't pick `Mage_8.jpeg` if only `Mage_1.jpeg`, `Mage_2.jpeg`, and `Mage_3.jpeg` exist!

**Want more variants?** Just change `MAX_IMAGE_VARIANTS` in the code!

---

## 💡 **Tips**

### **Minimum Coverage:**
Start with just `_1` variants for all professions:
- `Warrior_1.jpeg`
- `Mage_1.jpeg`
- `Assassin_1.jpeg`
- etc.

### **More Variety:**
Add 2-3 variants for your favorite combinations:
- `Warrior_1.jpeg`, `Warrior_2.jpeg`, `Warrior_3.jpeg`

### **Maximum Variety:**
Fill all 10 variants (or more!) for all professions:
- That's 10 × 7 = 70 images per nationality!
- 70 × 12 nationalities = 840 images per race!

---

## 📊 **Quick Count Calculator**

| Variants | Images Per Nationality | Images Per Race | Total (All Races) |
|----------|----------------------|-----------------|-------------------|
| 1        | 7                    | 84              | 672               |
| 2        | 14                   | 168             | 1,344             |
| 3        | 21                   | 252             | 2,016             |
| 4        | 28                   | 336             | 2,688             |
| 5        | 35                   | 420             | 3,360             |
| 10       | 70                   | 840             | 6,720             |
| 20       | 140                  | 1,680           | 13,440            |

---

## ✅ **Final Checklist**

Before committing images, verify:

- [ ] All filenames use underscore `_` not hyphen `-`
- [ ] All start with capital letter (Warrior, not warrior)
- [ ] All end with `.jpeg` (not .jpg or .png)
- [ ] Minimum `_1` variant exists for each profession
- [ ] Folder structure: `Race/Nationality/Profession_X.jpeg`
- [ ] Images are in correct folders
- [ ] All images pushed to GitHub

---

**That's it! Use this format and your images will work perfectly!** 🎨✨
