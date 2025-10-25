# 🎨 Quick Start: Adding Your Custom Images

## ✅ Folder Structure Created!

```
waifu-images/
└── races/
    ├── angel/      ← Put angel images here
    ├── demon/      ← Put demon images here
    ├── vampire/    ← Put vampire images here
    ├── elf/        ← Put elf images here
    ├── human/      ← Put human images here
    ├── dragon/     ← Put dragon images here
    ├── beast/      ← Put beast images here
    └── fairy/      ← Put fairy images here
```

## 📋 Step-by-Step Process

### Step 1: Prepare Your Images

For each race, prepare 3-5 images:
- **Resolution:** 400x400px to 600x600px (square)
- **Format:** JPG or PNG
- **File size:** Under 500KB each
- **Naming:** `angel_1.jpg`, `angel_2.jpg`, etc.

### Step 2: Add Images to Folders

Copy your images into the appropriate folders:

**Example for Angels:**
```
waifu-images/races/angel/
├── angel_1.jpg
├── angel_2.jpg
├── angel_3.jpg
├── angel_4.jpg
└── angel_5.jpg
```

**Repeat for all 8 races.**

### Step 3: Commit to GitHub

```bash
# From your project root
git add waifu-images/
git commit -m "Add custom waifu images for [race names]"
git push origin main
```

### Step 4: Get the URLs

Your images will be available at:
```
https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/angel_1.jpg
https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/vampire_1.jpg
```

**Format:**
```
https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/[RACE_FOLDER]/[FILENAME]
```

### Step 5: Update the Bot Code

Open `src/bot/data_tables.py` and replace the URLs:

```python
WAIFU_IMAGES_BY_RACE = {
    "Human": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/human_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/human_2.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/human_3.jpg",
    ],
    "Elf": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/elf_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/elf_2.jpg",
    ],
    "Demon": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/demon_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/demon_2.jpg",
    ],
    "Angel": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/angel_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/angel_2.jpg",
    ],
    "Vampire": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/vampire_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/vampire_2.jpg",
    ],
    "Dragon": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/dragon_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/dragon_2.jpg",
    ],
    "Beast": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/beast_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/beast_2.jpg",
    ],
    "Fairy": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/fairy_1.jpg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/fairy_2.jpg",
    ],
}
```

### Step 6: Deploy

```bash
git add src/bot/data_tables.py
git commit -m "Update waifu images with custom artwork"
git push origin main
```

Render will automatically redeploy! 🚀

---

## 🎯 Quick Checklist

- [ ] Prepare 24-40 images (3-5 per race)
- [ ] Resize images to 400-600px square
- [ ] Optimize file sizes (<500KB each)
- [ ] Copy images to `waifu-images/races/[race_name]/` folders
- [ ] Commit images: `git add waifu-images/` → `git push`
- [ ] Update URLs in `src/bot/data_tables.py`
- [ ] Deploy: `git push`
- [ ] Test by summoning new waifus!

---

## 💡 Tips

### Where to Find Images?

1. **AI Generation** (Recommended):
   - Bing Image Creator (free): https://www.bing.com/images/create
   - Leonardo.AI (150/day free): https://leonardo.ai/
   - Prompts: "anime angel girl portrait, white wings, holy aura"

2. **Free Stock**:
   - Pixabay: https://pixabay.com/
   - Search: "anime fantasy character"

3. **Commission an Artist**:
   - Fiverr: $5-50 per image
   - DeviantArt: Many artists for hire

### Testing URLs

Before updating the bot, test if images load:
1. Push images to GitHub
2. Open URL in browser:
   ```
   https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/angel_1.jpg
   ```
3. If image loads → URL is correct ✅
4. If 404 error → Check filename/path ❌

### Pro Tips

- **Consistent naming**: `angel_1.jpg`, `angel_2.jpg` (not `angel1.jpg`, `Angel_1.JPG`)
- **No spaces**: Use `_` instead of spaces in filenames
- **Lowercase**: Keep folder names lowercase
- **Backup**: Keep original high-res images in a separate backup folder

---

## 🆘 Troubleshooting

**Problem: Images not loading**
- Check if GitHub URL is accessible in browser
- Verify repo is public
- Check filename spelling (case-sensitive!)

**Problem: Wrong race getting wrong images**
- Verify race names match exactly: `"Angel"` not `"angel"`
- Check `src/bot/data_tables.py` for typos

**Problem: Images too slow**
- Resize to 500x500px
- Compress with TinyPNG: https://tinypng.com/
- Target <200KB per image

---

## 📚 Full Documentation

For detailed guides, see:
- `CUSTOM_IMAGES_GUIDE.md` - Complete 621-line guide
- `waifu-images/README.md` - Images folder documentation

---

**You're all set! Start adding your images whenever you're ready! 🎨**

