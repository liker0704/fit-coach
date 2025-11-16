# Multi-Language Support (i18n)

## Overview

Internationalization (i18n) support enables the FitCoach desktop application to display content in multiple languages: English, Russian, and Czech.

**Status:** ✅ Completed
**Version:** Added in commit `f722f93`
**Date:** November 8, 2025
**Supported Languages:** EN 🇬🇧 | RU 🇷🇺 | CZ 🇨🇿

---

## Technical Stack

### Libraries

```json
{
  "i18next": "^23.x",
  "react-i18next": "^14.x",
  "i18next-browser-languagedetector": "^7.x"
}
```

**Installation:**
```bash
cd desktop
npm install i18next react-i18next i18next-browser-languagedetector
```

---

## Architecture

### 1. Configuration

#### i18n Config (`desktop/src/i18n/config.ts`)

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslation from './locales/en.json';
import ruTranslation from './locales/ru.json';
import czTranslation from './locales/cz.json';

export const resources = {
  en: { translation: enTranslation },
  ru: { translation: ruTranslation },
  cz: { translation: czTranslation },
} as const;

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false, // React already escapes
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
  });

export default i18n;
```

**Key Features:**
- **Language Detection:** Checks localStorage first, then browser language
- **Persistence:** Saves language preference to localStorage
- **Fallback:** Defaults to English if translation missing
- **Type Safety:** Resources exported as const for TypeScript

### 2. Initialization

#### Main Entry Point (`desktop/src/main.tsx`)

```typescript
import "./i18n/config"; // Initialize i18n before App
```

**Important:** i18n config must be imported **before** App component to ensure translations are loaded synchronously.

---

## Translation Files

### Structure

```
desktop/src/i18n/
├── config.ts           # i18n configuration
└── locales/
    ├── en.json         # English translations
    ├── ru.json         # Russian translations
    └── cz.json         # Czech translations
```

### Translation Keys

**Total Keys:** 150+ translation keys organized into namespaces

#### Namespaces

1. **common** - Buttons, labels, generic terms
2. **auth** - Login, register, logout
3. **nav** - Navigation items
4. **day** - Day tracking sections
5. **meals** - Meal-related terms
6. **exercise** - Exercise tracking
7. **water** - Water intake
8. **sleep** - Sleep tracking
9. **mood** - Mood entries
10. **stats** - Statistics page
11. **profile** - Profile settings
12. **agents** - AI agent labels
13. **validation** - Validation messages
14. **errors** - Error messages

### Sample Translations

#### English (`en.json`)
```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "auth": {
    "login": "Login",
    "logout": "Logout",
    "email": "Email"
  },
  "profile": {
    "personalInfo": "Personal Information",
    "healthGoals": "Health Goals",
    "language": "Language"
  }
}
```

#### Russian (`ru.json`)
```json
{
  "common": {
    "save": "Сохранить",
    "cancel": "Отмена",
    "delete": "Удалить"
  },
  "auth": {
    "login": "Вход",
    "logout": "Выход",
    "email": "Email"
  },
  "profile": {
    "personalInfo": "Личная информация",
    "healthGoals": "Цели здоровья",
    "language": "Язык"
  }
}
```

#### Czech (`cz.json`)
```json
{
  "common": {
    "save": "Uložit",
    "cancel": "Zrušit",
    "delete": "Smazat"
  },
  "auth": {
    "login": "Přihlášení",
    "logout": "Odhlásit",
    "email": "Email"
  },
  "profile": {
    "personalInfo": "Osobní informace",
    "healthGoals": "Zdravotní cíle",
    "language": "Jazyk"
  }
}
```

---

## Usage in Components

### Basic Hook Usage

```typescript
import { useTranslation } from 'react-i18next';

export default function MyComponent() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('profile.personalInfo')}</h1>
      <button>{t('common.save')}</button>
    </div>
  );
}
```

### With Interpolation

```typescript
const { t } = useTranslation();

// Translation: "Welcome, {{name}}!"
<p>{t('welcome', { name: user.name })}</p>
```

### Changing Language Programmatically

```typescript
import { useTranslation } from 'react-i18next';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <select onChange={(e) => changeLanguage(e.target.value)} value={i18n.language}>
      <option value="en">English</option>
      <option value="ru">Русский</option>
      <option value="cz">Čeština</option>
    </select>
  );
}
```

---

## Language Selector Implementation

### ProfilePage Component

**Location:** `desktop/src/pages/settings/ProfilePage.tsx`

#### 1. Import Hook

```typescript
import { useTranslation } from 'react-i18next';

