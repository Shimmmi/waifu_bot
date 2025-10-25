# 🎨 Waifu Card Images - Complete Implementation Guide

## 📋 Overview

This guide explains how to add actual images to waifu cards in the WebApp. Currently, cards show a placeholder emoji (🎭). We'll implement a system to display real anime character images.

---

## 🎯 Implementation Options

### Option 1: Free Anime Character APIs (Recommended for Testing)
**Pros:** Free, easy, immediate  
**Cons:** Random images, not custom to your waifus

### Option 2: Custom Image Hosting (Recommended for Production)
**Pros:** Full control, custom images, professional  
**Cons:** Requires image storage service

### Option 3: Hybrid Approach
**Pros:** Start with API, replace with custom later  
**Cons:** Need to update twice

---

## 🚀 Quick Start: Option 1 - Using Free APIs

### Step 1: Choose an API

**Waifu.pics API** (Most Popular)
- URL: `https://api.waifu.pics/sfw/waifu`
- Free, no API key needed
- Returns random anime girl images
- SFW (safe for work) content

**Other Options:**
- `https://api.waifu.im/` - More categories
- `https://nekos.best/api/v2/neko` - Cat girls
- `https://picsum.photos/` - Real photos (not anime)

### Step 2: Update Waifu Model to Store Image URLs

Currently, the `Waifu` model has `image_url` field, but it's always `None`. We need to generate URLs when creating waifus.

**File:** `src/bot/services/waifu_generator.py`

Add this function:

```python
import requests
import logging

logger = logging.getLogger(__name__)

def generate_waifu_image_url(name: str, rarity: str, race: str) -> str:
    """
    Generate image URL for waifu
    
    Options:
    1. Use free API (for testing)
    2. Use predefined URLs (for production)
    3. Return placeholder
    """
    # Option 1: Use free API (random images)
    try:
        # Try to fetch from waifu.pics API
        response = requests.get("https://api.waifu.pics/sfw/waifu", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("url", None)
    except Exception as e:
        logger.warning(f"Failed to fetch waifu image from API: {e}")
    
    # Fallback: Return None (will show placeholder)
    return None
```

### Step 3: Update `generate_waifu()` Function

**File:** `src/bot/services/waifu_generator.py`

Find the `generate_waifu()` function and add image generation:

```python
def generate_waifu(card_number: int, owner_id: int) -> Dict:
    """Генерирует новую вайфу"""
    # ... existing code ...
    
    # Generate image URL
    image_url = generate_waifu_image_url(name, rarity, race)
    
    return {
        "id": waifu_id,
        "card_number": card_number,
        "name": name,
        "rarity": rarity,
        "race": race,
        "profession": profession,
        "nationality": nationality,
        "image_url": image_url,  # ← Now has actual URL
        "owner_id": owner_id,
        # ... rest of the fields ...
    }
```

### Step 4: Update WebApp to Display Images

The WebApp already has code to display images! It's in `webapp/waifu-card.html`:

```html
<div class="card-image-container">
    ${waifu.image_url 
        ? `<img src="${waifu.image_url}" alt="${waifu.name}" class="card-image">`
        : `<div class="card-image-placeholder">🎭</div>`
    }
</div>
```

This means once `image_url` is not null, images will automatically display!

### Step 5: Add Image Error Handling

Update the image HTML to handle loading errors:

**File:** `webapp/waifu-card.html`

```javascript
// Find the renderWaifuCard function and update the image section:

<div class="card-image-container">
    ${waifu.image_url 
        ? `<img 
            src="${waifu.image_url}" 
            alt="${waifu.name}" 
            class="card-image"
            onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
          >
          <div class="card-image-placeholder" style="display:none;">🎭</div>`
        : `<div class="card-image-placeholder">🎭</div>`
    }
</div>
```

### Step 6: Test the Implementation

1. **Deploy changes:**
   ```bash
   git add .
   git commit -m "Feature: Add waifu images using free API"
   git push origin main
   ```

2. **Test:**
   - Summon a new waifu
   - Open WebApp
   - Should see an anime character image instead of 🎭

---

## 🎨 Option 2: Custom Image Hosting (Production)

### Step 1: Choose Image Hosting Service

**Recommended Services:**

1. **Cloudinary** (Easiest)
   - Free tier: 25GB storage, 25GB bandwidth/month
   - Automatic image optimization
   - CDN included
   - URL: https://cloudinary.com

2. **AWS S3 + CloudFront**
   - Most scalable
   - Pay as you go
   - Requires AWS account

