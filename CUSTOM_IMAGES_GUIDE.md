# 🎨 Custom Waifu Images - Complete Guide

## Overview

Your bot now uses a **classification system** that selects images based on:
1. **Race** (Angel, Demon, Vampire, etc.) - **Highest Priority**
2. **Profession** (Warrior, Mage, etc.) - **Medium Priority**
3. **Nationality** (Japanese, Chinese, etc.) - **Lowest Priority**

Example: An **Angel Warrior from Japan** will first try to get an Angel image, then Warrior if no Angel images exist, then Japanese as last resort.

---

## Part 1: Image Specifications

### Technical Requirements
- **Resolution:** 400x400px to 600x600px (square)
- **Format:** JPG, PNG, or WebP
- **File Size:** Keep under 500KB each
- **Aspect Ratio:** 1:1 (square format)

### Quality Guidelines
- ✅ Portrait-style (face visible)
- ✅ Good lighting
- ✅ Centered subject
- ✅ Consistent art style across all images
- ✅ High contrast (works well on various backgrounds)

### Naming Convention
```
race_number.jpg
vampire_1.jpg
vampire_2.jpg
angel_1.png
angel_2.png
demon_1.jpg
```

---

## Part 2: Where to Host Images

### Option 1: GitHub Repository (Recommended ⭐)

**Why:** Free, fast CDN, version control, easy updates

#### Setup Steps:

1. **Create a new repository** (or use existing)
   ```
   Repository name: waifu-images
   Public ✓
   ```

2. **Create folder structure:**
   ```
   waifu-images/
   ├── races/
   │   ├── angel/
   │   │   ├── angel_1.jpg
   │   │   ├── angel_2.jpg
   │   │   └── angel_3.jpg
   │   ├── demon/
   │   ├── vampire/
   │   ├── elf/
   │   ├── dragon/
   │   └── ...
   ├── professions/
   │   ├── warrior/
   │   ├── mage/
   │   └── ...
   └── nationalities/
       ├── japanese/
       ├── chinese/
       └── ...
   ```

3. **Get raw URLs:**
   - Click on image in GitHub
   - Click "Raw" button
   - Copy URL: `https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/angel/angel_1.jpg`

4. **Pro tip:** Use GitHub Desktop or git for batch uploads

### Option 2: ImgBB (Simplest)

**Why:** No account needed, drag & drop

1. Go to https://imgbb.com/
2. Upload images
3. Copy "Direct link"
4. Use immediately

**Cons:** No bulk management, harder to organize

### Option 3: Cloudflare R2 (Advanced)

**Why:** Professional CDN, 10GB free

1. Sign up at https://www.cloudflare.com/
2. Go to R2 → Create bucket
3. Upload images
4. Enable public access
5. Get URLs

---

## Part 3: Organizing Your Images

### Recommended Structure

#### By Race (Most Important!)
Each race should have 3-5 images minimum:

```python
"Angel": [
    "https://your-url.com/races/angel/angel_1.jpg",
    "https://your-url.com/races/angel/angel_2.jpg",
    "https://your-url.com/races/angel/angel_3.jpg",
    "https://your-url.com/races/angel/angel_4.jpg",
],
"Vampire": [
    "https://your-url.com/races/vampire/vampire_1.jpg",
    "https://your-url.com/races/vampire/vampire_2.jpg",
    "https://your-url.com/races/vampire/vampire_3.jpg",
],
"Demon": [
    "https://your-url.com/races/demon/demon_1.jpg",
    "https://your-url.com/races/demon/demon_2.jpg",
],
# ... and so on for all 8 races
```

#### Current Races in Your Bot:
1. **Human** - Normal people
2. **Elf** - Pointed ears, elegant
3. **Demon** - Horns, dark themes
4. **Angel** - Wings, holy aura
5. **Vampire** - Fangs, gothic style
6. **Dragon** - Scales, powerful
7. **Beast** - Animal features
8. **Fairy** - Small, magical

---

## Part 4: Finding Images

### Free Image Sources

#### Anime/Manga Style:
1. **Pinterest** - Search "anime [race] girl"
   - https://www.pinterest.com/
   - Good for discovering art

2. **DeviantArt** - Filter by "Free to use"
   - https://www.deviantart.com/
   - Check license before using

3. **Pixabay** - CC0 License (completely free)
   - https://pixabay.com/
   - Search: "anime fantasy character"

4. **Unsplash** - High quality (but less anime-style)
   - https://unsplash.com/

#### AI-Generated (Custom):
1. **Bing Image Creator** (Free)
   - https://www.bing.com/images/create
   - Prompts: "anime angel girl portrait, white wings, holy aura"

2. **Leonardo.AI** (150 free images/day)
   - https://leonardo.ai/
   - Great for consistent style

3. **Midjourney** (Paid, but best quality)
   - https://www.midjourney.com/

### Example Prompts for AI:
```
Angel: "anime angel girl portrait, white wings, halo, holy aura, soft lighting, elegant dress"
Vampire: "anime vampire girl portrait, red eyes, fangs, gothic dress, dark background"
Demon: "anime demon girl portrait, horns, dark wings, mysterious smile"
Elf: "anime elf girl portrait, pointed ears, forest background, elegant"
```

---

## Part 5: Update Your Bot

### Step 1: Upload Your Images