export default function ProfilePage() {
  const { t, i18n } = useTranslation();
  // ...
}
```

#### 2. Initialize State

```typescript
const [formData, setFormData] = useState<FormData>({
  // ... other fields
  language: i18n.language || 'en',  // Line 51
});
```

#### 3. Language Change Handler

```typescript
const handleInputChange = (field: keyof FormData, value: string | number | boolean) => {
  setFormData(prev => ({ ...prev, [field]: value }));

  // Handle language change - Lines 179-186
  if (field === 'language' && typeof value === 'string') {
    i18n.changeLanguage(value);
    toast({
      title: 'Language Changed',
      description: 'Language has been updated successfully',
    });
  }
};
```

#### 4. UI Components

```tsx
{/* Lines 392-408 */}
<div>
  <Label htmlFor="language">{t('profile.language')}</Label>
  <Select
    value={formData.language}
    onValueChange={(value) => handleInputChange('language', value)}
  >
    <SelectTrigger id="language">
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="en">English</SelectItem>
      <SelectItem value="ru">Русский</SelectItem>
      <SelectItem value="cz">Čeština</SelectItem>
    </SelectContent>
  </Select>
  <p className="text-sm text-gray-500 mt-1">Language changes apply instantly</p>
</div>
```

---

## Translated Components

### Currently Translated

**ProfilePage** (Demo implementation):
- ✅ Page title
- ✅ Section headings (Personal Info, Health Goals, App Settings)
- ✅ Labels (Full Name, Theme, Language, Daily Reminder)
- ✅ Buttons (Save, Logout)
- ✅ Loading states

**Example:**
```tsx
// Before
<h1>Profile & Settings</h1>

// After
<h1>{t('profile.personalInfo')}</h1>
```

### To Be Translated

For full i18n coverage, these components should be translated:

- [ ] LoginPage
- [ ] RegisterPage
- [ ] CalendarPage
- [ ] DayView (all 7 tabs)
- [ ] StatisticsPage
- [ ] AI Agent dialogs
- [ ] Toast notifications
- [ ] Error messages

**Template for translating components:**

```typescript
// 1. Import hook
import { useTranslation } from 'react-i18next';

// 2. Get t function
const { t } = useTranslation();

// 3. Replace hardcoded strings
<Button>{t('common.save')}</Button>
<Label>{t('profile.age')}</Label>
<p>{t('errors.loadFailed')}</p>
```

---

## Persistence & Detection

### localStorage Key

```
i18nextLng: "en" | "ru" | "cz"
```

**Stored automatically** when language changes.

### Detection Order

1. **localStorage** - User's previously selected language
2. **Browser navigator** - Browser's preferred language
3. **Fallback** - English (en)

### Example Detection Flow

```
1. User opens app for first time
   → Checks localStorage: empty
   → Checks browser language: "ru-RU"
   → Sets language to "ru"

2. User changes to Czech
   → Saves "cz" to localStorage
   → Future visits: loads "cz" from localStorage
```

---

## Testing

### Manual Testing Checklist

- [ ] Open app → Detects browser language correctly
- [ ] Change language in Settings → UI updates instantly
- [ ] Refresh page → Language persists
- [ ] Clear localStorage → Falls back to browser language
- [ ] Test all 3 languages (EN/RU/CZ)
- [ ] Check special characters (Cyrillic, Czech diacritics)
- [ ] Verify toast notifications are translated
- [ ] Check long text doesn't break UI layout

### Testing Language Switching

```typescript
// In browser console (DevTools)
localStorage.setItem('i18nextLng', 'ru');
location.reload(); // Should show Russian

localStorage.setItem('i18nextLng', 'cz');
location.reload(); // Should show Czech

localStorage.removeItem('i18nextLng');
location.reload(); // Should detect browser language
```

---

## Adding New Languages

### Step 1: Create Translation File

```bash
cd desktop/src/i18n/locales
touch de.json  # German
```

### Step 2: Add Translations

Copy structure from `en.json` and translate all keys:

```json
{
  "common": {
    "save": "Speichern",
    "cancel": "Abbrechen"
  }
}
```

### Step 3: Import in Config

```typescript
// desktop/src/i18n/config.ts
import deTranslation from './locales/de.json';