3. **ImgBB** (Simplest)
   - Free image hosting
   - Direct links
   - No account needed for basic use

4. **GitHub Repository** (Free for small projects)
   - Create a `waifu-images` repo
   - Upload images
   - Use raw.githubusercontent.com URLs

### Step 2: Set Up Cloudinary (Recommended)

1. **Create Account:**
   - Go to https://cloudinary.com/users/register/free
   - Sign up for free account

2. **Get Credentials:**
   - Dashboard → Settings → Access Keys
   - Note: Cloud Name, API Key, API Secret

3. **Install Cloudinary SDK:**
   ```bash
   pip install cloudinary
   ```

4. **Add to requirements.txt:**
   ```
   cloudinary==1.36.0
   ```

### Step 3: Upload Images to Cloudinary

**Option A: Manual Upload**
1. Go to Cloudinary dashboard
2. Media Library → Upload
3. Create folder: `waifu-images`
4. Upload your images
5. Note the public IDs

**Option B: Programmatic Upload**
```python
import cloudinary
import cloudinary.uploader

# Configure
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET"
)

# Upload image
result = cloudinary.uploader.upload(
    "path/to/image.jpg",
    folder="waifu-images",
    public_id="waifu_name"
)

print(result['secure_url'])
```

### Step 4: Create Image Mapping System

**File:** `src/bot/data_tables.py`

```python
# Waifu image mapping
WAIFU_IMAGES = {
    # Format: "name": "cloudinary_public_id" or "full_url"
    "Sakura": "waifu-images/sakura_default",
    "Miku": "waifu-images/miku_default",
    "Asuna": "waifu-images/asuna_default",
    # Add more mappings...
}

# Alternative: Map by race/profession
RACE_IMAGES = {
    "Human": [
        "waifu-images/human_1",
        "waifu-images/human_2",
        "waifu-images/human_3",
    ],
    "Elf": [
        "waifu-images/elf_1",
        "waifu-images/elf_2",
    ],
    "Angel": [
        "waifu-images/angel_1",
        "waifu-images/angel_2",
    ],
    # Add more...
}

def get_cloudinary_url(public_id: str, width: int = 400, quality: str = "auto") -> str:
    """Generate optimized Cloudinary URL"""
    cloud_name = "YOUR_CLOUD_NAME"
    return f"https://res.cloudinary.com/{cloud_name}/image/upload/w_{width},q_{quality}/{public_id}.jpg"
```

### Step 5: Update Waifu Generator

**File:** `src/bot/services/waifu_generator.py`

```python
from bot.data_tables import WAIFU_IMAGES, RACE_IMAGES, get_cloudinary_url
import random

def generate_waifu_image_url(name: str, rarity: str, race: str) -> str:
    """
    Generate image URL for waifu
    Priority:
    1. Specific name mapping
    2. Random from race pool
    3. Generic placeholder
    """
    # Try to find specific image for this name
    if name in WAIFU_IMAGES:
        public_id = WAIFU_IMAGES[name]
        return get_cloudinary_url(public_id)
    
    # Try to find image for this race
    if race in RACE_IMAGES and RACE_IMAGES[race]:
        public_id = random.choice(RACE_IMAGES[race])
        return get_cloudinary_url(public_id)
    
    # Fallback: return None (will show placeholder)
    return None
```

### Step 6: Environment Variables for Security

