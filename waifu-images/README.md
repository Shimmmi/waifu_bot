# Waifu Images Repository

This folder contains custom artwork for waifu characters organized by race.

## Structure

```
waifu-images/
└── races/
    ├── angel/      - Angel race images (wings, holy theme)
    ├── demon/      - Demon race images (horns, dark theme)
    ├── vampire/    - Vampire race images (fangs, gothic)
    ├── elf/        - Elf race images (pointed ears)
    ├── human/      - Human race images
    ├── dragon/     - Dragon race images (scales, powerful)
    ├── beast/      - Beast race images (animal features)
    └── fairy/      - Fairy race images (small, magical)
```

## Image Specifications

- **Resolution:** 400x400px to 600x600px (square format)
- **Format:** JPG or PNG
- **File Size:** Keep under 500KB per image
- **Naming:** `race_number.jpg` (e.g., `angel_1.jpg`, `vampire_2.png`)

## How to Add Images

1. Place images in the appropriate race folder
2. Name them sequentially (e.g., `angel_1.jpg`, `angel_2.jpg`)
3. Commit and push:
   ```bash
   git add waifu-images/
   git commit -m "Add new waifu images"
   git push origin main
   ```

4. Update `src/bot/data_tables.py` with the new URLs:
   ```python
   "Angel": [
       "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/angel_1.jpg",
       "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/angel_2.jpg",
   ],
   ```

## Current Status

- [ ] Angel images (0 added)
- [ ] Demon images (0 added)
- [ ] Vampire images (0 added)
- [ ] Elf images (0 added)
- [ ] Human images (0 added)
- [ ] Dragon images (0 added)
- [ ] Beast images (0 added)
- [ ] Fairy images (0 added)

## Notes

- Each race should have at least 3-5 images for variety
- Maintain consistent art style across all images
- Images should be portrait-style with the face clearly visible