export const resources = {
  en: { translation: enTranslation },
  ru: { translation: ruTranslation },
  cz: { translation: czTranslation },
  de: { translation: deTranslation },  // Add new language
} as const;
```

### Step 4: Update Language Selector

```tsx
// desktop/src/pages/settings/ProfilePage.tsx
<SelectContent>
  <SelectItem value="en">English</SelectItem>
  <SelectItem value="ru">Русский</SelectItem>
  <SelectItem value="cz">Čeština</SelectItem>
  <SelectItem value="de">Deutsch</SelectItem>  {/* Add option */}
</SelectContent>
```

---

## Best Practices

### 1. Namespace Organization

Group related translations:

```json
{
  "auth": {
    "login": "...",
    "register": "..."
  },
  "errors": {
    "network": "...",
    "validation": "..."
  }
}
```

### 2. Consistent Key Naming

Use descriptive, hierarchical keys:

✅ Good:
```json
"profile.personalInfo"
"auth.loginButton"
"errors.invalidEmail"
```

❌ Bad:
```json
"p1"
"btn_login"
"err01"
```

### 3. Avoid Hardcoded Strings

Always use translation keys:

```typescript
// ❌ Bad
<Button>Save Changes</Button>

// ✅ Good
<Button>{t('common.save')}</Button>
```

### 4. Handle Plurals

```json
{
  "items": "{{count}} item",
  "items_plural": "{{count}} items"
}
```

```typescript
t('items', { count: 1 });  // "1 item"
t('items', { count: 5 });  // "5 items"
```

### 5. Date/Time Formatting

Use locale-aware formatting:

```typescript
import { format } from 'date-fns';
import { ru, cs } from 'date-fns/locale';

const locales = { en: undefined, ru, cz: cs };

format(new Date(), 'PPP', { locale: locales[i18n.language] });
```

---

## Troubleshooting

### Issue: Translations not loading

**Solution:**
1. Check i18n config is imported in `main.tsx`
2. Verify JSON files are in `locales/` folder
3. Check browser console for errors

### Issue: Language not persisting

**Solution:**
1. Check localStorage permissions
2. Verify `i18nextLng` key exists after language change
3. Ensure LanguageDetector is configured correctly

### Issue: Missing translation shows key

**Solution:**
1. Add missing key to all language files
2. Check key path is correct (case-sensitive)
3. Verify fallback language (EN) has the key

### Issue: Special characters broken

**Solution:**
1. Ensure JSON files are UTF-8 encoded
2. Use `\u` escape codes if needed
3. Test with `console.log(t('key'))` to verify

---

## Performance Considerations

### Bundle Size

Each translation file adds to bundle size:
- `en.json`: ~8 KB
- `ru.json`: ~12 KB (Cyrillic characters)
- `cz.json`: ~9 KB

**Total:** ~29 KB uncompressed

### Lazy Loading (Future Enhancement)

For larger apps, consider lazy loading translations:

```typescript
i18n.init({
  backend: {
    loadPath: '/locales/{{lng}}/{{ns}}.json',
  },
  // Load translations on demand
});
```

---

## Related Files

### Configuration
- `desktop/src/i18n/config.ts` - Main i18n setup
- `desktop/src/main.tsx` - Import point

### Translations
- `desktop/src/i18n/locales/en.json` - English
- `desktop/src/i18n/locales/ru.json` - Russian
- `desktop/src/i18n/locales/cz.json` - Czech

### Components
- `desktop/src/pages/settings/ProfilePage.tsx` - Language selector UI

### Dependencies
- `desktop/package.json` - i18n packages

### Git
- **Commit:** `f722f93` - feat: implement multi-language support (i18n) with EN/RU/CZ
- **Branch:** `claude/vision-agent-api-mvp-011CUtnYH1RZ2qCVJzP2ALff`

---

## Future Enhancements

1. **RTL Support** - Add Arabic/Hebrew with right-to-left layout
2. **Dynamic Loading** - Load translations on demand to reduce bundle size
3. **Translation Management** - Use Crowdin or similar service for community translations
4. **Automatic Detection** - Use IP geolocation for better language detection
5. **Number/Date Formatting** - Locale-aware formatting for all numbers and dates
6. **Full Coverage** - Translate all remaining components (login, calendar, charts, etc.)