**File:** `.env` (DON'T commit this!)
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**File:** `src/bot/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    cloudinary_cloud_name: str = "demo"
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    class Config:
        env_file = ".env"
```

**Update Render Environment Variables:**
1. Render Dashboard → Your Service → Environment
2. Add:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

---

## 🎨 Option 3: Using GitHub for Free Hosting

### Step 1: Create Image Repository

1. Create new GitHub repo: `waifu-images`
2. Upload images to folders:
   ```
   waifu-images/
   ├── human/
   │   ├── girl_1.jpg
   │   ├── girl_2.jpg
   ├── elf/
   │   ├── elf_1.jpg
   │   ├── elf_2.jpg
   └── angel/
       ├── angel_1.jpg
       └── angel_2.jpg
   ```

### Step 2: Get Raw URLs

GitHub raw URL format:
```
https://raw.githubusercontent.com/USERNAME/waifu-images/main/human/girl_1.jpg
```

### Step 3: Create Mapping

**File:** `src/bot/data_tables.py`

```python
GITHUB_BASE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/waifu-images/main"

WAIFU_IMAGE_PATHS = {
    "Human": [
        f"{GITHUB_BASE_URL}/human/girl_1.jpg",
        f"{GITHUB_BASE_URL}/human/girl_2.jpg",
        f"{GITHUB_BASE_URL}/human/girl_3.jpg",
    ],
    "Elf": [
        f"{GITHUB_BASE_URL}/elf/elf_1.jpg",
        f"{GITHUB_BASE_URL}/elf/elf_2.jpg",
    ],
    # Add more...
}

def get_waifu_image_by_race(race: str) -> str:
    """Get random image for race"""
    images = WAIFU_IMAGE_PATHS.get(race, [])
    return random.choice(images) if images else None
```

---

## 🎨 Styling & Optimization

### Step 1: Update CSS for Better Image Display

**File:** `webapp/waifu-card.html`

Add/update these styles:

```css
.card-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center top; /* Focus on face */
}

/* Add loading animation */
.card-image {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Loading spinner while image loads */
.card-image-container::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.card-image-container.loaded::before {
    display: none;
}

@keyframes spin {
    to { transform: translate(-50%, -50%) rotate(360deg); }
}
```

### Step 2: Add Image Lazy Loading

```javascript
// In renderWaifuCard function:
${waifu.image_url 
    ? `<img 
        src="${waifu.image_url}" 
        alt="${waifu.name}" 
        class="card-image"
        loading="lazy"
        onload="this.parentElement.classList.add('loaded')"
        onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
      >`
    : `<div class="card-image-placeholder">🎭</div>`
}
```

---

## 🧪 Testing Checklist

### Test 1: Image Display
- [ ] New waifus have image URLs
- [ ] WebApp shows images instead of 🎭
- [ ] Images load correctly
- [ ] No broken image icons

### Test 2: Error Handling
- [ ] Invalid URLs show placeholder
- [ ] Slow loading shows spinner
- [ ] Failed loads fall back to 🎭

### Test 3: Performance
- [ ] Images load in < 3 seconds
- [ ] WebApp doesn't freeze while loading
- [ ] Multiple cards load efficiently

### Test 4: Mobile
- [ ] Images display correctly on mobile
- [ ] Images are appropriately sized
- [ ] No layout breaks

---

## 📊 Image Requirements

### Recommended Specifications:
- **Format:** JPG or PNG
- **Size:** 400x600px (portrait)
- **File size:** < 200KB
- **Aspect ratio:** 2:3 (standard character portrait)
- **Quality:** 80-85% (good balance)

### Image Optimization:
```bash
# Using ImageMagick
convert input.jpg -resize 400x600^ -gravity center -extent 400x600 -quality 85 output.jpg

# Using Python (Pillow)
from PIL import Image
img = Image.open('input.jpg')
img = img.resize((400, 600), Image.LANCZOS)
img.save('output.jpg', quality=85, optimize=True)
```

---

## 🚀 Quick Implementation (Fastest Way)

If you want to get started IMMEDIATELY:

### 5-Minute Setup:

1. **Update waifu_generator.py:**
```python
def generate_waifu_image_url(name: str, rarity: str, race: str) -> str:
    """Quick implementation using free API"""
    try:
        import requests
        response = requests.get("https://api.waifu.pics/sfw/waifu", timeout=5)
        if response.status_code == 200:
            return response.json().get("url")
    except:
        pass
    return None
```

2. **Add to generate_waifu():**
```python
image_url = generate_waifu_image_url(name, rarity, race)
```

3. **Deploy:**
```bash
git add .
git commit -m "Add waifu images"
git push origin main
```

4. **Test:**
- Summon new waifu
- Open WebApp
- See anime image! 🎉

---

## 📝 Next Steps

After basic implementation:
1. ✅ Get images working (use free API)
2. 📸 Collect/create custom images
3. ☁️ Set up Cloudinary account
4. 🗂️ Upload images
5. 🔄 Switch from API to custom images
6. 🎨 Optimize and style

---

## 🆘 Troubleshooting

### Images Not Showing
- Check `image_url` in database (should not be NULL)
- Check browser console for errors
- Verify URL is accessible
- Check CORS headers

### Slow Loading
- Use CDN (Cloudinary/CloudFront)
- Optimize image sizes
- Add lazy loading
- Use WebP format

### Broken Images
- Add error handling
- Use fallback placeholder
- Check URL format
- Verify image permissions

---

## 📚 Resources

- **Free Anime Images:** https://api.waifu.pics/
- **Cloudinary Docs:** https://cloudinary.com/documentation
- **Image Optimization:** https://tinypng.com/
- **Free Stock Images:** https://unsplash.com/

---

Would you like me to implement the quick 5-minute version right now? 🚀