Upload all images to your chosen hosting service (GitHub recommended).

### Step 2: Update `src/bot/data_tables.py`

Open the file and replace the URLs in `WAIFU_IMAGES_BY_RACE`:

```python
WAIFU_IMAGES_BY_RACE = {
    "Human": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/human/human_1.jpg",
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/human/human_2.jpg",
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/human/human_3.jpg",
    ],
    "Elf": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/elf/elf_1.jpg",
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/elf/elf_2.jpg",
    ],
    "Demon": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/demon/demon_1.jpg",
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/demon/demon_2.jpg",
    ],
    "Angel": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/angel/angel_1.jpg",
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/angel/angel_2.jpg",
    ],
    "Vampire": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/vampire/vampire_1.jpg",
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/vampire/vampire_2.jpg",
    ],
    "Dragon": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/dragon/dragon_1.jpg",
    ],
    "Beast": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/beast/beast_1.jpg",
    ],
    "Fairy": [
        "https://raw.githubusercontent.com/YourUsername/waifu-images/main/races/fairy/fairy_1.jpg",
    ],
}
```

### Step 3: (Optional) Add Profession Images

If you want even more variety:

```python
WAIFU_IMAGES_BY_PROFESSION = {
    "Warrior": [
        "https://your-url.com/professions/warrior/warrior_1.jpg",
        "https://your-url.com/professions/warrior/warrior_2.jpg",
    ],
    "Mage": [
        "https://your-url.com/professions/mage/mage_1.jpg",
    ],
    # ... etc
}
```

### Step 4: Deploy to Render

```bash
git add src/bot/data_tables.py
git commit -m "Update waifu images with custom artwork"
git push origin main
```

Render will automatically redeploy!

---

## Part 6: Update Existing Waifus

After adding your custom images, you can update existing waifus using SQL:

### Option A: Update via Neon SQL Editor

```sql
-- Update Angels
UPDATE waifu 
SET image_url = 'https://your-url.com/races/angel/angel_1.jpg' 
WHERE race = 'Angel' AND (image_url IS NULL OR image_url LIKE '%dicebear%');

-- Update Vampires
UPDATE waifu 
SET image_url = 'https://your-url.com/races/vampire/vampire_1.jpg' 
WHERE race = 'Vampire' AND (image_url IS NULL OR image_url LIKE '%dicebear%');

-- Update Demons
UPDATE waifu 
SET image_url = 'https://your-url.com/races/demon/demon_1.jpg' 
WHERE race = 'Demon' AND (image_url IS NULL OR image_url LIKE '%dicebear%');

-- Repeat for all races...
```

### Option B: Random Assignment per Race

```sql
-- This assigns different images to different waifus of the same race
UPDATE waifu 
SET image_url = CASE 
    WHEN id LIKE '%0' THEN 'https://your-url.com/races/angel/angel_1.jpg'
    WHEN id LIKE '%1' THEN 'https://your-url.com/races/angel/angel_2.jpg'
    WHEN id LIKE '%2' THEN 'https://your-url.com/races/angel/angel_3.jpg'
    ELSE 'https://your-url.com/races/angel/angel_1.jpg'
END
WHERE race = 'Angel';

-- Repeat for each race
```

---

## Part 7: Testing

1. **Local Test:**
   ```bash
   # Summon a new waifu
   python -m pytest tests/ -k test_waifu_generation
   ```

2. **Production Test:**
   - Summon a new waifu of each race
   - Open detailed info
   - Verify correct images appear

3. **Check Logs:**
   - Look for: `🎨 Selected Angel waifu image: https://...`
   - Verify the correct race is being matched

---

## Part 8: Advanced Tips

### Dynamic Loading
If you have MANY images, you can use a CDN with pattern matching:

```python
def get_waifu_image(race: str = None, **kwargs) -> str:
    if race:
        # Generate URL dynamically
        race_lower = race.lower()
        image_num = random.randint(1, 10)  # If you have 10 images per race
        return f"https://your-cdn.com/races/{race_lower}/{race_lower}_{image_num}.jpg"
    return fallback_image
```

### Image Preloading
For better WebApp performance, you can add image preloading:

```html
<!-- In webapp/waifu-card.html -->
<link rel="preload" as="image" href="{{image_url}}">
```

### Lazy Loading
For mobile optimization:

```html
<img src="{{image_url}}" loading="lazy" alt="{{name}}">
```

---

## Summary Checklist

- [ ] Choose hosting service (GitHub recommended)
- [ ] Collect/create 3-5 images per race (8 races = 24-40 images minimum)
- [ ] Upload images to hosting service
- [ ] Update `src/bot/data_tables.py` with your URLs
- [ ] Test locally (optional)
- [ ] Deploy to Render (`git push`)
- [ ] Update existing waifus via SQL (optional)
- [ ] Verify in production bot

---

## Need Help?

**Common Issues:**

1. **Images not loading:** Check if URLs are publicly accessible
2. **Wrong race images:** Verify race names match exactly (case-sensitive)
3. **Slow loading:** Optimize image file sizes (<500KB)

**Image Requirements Summary:**
- 📏 Size: 400-600px square
- 📁 Format: JPG or PNG
- 💾 File size: <500KB
- 🎨 Style: Consistent across all images
- 🔗 Hosting: Publicly accessible URLs

Good luck with your custom images! 🎨✨

